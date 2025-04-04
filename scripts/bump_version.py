#!/usr/bin/env python3
import re
import sys
from pathlib import Path
from typing import Literal, Optional

VERSION_FILE = Path(__file__).parent.parent / "src" / "version.py"
VERSION_PATTERN = re.compile(r'VERSION = "(\d+)\.(\d+)\.(\d+)"')

VersionPart = Literal["major", "minor", "patch"]

def read_version() -> tuple[int, int, int]:
    """Read the current version from version.py."""
    content = VERSION_FILE.read_text()
    match = VERSION_PATTERN.search(content)
    if not match:
        raise ValueError("Could not find version string in version.py")
    return tuple(map(int, match.groups()))

def write_version(version: tuple[int, int, int]) -> None:
    """Write the new version to version.py."""
    version_str = f'VERSION = "{".".join(map(str, version))}"'
    VERSION_FILE.write_text(version_str + "\n")

def bump_version(part: VersionPart) -> None:
    """Bump the version number."""
    major, minor, patch = read_version()
    
    if part == "major":
        new_version = (major + 1, 0, 0)
    elif part == "minor":
        new_version = (major, minor + 1, 0)
    else:  # patch
        new_version = (major, minor, patch + 1)
    
    write_version(new_version)
    print(f"Version bumped to {'.'.join(map(str, new_version))}")

def main() -> None:
    """Main entry point."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("major", "minor", "patch"):
        print("Usage: bump_version.py <major|minor|patch>")
        sys.exit(1)
    
    bump_version(sys.argv[1])

if __name__ == "__main__":
    main()
