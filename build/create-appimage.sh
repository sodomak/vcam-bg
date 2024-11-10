#!/bin/bash

# Exit on error
set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Detect Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Using Python version: $PYTHON_VERSION"

# Create and activate virtual environment
python -m venv "$SCRIPT_DIR/venv"
source "$SCRIPT_DIR/venv/bin/activate"

# Install dependencies in virtual environment
pip install \
    opencv-python-headless \
    mediapipe \
    numpy \
    pillow

# Create AppDir structure
mkdir -p "$SCRIPT_DIR/AppDir/usr/bin"
mkdir -p "$SCRIPT_DIR/AppDir/usr/lib/python$PYTHON_VERSION/site-packages"
mkdir -p "$SCRIPT_DIR/AppDir/usr/share/applications"
mkdir -p "$SCRIPT_DIR/AppDir/usr/share/icons/hicolor/256x256/apps"

# Copy virtual environment packages to AppDir
cp -r "$SCRIPT_DIR/venv/lib/python$PYTHON_VERSION/site-packages"/* "$SCRIPT_DIR/AppDir/usr/lib/python$PYTHON_VERSION/site-packages/"

# Copy application files
cp -r "$PROJECT_DIR/src" "$SCRIPT_DIR/AppDir/usr/lib/python$PYTHON_VERSION/site-packages/"

# Create launcher script
cat > "$SCRIPT_DIR/AppDir/usr/bin/vcam-bg" << EOF
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PYTHONPATH="$HERE/../lib/python$PYTHON_VERSION/site-packages:$PYTHONPATH"
exec python3 "$HERE/../lib/python$PYTHON_VERSION/site-packages/src/main.py" "$@"
EOF

chmod +x "$SCRIPT_DIR/AppDir/usr/bin/vcam-bg"

# Get version from version.py
VERSION=$(grep -oP 'VERSION = "\K[^"]+' "${SCRIPT_DIR}/../src/version.py")

# Create desktop entry with correct categories
cat > "$SCRIPT_DIR/AppDir/vcam-bg.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Virtual Camera Background
GenericName=Virtual Camera Background
Comment=Virtual background for any video conferencing app
Exec=vcam-bg
Icon=vcam-bg
Terminal=false
Categories=AudioVideo;Video;
Keywords=camera;background;virtual;video;conference;meeting;blur;
StartupNotify=true
X-AppImage-Version=${VERSION}
X-AppImage-BuildDate=$(date -u +%Y-%m-%d)
X-AppImage-Arch=x86_64
X-AppImage-Name=Virtual Camera Background
X-AppImage-Description=Virtual background for any video conferencing app
X-AppImage-URL=https://github.com/sodomak/vcam-bg
X-AppImage-License=MIT
X-AppImage-Author=sodomak
EOF

# Remove all old metadata files
rm -f "$SCRIPT_DIR/AppDir/usr/share/metainfo/vcam-bg.appdata.xml"
rm -f "$SCRIPT_DIR/AppDir/usr/share/metainfo/io.github.sodomak.vcam-bg.appdata.xml"

# Create AppStream metadata with fixes
mkdir -p "$SCRIPT_DIR/AppDir/usr/share/metainfo"
cat > "$SCRIPT_DIR/AppDir/usr/share/metainfo/io.github.sodomak.vcam-bg.metainfo.xml" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>io.github.sodomak.vcam-bg</id>
  <metadata_license>MIT</metadata_license>
  <project_license>MIT</project_license>
  <name>Virtual Camera Background</name>
  <summary>Virtual background for any video conferencing app</summary>
  <description>
    <p>
      A simple Linux application that enables custom backgrounds in any video call, regardless of native support in the conferencing app.
      Compatible with Signal Desktop, Zoom, Teams, Meet, and all other video chat software.
    </p>
    <p>Features:</p>
    <ul>
      <li>Real-time background replacement using MediaPipe</li>
      <li>Multiple camera support with MJPG format</li>
      <li>Adjustable FPS and resolution scaling</li>
      <li>Edge smoothing with Gaussian blur</li>
      <li>Light/Dark theme</li>
      <li>Multi-language support (English, Čeština)</li>
    </ul>
  </description>
  <launchable type="desktop-id">vcam-bg.desktop</launchable>
  <url type="homepage">https://github.com/sodomak/vcam-bg</url>
  <provides>
    <binary>vcam-bg</binary>
  </provides>
  <developer id="io.github.sodomak">
    <name>sodomak</name>
    <url>https://github.com/sodomak</url>
  </developer>
  <releases>
    <release version="${VERSION}" date="$(date -I)"/>
  </releases>
  <content_rating type="oars-1.1">
    <content_attribute id="social-info">mild</content_attribute>
  </content_rating>
  <categories>
    <category>AudioVideo</category>
    <category>Video</category>
  </categories>
</component>
EOF

# Also copy desktop file to applications directory
cp "$SCRIPT_DIR/AppDir/vcam-bg.desktop" "$SCRIPT_DIR/AppDir/usr/share/applications/"

# Create AppRun script
cat > "$SCRIPT_DIR/AppDir/AppRun" << EOF
#!/bin/bash
SELF=\$(readlink -f "\$0")
HERE=\${SELF%/*}

# Set environment variables
export PATH="\$HERE/usr/bin:\$PATH"
export PYTHONPATH="\$HERE/usr/lib/python$PYTHON_VERSION/site-packages:\$PYTHONPATH"
export LD_LIBRARY_PATH="\$HERE/usr/lib:\$LD_LIBRARY_PATH"

# Execute the application directly using Python
exec python3 "\$HERE/usr/lib/python$PYTHON_VERSION/site-packages/src/main.py" "\$@"
EOF

chmod +x "$SCRIPT_DIR/AppDir/AppRun"

# Generate icons in multiple sizes using magick instead of convert
for size in 16 32 48 64 128 256 512; do
    mkdir -p "$SCRIPT_DIR/AppDir/usr/share/icons/hicolor/${size}x${size}/apps"
    magick "$PROJECT_DIR/app.png" -resize ${size}x${size} \
        "$SCRIPT_DIR/AppDir/usr/share/icons/hicolor/${size}x${size}/apps/vcam-bg.png"
done

# Copy largest icon to AppDir root
cp "$SCRIPT_DIR/AppDir/usr/share/icons/hicolor/512x512/apps/vcam-bg.png" "$SCRIPT_DIR/AppDir/"

# Download AppImage builder if not present
if [ ! -f "$SCRIPT_DIR/appimagetool-x86_64.AppImage" ]; then
    wget -O "$SCRIPT_DIR/appimagetool-x86_64.AppImage" \
        "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x "$SCRIPT_DIR/appimagetool-x86_64.AppImage"
fi

# Create AppImage
export ARCH=x86_64
"$SCRIPT_DIR/appimagetool-x86_64.AppImage" "$SCRIPT_DIR/AppDir" "vcam-bg-x86_64.AppImage"

echo "AppImage created: vcam-bg-x86_64.AppImage"

# Deactivate virtual environment
deactivate

# Clean up
rm -rf "$SCRIPT_DIR/venv"