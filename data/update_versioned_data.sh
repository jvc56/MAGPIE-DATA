#!/bin/bash
set -e

# Script to generate versioned data tarballs
# Creates MAGPIE-DATA/versioned-tarballs/data-YYYYMMDD.tgz for each version

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSIONED_DIR="$SCRIPT_DIR/versioned"
OUTPUT_DIR="$(dirname "$SCRIPT_DIR")/versioned-tarballs"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Iterate through each versioned directory
for version_dir in "$VERSIONED_DIR"/*; do
  if [ -d "$version_dir" ]; then
    version_name=$(basename "$version_dir")
    output_file="$OUTPUT_DIR/data-${version_name}.tgz"

    echo "Creating $output_file..."

    # Create temporary directory
    temp_dir=$(mktemp -d)

    # Copy the versioned directory to temp with name 'data'
    # Using cp -RL to follow symlinks
    cp -RL "$version_dir" "$temp_dir/data"

    # Create tarball from the renamed directory
    # Use --no-xattrs to exclude macOS extended attributes (._* files)
    tar --no-xattrs -czf "$output_file" -C "$temp_dir" "data"

    # Split into 40MB chunks if larger than 40MB
    file_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
    chunk_size=$((40 * 1024 * 1024))  # 40MB in bytes

    if [ "$file_size" -gt "$chunk_size" ]; then
      echo "Tarball is $(($file_size / 1024 / 1024))MB, splitting into 40MB chunks..."
      split -b 40m "$output_file" "${output_file}."
      rm "$output_file"
      echo "Created chunks: ${output_file}.*"
    else
      echo "Created $output_file ($(($file_size / 1024 / 1024))MB, no splitting needed)"
    fi

    # Clean up temp directory
    rm -rf "$temp_dir"
  fi
done

echo "All versioned data tarballs created in $OUTPUT_DIR"
