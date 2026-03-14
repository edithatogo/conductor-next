import sys
from pathlib import Path
import argparse


ROOT = Path(__file__).resolve().parents[1]
CORE_SRC = ROOT / "conductor-core" / "src"

if str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))

from conductor_core.validation import ValidationService


GEMINI_MAPPINGS = {
    "commands/conductor/conductor.toml": "conductor.j2",
    "commands/conductor/setup.toml": "setup.j2",
    "commands/conductor/newTrack.toml": "new_track.j2",
    "commands/conductor/implement.toml": "implement.j2",
    "commands/conductor/status.toml": "status.j2",
    "commands/conductor/revert.toml": "revert.j2",
}

COMMAND_MAPPINGS = {
    "commands/conductor-info.md": "conductor.j2",
    "commands/conductor-setup.md": "setup.j2",
    "commands/conductor-newtrack.md": "new_track.j2",
    "commands/conductor-implement.md": "implement.j2",
    "commands/conductor-status.md": "status.j2",
    "commands/conductor-revert.md": "revert.j2",
}

CLAUDE_MAPPINGS = {
    ".claude/commands/conductor-setup.md": "setup.j2",
    ".claude/commands/conductor-newtrack.md": "new_track.j2",
    ".claude/commands/conductor-implement.md": "implement.j2",
    ".claude/commands/conductor-status.md": "status.j2",
    ".claude/commands/conductor-revert.md": "revert.j2",
}


def _validate_mapping(
    service: ValidationService,
    mapping: dict[str, str],
    validator: str,
) -> list[str]:
    failures: list[str] = []

    for rel_path, template in mapping.items():
        path = ROOT / rel_path
        if validator == "toml":
            valid, msg = service.validate_gemini_toml(path, template)
        else:
            valid, msg = service.validate_claude_md(path, template)

        status = "OK" if valid else "ERROR"
        print(f"[{status}] {rel_path} -> {template}: {msg}")
        if not valid:
            failures.append(f"{rel_path}: {msg}")

    return failures


def _sync_mapping(
    service: ValidationService,
    mapping: dict[str, str],
    validator: str,
) -> None:
    for rel_path, template in mapping.items():
        path = ROOT / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if validator == "toml":
            success, msg = service.synchronize_gemini_toml(path, template)
        else:
            success, msg = service.synchronize_claude_md(path, template)

        status = "OK" if success else "ERROR"
        print(f"[{status}] synced {rel_path} <- {template}: {msg}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", action="store_true", help="Synchronize conductor assets from templates")
    args = parser.parse_args()

    templates_dir = ROOT / "conductor-core" / "src" / "conductor_core" / "templates"
    service = ValidationService(templates_dir)

    if args.sync:
        _sync_mapping(service, GEMINI_MAPPINGS, "toml")
        _sync_mapping(service, COMMAND_MAPPINGS, "md")
        _sync_mapping(service, CLAUDE_MAPPINGS, "md")
        print("\n[OK] Conductor assets synchronized from templates.")
        return 0

    failures: list[str] = []
    failures.extend(_validate_mapping(service, GEMINI_MAPPINGS, "toml"))
    failures.extend(_validate_mapping(service, COMMAND_MAPPINGS, "md"))
    failures.extend(_validate_mapping(service, CLAUDE_MAPPINGS, "md"))

    if failures:
        print("\nConductor asset validation failed:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("\n[OK] Conductor command and template assets are structurally valid and synchronized.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
