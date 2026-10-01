"""Bounded, safe official archive extraction. Data remains outside Git; no execution."""

from __future__ import annotations

from pathlib import Path, PurePosixPath, PureWindowsPath
import stat
import zipfile


def safe_members(members, max_bytes=900_000_000, max_files=8000):
    """Validate names, types and expansion limits BEFORE extraction."""
    if not members or len(members) > max_files:
        raise ValueError("Empty/over-limit archive member count")
    seen, total = set(), 0
    for member in members:
        name, size, special = member["name"], member["bytes"], member["special"]
        posix, windows = PurePosixPath(name), PureWindowsPath(name)
        if (
            not name
            or "\\" in name
            or "\x00" in name
            or "\n" in name
            or "\r" in name
            or posix.is_absolute()
            or windows.drive
            or ".." in posix.parts
            or ":" in name
            or special
            or not isinstance(size, int)
            or size < 0
        ):
            raise ValueError("Unsafe archive member name/type/size")
        normalized = str(posix).casefold()
        if normalized in seen:
            raise ValueError("Duplicate/case-colliding archive member")
        seen.add(normalized)
        total += size
        if total > max_bytes:
            raise ValueError("Archive uncompressed byte limit exceeded")
    return total


def unpack(path: Path, dest: Path):
    """Extract only to a new/empty private directory, with CRC and path/type checks."""
    path, dest = Path(path), Path(dest)
    if dest.exists() and any(dest.iterdir()):
        raise ValueError("Refuse extraction into a nonempty destination")
    dest.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            members = []
            for info in archive.infolist():
                mode = info.external_attr >> 16
                kind = stat.S_IFMT(mode)
                members.append(
                    {
                        "name": info.filename,
                        "bytes": info.file_size,
                        "special": bool(info.flag_bits & 1) or kind not in (0, stat.S_IFREG, stat.S_IFDIR),
                    }
                )
            total = safe_members(members)
            if archive.testzip() is not None:
                raise ValueError("Official ZIP CRC failure")
            archive.extractall(dest)
    elif path.suffix.lower() == ".7z":
        import py7zr  # optional requirements-research.txt; never needed for site TIFF downloads

        with py7zr.SevenZipFile(path) as archive:
            if archive.needs_password():
                raise ValueError("Encrypted research archives are unsupported")
            members = [
                {
                    "name": info.filename,
                    "bytes": int(info.uncompressed),
                    "special": info.is_symlink
                    or info.is_junction
                    or info.is_socket
                    or (info.posix_mode is not None and info.st_fmt not in (stat.S_IFREG, stat.S_IFDIR, 0)),
                }
                for info in archive.files
            ]
            total = safe_members(members)
            if archive.testzip() is not None:
                raise ValueError("Official 7z CRC failure")
            archive.reset()
            archive.extractall(dest)
    else:
        raise ValueError("Expected official .zip or .7z archive")
    root = dest.resolve()
    files = []
    for p in dest.rglob("*"):
        if p.is_symlink() or not p.resolve().is_relative_to(root) or (not p.is_file() and not p.is_dir()):
            raise ValueError("Extraction produced an unsafe file")
        if p.is_file():
            files.append(p)
    if sum(p.stat().st_size for p in files) != total:
        raise ValueError("Extracted size does not match checked member inventory")
    return {"members": members, "uncompressed_bytes": total, "crc_verified": True}
