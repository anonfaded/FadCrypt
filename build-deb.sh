#!/bin/bash
set -e

# Build script for FadCrypt Linux .deb package

echo "=== Building FadCrypt for Linux ==="

# Extract version from version.py
VERSION=$(python3 -c "from version import __version__; print(__version__)")
PACKAGE_NAME=$(python3 -c "from version import PACKAGE_NAME; print(PACKAGE_NAME)")
MAINTAINER=$(python3 -c "from version import MAINTAINER_FULL; print(MAINTAINER_FULL)")
DESCRIPTION=$(python3 -c "from version import PACKAGE_DESCRIPTION; print(PACKAGE_DESCRIPTION)")

# Strip 'v' prefix from version for Debian package (Debian versions must start with a digit)
DEB_VERSION="${VERSION#v}"

echo "Building version: $VERSION (Debian: $DEB_VERSION)"

# Check dependencies
echo "Checking dependencies..."
command -v python3 >/dev/null 2>&1 || { echo "Error: python3 not found"; exit 1; }
command -v pyinstaller >/dev/null 2>&1 || { echo "Error: pyinstaller not found. Install with: pip install pyinstaller"; exit 1; }

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist fadcrypt-deb

# Build GUI executable with PyInstaller (console=False)
echo "Building GUI executable with PyInstaller..."
pyinstaller --clean FadCrypt_Linux.spec

# Check if GUI build succeeded
if [ ! -f "dist/fadcrypt" ]; then
    echo "Error: GUI build failed - executable not found"
    exit 1
fi

# Build CLI executable with PyInstaller (console=True)
echo "Building CLI executable with PyInstaller..."
pyinstaller --clean FadCrypt_Linux_CLI.spec

# Check if CLI build succeeded
if [ ! -f "dist/fadcrypt-cli" ]; then
    echo "Error: CLI build failed - executable not found"
    exit 1
fi

# Create .deb package structure
echo "Creating .deb package structure..."
mkdir -p fadcrypt-deb/DEBIAN
mkdir -p fadcrypt-deb/usr/bin
mkdir -p fadcrypt-deb/usr/share/applications
mkdir -p fadcrypt-deb/usr/share/pixmaps
mkdir -p fadcrypt-deb/usr/share/doc/fadcrypt
mkdir -p fadcrypt-deb/etc/systemd/system
mkdir -p fadcrypt-deb/usr/share/fadcrypt

# Copy files
echo "Copying files..."
cp dist/fadcrypt fadcrypt-deb/usr/bin/
cp dist/fadcrypt-cli fadcrypt-deb/usr/bin/
cp debian/fadcrypt.desktop fadcrypt-deb/usr/share/applications/
cp debian/fadcrypt-cli.desktop fadcrypt-deb/usr/share/applications/
cp img/1.png fadcrypt-deb/usr/share/pixmaps/fadcrypt.png
cp img/fadcrypt_cli.png fadcrypt-deb/usr/share/pixmaps/fadcrypt_cli.png
cp LICENSE fadcrypt-deb/usr/share/doc/fadcrypt/
cp README.md fadcrypt-deb/usr/share/doc/fadcrypt/

# Copy elevated daemon service and scripts
echo "Installing elevated daemon service..."
cp etc/systemd/system/fadcrypt-elevated.service fadcrypt-deb/etc/systemd/system/
chmod 644 fadcrypt-deb/etc/systemd/system/fadcrypt-elevated.service

# Copy elevated daemon implementation to /usr/share/fadcrypt/
cp core/linux/elevated_daemon.py fadcrypt-deb/usr/share/fadcrypt/elevated-daemon.py
chmod 755 fadcrypt-deb/usr/share/fadcrypt/elevated-daemon.py

# Copy prerm script for cleanup on uninstall
if [ -f debian/prerm ]; then
    cp debian/prerm fadcrypt-deb/DEBIAN/
    chmod 755 fadcrypt-deb/DEBIAN/prerm
    echo "Added prerm script for automatic cleanup on uninstall"
fi

# Copy postinst script for daemon setup
if [ -f debian/postinst ]; then
    cp debian/postinst fadcrypt-deb/DEBIAN/
    chmod 755 fadcrypt-deb/DEBIAN/postinst
    echo "Added postinst script for daemon service setup"
fi

# Set permissions
chmod 755 fadcrypt-deb/usr/bin/fadcrypt
chmod 755 fadcrypt-deb/usr/bin/fadcrypt-cli
chmod 644 fadcrypt-deb/usr/share/applications/fadcrypt.desktop
chmod 644 fadcrypt-deb/usr/share/applications/fadcrypt-cli.desktop

# Create control file with dynamic size
INSTALLED_SIZE=$(du -sk fadcrypt-deb/usr | cut -f1)
cat > fadcrypt-deb/DEBIAN/control << EOF
Package: ${PACKAGE_NAME}
Version: ${DEB_VERSION}
Section: utils
Priority: optional
Architecture: amd64
Installed-Size: ${INSTALLED_SIZE}
Depends: python3 (>= 3.8), libgtk-3-0
Maintainer: ${MAINTAINER}
Description: ${DESCRIPTION}
 FadCrypt is a cross-platform GUI application that helps you lock and
 monitor applications with password protection and encrypted configuration.
 .
 Features include:
  - Lock/unlock specific applications
  - Password-protected monitoring
  - System tray integration
  - Auto-start on login support
  - Built-in mini snake game
EOF

# Build the .deb package
echo "Building .deb package..."
dpkg-deb --build fadcrypt-deb ${PACKAGE_NAME}_${DEB_VERSION}_amd64.deb

echo ""
echo "=== Build Complete ==="
echo "Package: ${PACKAGE_NAME}_${DEB_VERSION}_amd64.deb"
echo "App Version: ${VERSION}"
echo ""
echo "To install:"
echo "  sudo dpkg -i ${PACKAGE_NAME}_${DEB_VERSION}_amd64.deb"
echo ""
echo "To run:"
echo "  ${PACKAGE_NAME}"
echo ""
