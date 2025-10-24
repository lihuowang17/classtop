#!/bin/bash
# ClassTop Python Setup Script for macOS
# Downloads and configures CPython for standalone build

set -e  # Exit on error

echo "🐍 ClassTop Python Setup Script"
echo "================================"
echo ""

# Configuration
PYTHON_VERSION="3.13"
ARCH="aarch64"  # Apple Silicon
OS="apple-darwin"
TARBALL_NAME="cpython-${PYTHON_VERSION}*-${ARCH}-${OS}-install_only_stripped.tar.gz"
PYEMBED_DIR="./src-tauri/pyembed"
PYTHON_DIR="${PYEMBED_DIR}/python"

# GitHub release URL
RELEASES_URL="https://github.com/indygreg/python-build-standalone/releases"

echo "📋 Configuration:"
echo "   Python Version: ${PYTHON_VERSION}"
echo "   Architecture: ${ARCH}"
echo "   Platform: ${OS}"
echo ""

# Check if already installed
if [ -f "${PYTHON_DIR}/bin/python3" ]; then
    echo "✅ Python already installed at ${PYTHON_DIR}"
    echo ""
    read -p "Reinstall? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping installation."
        exit 0
    fi
    echo "🗑️  Removing existing installation..."
    rm -rf "${PYEMBED_DIR}"
fi

# Create directory
echo "📁 Creating directory: ${PYEMBED_DIR}"
mkdir -p "${PYEMBED_DIR}"
cd "${PYEMBED_DIR}"

# Find latest release
echo "🔍 Finding latest Python ${PYTHON_VERSION} release..."
echo ""
echo "Please visit: ${RELEASES_URL}"
echo "Download the file matching: ${TARBALL_NAME}"
echo ""
echo "After downloading, place it in: $(pwd)"
echo ""
read -p "Press Enter after you've downloaded the file..."

# Find the downloaded tarball
TARBALL=$(ls cpython-${PYTHON_VERSION}*-${ARCH}-${OS}-install_only_stripped.tar.gz 2>/dev/null | head -n 1)

if [ -z "$TARBALL" ]; then
    echo ""
    echo "❌ Error: Tarball not found in current directory"
    echo "Expected pattern: ${TARBALL_NAME}"
    echo "Current directory: $(pwd)"
    echo ""
    ls -la
    exit 1
fi

echo "✅ Found tarball: $TARBALL"
echo ""

# Extract tarball
echo "📦 Extracting Python..."
tar -xzf "$TARBALL"

# Check extraction result
if [ ! -d "python" ]; then
    echo "❌ Error: Extraction failed - 'python' directory not found"
    exit 1
fi

echo "✅ Extraction complete"
echo ""

# Find libpython dylib
LIBPYTHON=$(ls python/lib/libpython${PYTHON_VERSION}*.dylib 2>/dev/null | head -n 1)

if [ -z "$LIBPYTHON" ]; then
    echo "⚠️  Warning: libpython dylib not found, trying to locate..."
    LIBPYTHON=$(find python/lib -name "libpython*.dylib" | head -n 1)
fi

# Patch install_name if dylib found
if [ -n "$LIBPYTHON" ]; then
    DYLIB_NAME=$(basename "$LIBPYTHON")
    echo "🔧 Patching install_name for: $DYLIB_NAME"
    install_name_tool -id "@rpath/$DYLIB_NAME" "$LIBPYTHON"
    echo "✅ Patching complete"
else
    echo "⚠️  Warning: Could not find libpython dylib to patch"
    echo "   This may cause runtime issues"
fi

echo ""
echo "🎉 Python setup complete!"
echo ""
echo "📁 Python installed at: ${PYTHON_DIR}"
echo "🐍 Python binary: ${PYTHON_DIR}/bin/python3"
echo ""

# Verify installation
if [ -f "${PYTHON_DIR}/bin/python3" ]; then
    PYTHON_PATH="${PYTHON_DIR}/bin/python3"
    echo "✅ Verification:"
    echo "   Path: $PYTHON_PATH"
    $PYTHON_PATH --version
    echo ""
    echo "🚀 You can now run: ./build.sh"
else
    echo "❌ Error: Python binary not found after installation"
    exit 1
fi
