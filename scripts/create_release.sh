#!/bin/bash

# Exit on error
set -e

# Get version from version.py
VERSION=$(grep -oP 'VERSION = "\K[^"]+' src/version.py)

# Create tag name
TAG="v$VERSION"

# Check if tag exists
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "Error: Tag $TAG already exists"
    exit 1
fi

# Check if working directory is clean
if ! git diff-index --quiet HEAD --; then
    echo "Error: Working directory is not clean. Please commit all changes first."
    exit 1
fi

# Check if we're on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Error: Not on main branch. Please switch to main branch first."
    exit 1
fi

# Create and push tag
echo "Creating tag $TAG..."
git tag -a "$TAG" -m "Release $TAG"
echo "Pushing tag..."
git push origin "$TAG"

echo "Release $TAG created and pushed successfully!"
echo "GitHub Actions will now build and publish the release."