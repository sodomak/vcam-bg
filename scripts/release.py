#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path
from typing import Literal, Optional, Tuple
import re

# Reuse version handling code
VERSION_FILE = Path(__file__).parent.parent / "src" / "version.py"
VERSION_PATTERN = re.compile(r'VERSION = "(\d+)\.(\d+)\.(\d+)"')
VersionPart = Literal["major", "minor", "patch"]

def read_version() -> Tuple[int, int, int]:
    """Read the current version from version.py."""
    content = VERSION_FILE.read_text()
    match = VERSION_PATTERN.search(content)
    if not match:
        raise ValueError("Could not find version string in version.py")
    return tuple(map(int, match.groups()))

def write_version(version: Tuple[int, int, int]) -> None:
    """Write the new version to version.py."""
    version_str = f'VERSION = "{".".join(map(str, version))}"'
    VERSION_FILE.write_text(version_str + "\n")

def bump_version(part: VersionPart) -> str:
    """Bump the version number and return the new version string."""
    major, minor, patch = read_version()
    
    if part == "major":
        new_version = (major + 1, 0, 0)
    elif part == "minor":
        new_version = (major, minor + 1, 0)
    else:  # patch
        new_version = (major, minor, patch + 1)
    
    write_version(new_version)
    return ".".join(map(str, new_version))

def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and handle errors."""
    try:
        return subprocess.run(cmd, check=check, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(cmd)}:")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        raise

def git_is_clean() -> bool:
    """Check if git working directory is clean."""
    result = run_command(["git", "status", "--porcelain"], check=False)
    return not result.stdout.strip()

def create_release(version_part: VersionPart) -> None:
    """Create a new release with version bump."""
    # Check if working directory is clean (this will show any uncommitted changes)
    if not git_is_clean():
        # Instead of erroring, commit all changes
        new_version = bump_version(version_part)
        version_tag = f"v{new_version}"
        
        # Git operations - commit all changes including the version bump
        run_command(["git", "add", "."])  # Add all changes
        run_command(["git", "commit", "-m", f"Release version {new_version}"])
        run_command(["git", "tag", "-a", version_tag, "-m", f"Release {version_tag}"])
        
        # Push changes
        print("\nPushing changes to remote...")
        run_command(["git", "push", "origin", "main"])
        run_command(["git", "push", "origin", version_tag])
        
        print(f"\nSuccessfully created release {version_tag}")
        print("\nGitHub Actions workflow will automatically:")
        print("1. Build the AppImage")
        print("2. Create a GitHub release")
        print("3. Upload the AppImage as a release asset")
    else:
        print("No changes to commit. Please make changes before creating a release.")
        sys.exit(1)

def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Create a new release with version bump")
    parser.add_argument("version_part", choices=["major", "minor", "patch"],
                      help="Which part of the version to bump")
    parser.add_argument("--dry-run", action="store_true",
                      help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    if args.dry_run:
        current = ".".join(map(str, read_version()))
        print(f"Current version: {current}")
        print(f"Would bump {args.version_part} version")
        print("Would create git commit and tag")
        print("Would push to remote")
        return
        
    create_release(args.version_part)

if __name__ == "__main__":
    main() 