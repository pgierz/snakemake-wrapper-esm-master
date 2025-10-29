#!/bin/bash
# Script to build documentation with proper environment

set -e

echo "Setting up documentation build environment..."

# Install package with docs dependencies
pip install -e ".[docs]"

echo "Building documentation..."
cd docs
make clean
make html

echo "Documentation built successfully!"
echo "Open _build/html/index.html to view"
