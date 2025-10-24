#!/bin/bash
# ClassTop Python Auto Setup Script for macOS (Apple Silicon)
# Automatically downloads and configures CPython for standalone build

set -e  # Exit on error

echo "🐍 ClassTop Python Auto Setup Script"
echo "===================================="
echo ""

# Configuration - Using known stable release
RELEASE_TAG="20241016"
PYTHON_VERSION="3.13.0"
PYTHON_SHORT="3.13"
ARCH="aarch64"
OS="apple-darwin"
BUILD_TYPE="install_only_stripped"

FILENAME="cpython-${PYTHON_VERSION}+${RELEASE_TAG}-${ARCH}-${OS}-${BUILD_TYPE}.tar.gz"
DOWNLOAD_URL="https://github.com/indygreg/python-build-standalone/releases/download/${RELEASE_TAG}/${FILENAME}"

PYEMBED_DIR="./src-tauri/pyembed"
PYTHON_DIR="${PYEMBED_DIR}/python"

echo "📋 Configuration:"
echo "   Python Version: ${PYTHON_VERSION}"
echo "   Release: ${RELEASE_TAG}"
echo "   Architecture: ${ARCH}"
echo "   Platform: ${OS}"
echo ""

# Check if already installed
if [ -f "${PYTHON_DIR}/bin/python3" ]; then
    echo "✅ Python already installed at ${PYTHON_DIR}"
    INSTALLED_VERSION=$(${PYTHON_DIR}/bin/python3 --version 2>&1)
    echo "   Installed: ${INSTALLED_VERSION}"
    echo ""
    read -p "Reinstall? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping installation."
        echo ""
        echo "🚀 You can now run: ./build.sh"
        exit 0
    fi
    echo "🗑️  Removing existing installation..."
    rm -rf "${PYEMBED_DIR}"
fi

# Create directory
echo "📁 Creating directory: ${PYEMBED_DIR}"
mkdir -p "${PYEMBED_DIR}"
cd "${PYEMBED_DIR}"

# Download
echo "⬇️  Downloading Python ${PYTHON_VERSION}..."
echo "   URL: ${DOWNLOAD_URL}"
echo ""

if command -v wget &> /dev/null; then
    wget -q --show-progress "${DOWNLOAD_URL}" -O "${FILENAME}"
elif command -v curl &> /dev/null; then
    curl -L --progress-bar "${DOWNLOAD_URL}" -o "${FILENAME}"
else
    echo "❌ Error: Neither wget nor curl found"
    echo "Please install curl: brew install curl"
    exit 1
fi

# Verify download
if [ ! -f "${FILENAME}" ]; then
    echo "❌ Error: Download failed"
    exit 1
fi

FILE_SIZE=$(ls -lh "${FILENAME}" | awk '{print $5}')
echo ""
echo "✅ Download complete (${FILE_SIZE})"
echo ""

# Extract tarball
echo "📦 Extracting Python..."
tar -xzf "${FILENAME}"

# Check extraction result
if [ ! -d "python" ]; then
    echo "❌ Error: Extraction failed - 'python' directory not found"
    exit 1
fi

echo "✅ Extraction complete"
echo ""

# Clean up tarball
echo "🧹 Cleaning up..."
rm -f "${FILENAME}"

# Find and patch libpython dylib
echo "🔍 Looking for libpython dylib..."
LIBPYTHON=$(find python/lib -name "libpython${PYTHON_SHORT}*.dylib" -type f 2>/dev/null | head -n 1)

if [ -z "$LIBPYTHON" ]; then
    echo "⚠️  Warning: Trying alternative search..."
    LIBPYTHON=$(find python/lib -name "libpython*.dylib" -type f 2>/dev/null | head -n 1)
fi

# Patch install_name if dylib found
if [ -n "$LIBPYTHON" ]; then
    DYLIB_NAME=$(basename "$LIBPYTHON")
    echo "✅ Found: $DYLIB_NAME"
    echo "🔧 Patching install_name..."
    install_name_tool -id "@rpath/$DYLIB_NAME" "$LIBPYTHON"
    echo "✅ Patching complete"
else
    echo "⚠️  Warning: Could not find libpython dylib to patch"
    echo "   This may cause runtime issues"
fi

echo ""
echo "🎉 Python setup complete!"
echo ""
echo "📁 Installation path: ${PYTHON_DIR}"
echo ""

# Go back to project root
cd ../..

# Verify installation
if [ -f "${PYTHON_DIR}/bin/python3" ]; then
    PYTHON_PATH="${PYTHON_DIR}/bin/python3"
    echo "✅ Verification:"
    $PYTHON_PATH --version
    echo ""

    # Show Python info
    echo "📊 Python details:"
    $PYTHON_PATH -c "import sys; print(f'   Prefix: {sys.prefix}')"
    $PYTHON_PATH -c "import sys; print(f'   Executable: {sys.executable}')"
    echo ""

    echo "🚀 Next steps:"
    echo "   Run: ./build.sh"
else
    echo "❌ Error: Python binary not found after installation"
    exit 1
fi
