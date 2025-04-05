#!/bin/bash

# Exit on error
set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Download and compile Python 3.11
PYTHON_VERSION="3.11.8"
if [ ! -d "$SCRIPT_DIR/Python-$PYTHON_VERSION" ]; then
    wget "https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz"
    tar xzf "Python-$PYTHON_VERSION.tgz"
    cd "Python-$PYTHON_VERSION"
    ./configure --prefix="$SCRIPT_DIR/AppDir/usr" --enable-shared --with-system-ffi \
        --enable-optimizations \
        --with-ensurepip=install \
        --with-system-expat \
        --enable-loadable-sqlite-extensions \
        --with-tcltk-includes=/usr/include/tcl \
        --with-tcltk-libs=/usr/lib/x86_64-linux-gnu
    make -j$(nproc)
    make install
    cd ..
    rm -f "Python-$PYTHON_VERSION.tgz"
fi

# Use the compiled Python
PYTHON_EXEC="$SCRIPT_DIR/AppDir/usr/bin/python3"
export LD_LIBRARY_PATH="$SCRIPT_DIR/AppDir/usr/lib:$LD_LIBRARY_PATH"

# Create and activate virtual environment using the compiled Python
rm -rf "$SCRIPT_DIR/venv"  # Clean up any existing venv
"$PYTHON_EXEC" -m venv --clear "$SCRIPT_DIR/venv"
source "$SCRIPT_DIR/venv/bin/activate"

# Verify we're using the correct Python version in the virtual environment
VENV_PYTHON_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [ "$VENV_PYTHON_VERSION" != "${PYTHON_VERSION%.*}" ]; then
    echo "Error: Virtual environment Python version ($VENV_PYTHON_VERSION) doesn't match expected version ($PYTHON_VERSION)"
    deactivate
    rm -rf "$SCRIPT_DIR/venv"
    exit 1
fi

# Upgrade pip first
"$SCRIPT_DIR/venv/bin/python" -m pip install --upgrade pip

# Install dependencies in virtual environment with specific versions
"$SCRIPT_DIR/venv/bin/python" -m pip install \
    opencv-python-headless==4.8.1.78 \
    mediapipe==0.10.9 \
    numpy==1.24.3 \
    pillow==10.2.0

# Create AppDir structure
mkdir -p "$SCRIPT_DIR/AppDir/usr/bin"
mkdir -p "$SCRIPT_DIR/AppDir/usr/lib/python${PYTHON_VERSION%.*}/site-packages"
mkdir -p "$SCRIPT_DIR/AppDir/usr/share/applications"
mkdir -p "$SCRIPT_DIR/AppDir/usr/share/icons/hicolor/256x256/apps"

# Copy virtual environment packages to AppDir
cp -r "$SCRIPT_DIR/venv/lib/python${PYTHON_VERSION%.*}/site-packages"/* "$SCRIPT_DIR/AppDir/usr/lib/python${PYTHON_VERSION%.*}/site-packages/"

# Copy application files
cp -r "$PROJECT_DIR/src" "$SCRIPT_DIR/AppDir/usr/lib/python${PYTHON_VERSION%.*}/site-packages/"

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
export PYTHONPATH="\$HERE/usr/lib/python3.11/site-packages:\$PYTHONPATH"
export LD_LIBRARY_PATH="\$HERE/usr/lib:\$LD_LIBRARY_PATH"
export PYTHONHOME="\$HERE/usr"

# Execute the application using bundled Python
exec "\$HERE/usr/bin/python3" "\$HERE/usr/lib/python3.11/site-packages/src/main.py" "\$@"
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

# Function to copy binary and its dependencies
copy_binary_and_deps() {
    local binary="$1"
    local target_dir="$2"
    
    # Copy the binary itself
    cp -L "$binary" "$target_dir/"
    
    # Get list of dependencies and copy them if not already present
    ldd "$binary" | grep "=> /" | awk '{print $3}' | while read lib; do
        if [ ! -f "$SCRIPT_DIR/AppDir/usr/lib/$(basename "$lib")" ]; then
            cp -L "$lib" "$SCRIPT_DIR/AppDir/usr/lib/"
        fi
    done
}

# Create lib directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/AppDir/usr/lib"

# Copy Tcl/Tk libraries
cp -L /usr/lib/x86_64-linux-gnu/libtk* "$SCRIPT_DIR/AppDir/usr/lib/"
cp -L /usr/lib/x86_64-linux-gnu/libtcl* "$SCRIPT_DIR/AppDir/usr/lib/"
cp -r /usr/lib/x86_64-linux-gnu/tcl* "$SCRIPT_DIR/AppDir/usr/lib/"
cp -r /usr/lib/x86_64-linux-gnu/tk* "$SCRIPT_DIR/AppDir/usr/lib/"

# Copy binaries and their dependencies
copy_binary_and_deps "$(which v4l2-ctl)" "$SCRIPT_DIR/AppDir/usr/bin"
copy_binary_and_deps "$(which ffmpeg)" "$SCRIPT_DIR/AppDir/usr/bin"
copy_binary_and_deps "$(which ffprobe)" "$SCRIPT_DIR/AppDir/usr/bin"

# Create AppImage
export ARCH=x86_64
"$SCRIPT_DIR/appimagetool-x86_64.AppImage" "$SCRIPT_DIR/AppDir" "vcam-bg-x86_64.AppImage"

echo "AppImage created: vcam-bg-x86_64.AppImage"

# Deactivate virtual environment
deactivate

# Clean up
rm -rf "$SCRIPT_DIR/venv"