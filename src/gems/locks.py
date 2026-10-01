"""Content-addressed research locks that work in shallow clones and source archives.

Digests were independently compared with the original preregistration/implementation
commits. They are checked, not refreshed from the current files. Git history remains
linked evidence, but its absence cannot silently disable integrity verification.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

LOCKED_FILES = {
    "research/preregistration-h21.md": "63618210601d87197a9cc88f17c7f70c103a8c224ac7cbde5e559ece312555fa",
    "research/preregistration-h21-s2.md": "e919a3fa18272b3a3162c8d04bb7c3242b6283bb5593e63e538d50ac6ae998bd",
    "research/preregistration-h21-s3.md": "7353bfbdabe48637bdd549722cbefaa70da1bb5ca62f4c1ee80332c23e9145a8",
    "evidence/h21-1-results.json": "ee3a52c471720dd5d6692a9fb849d21979111de2c3ecf57d6130f8dab66c6c67",
    "evidence/h21-5-results.json": "8979d1b93ba33bfb5fd0712198bc5953b97850baac42572b56a1d384a764e75d",
    "evidence/data-verification.json": "e4b27401fac136dcf05effbf202cfb38da140579f3a8eeb6372d812de7de21ef",
}
ORIGINAL_PROMPT_SHA = "3dc7b31b359dd6a0f8f992c75e26f3daf8faa37b69699493a6a17cf358086a02"


def verify_file(root: Path, relative: str) -> bytes:
    expected = LOCKED_FILES[relative]
    content = (Path(root) / relative).read_bytes()
    if hashlib.sha256(content).hexdigest() != expected:
        raise ValueError(f"Immutable research file changed: {relative}")
    return content


def verify_prompt(readme: Path) -> str:
    text = Path(readme).read_text(encoding="utf-8")
    try:
        prompt = text.split("```text\n", 1)[1].split("\n```", 1)[0]
    except IndexError as exc:
        raise ValueError("Full original prompt is missing") from exc
    if hashlib.sha256(prompt.encode("utf-8")).hexdigest() != ORIGINAL_PROMPT_SHA:
        raise ValueError("Full original prompt changed")
    return prompt
