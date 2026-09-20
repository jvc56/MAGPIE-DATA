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

    # cp -RL dereferences every symlink, including ones that only exist to
    # avoid duplicating a file within data/lexica or data/strategy (e.g. a
    # lexicon edition symlinked to another edition's leaves/PAT because it
    # ships the same weights). Those are safe to restore as real symlinks
    # in the tarball: both the link and its target live in the same
    # directory, so they resolve correctly no matter where the tarball is
    # extracted. Symlinks whose target escapes their directory (like
    # data/versioned/*/lexica -> ../../lexica, which points outside this
    # snapshot into the live repo tree) must stay dereferenced, since that
    # path will not exist for someone who only has the extracted tarball.
    find "$SCRIPT_DIR" -type l | while read -r link; do
      target=$(readlink "$link")
      case "$target" in
        */*) continue ;;  # escapes its directory -- keep dereferenced
      esac
      rel="${link#"$SCRIPT_DIR"/}"
      if [ -e "$temp_dir/data/$rel" ] || [ -L "$temp_dir/data/$rel" ]; then
        ln -sf "$target" "$temp_dir/data/$rel"
      fi
    done

    # Remove extended attributes on macOS to prevent ._* files
    if command -v xattr >/dev/null 2>&1; then
        xattr -r -clear "$temp_dir/data" 2>/dev/null || true
    fi

    # Create tarball from the renamed directory
    # Use --no-xattrs to exclude macOS extended attributes
    # Set COPYFILE_DISABLE=1 to prevent ._* AppleDouble files on macOS
    COPYFILE_DISABLE=1 tar --no-xattrs -czf "$output_file" -C "$temp_dir" "data"

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
