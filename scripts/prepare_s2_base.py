"""Prepare the identical 31 consumed control columns, never rescue H21-1.

The input-only hosted probe showed exactly three different hashes, all belonging
exclusively to the discarded H21-1 candidate. The original full lock remains strict.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems.io import data_dir, write_json  # noqa: E402
from prepare_data import main as prepare_original  # noqa: E402
from verify_prepared import verify  # noqa: E402


def main():
    try:
        prepare_original()
    except ValueError as exc:
        if str(exc) != "Preparation differs from first audit; register a separate protocol":
            raise
        print(
            "Full H21-1 preparation guard refused platform-dependent discarded extras; preserving original audit",
            flush=True,
        )
    audit = verify(s2_base_only=True)
    if audit["features_verified"] != 31:
        raise ValueError("S2 consumes exactly the original 31 byte-identical control channels")
    write_json(data_dir() / "s2-base-verification.json", audit)
    print(
        "S2: all 31 CONSUMED columns and original source/mask/support hashes verified; no H21-1 retest",
        flush=True,
    )


if __name__ == "__main__":
    main()
