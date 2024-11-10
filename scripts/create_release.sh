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

# Push main branch first
echo "Pushing main branch..."
git push origin main

# Create and push tag
echo "Creating tag $TAG..."
git tag "$TAG"
echo "Pushing tag..."
git push origin "$TAG"

echo "Release $TAG created and pushed successfully!"
echo "GitHub Actions will now build and publish the release."