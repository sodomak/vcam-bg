#!/bin/bash

# Get version from version.py
VERSION=$(grep -oP 'VERSION = "\K[^"]+' src/version.py)

# Create tag name
TAG="v$VERSION"

# Check if tag exists
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "Error: Tag $TAG already exists"
    exit 1
fi

# Create and push tag
git tag "$TAG"
git push origin "$TAG"

echo "Release $TAG created and pushed successfully!"
echo "GitHub Actions will now build and publish the release." 