#!/bin/bash
set -e

# Script to generate versioned testdata tarballs
# Creates MAGPIE-DATA/versioned-tarballs/testdata-YYYYMMDD.tgz for each version

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSIONED_DIR="$SCRIPT_DIR/versioned"
OUTPUT_DIR="$(dirname "$SCRIPT_DIR")/versioned-tarballs"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Iterate through each versioned directory
for version_dir in "$VERSIONED_DIR"/*; do
  if [ -d "$version_dir" ]; then
    version_name=$(basename "$version_dir")
    output_file="$OUTPUT_DIR/testdata-${version_name}.tgz"

    echo "Creating $output_file..."

    # Create temporary directory
    temp_dir=$(mktemp -d)

    # Copy the versioned directory to temp with name 'testdata'
    # Using cp -RL to follow symlinks
    cp -RL "$version_dir" "$temp_dir/testdata"

    # Create tarball from the renamed directory
    tar -czf "$output_file" -C "$temp_dir" "testdata"

    # Clean up temp directory
    rm -rf "$temp_dir"

    echo "Created $output_file"
  fi
done

echo "All versioned testdata tarballs created in $OUTPUT_DIR"
