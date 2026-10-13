#!/usr/bin/env python3
"""Verify immutable XS data identities and their resolved file contents."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess

from xs_codebook import validate_codebook


MANIFEST_PATH = 'data/xs/manifest.json'


def validate(root, manifest, previous=None):
    if manifest.get('version') != 1 or not manifest.get('files'):
        raise ValueError('Invalid XS manifest')
    if previous is not None:
        if previous.get('version') != manifest['version']:
            raise ValueError('Existing XS manifest version must remain readable')
        for name, identity in previous['files'].items():
            if manifest['files'].get(name) != identity:
                raise ValueError(f'Existing XS identity changed or removed: {name}')
    for name, identity in manifest['files'].items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or '\\' in name:
            raise ValueError(f'Invalid XS path: {name}')
        path = root / relative
        # Repository links may reach data/lexica, but not outside data/.
        resolved = path.resolve(strict=True)
        if root.parent.resolve() not in resolved.parents:
            raise ValueError(f'XS link escapes data directory: {name}')
        raw = resolved.read_bytes()
        if len(raw) != identity['bytes'] or hashlib.sha256(raw).hexdigest() != identity['sha256']:
            raise ValueError(
                f'XS data changed: {name}. Preserve its original bytes at the XS '
                'path before updating the live target; do not update its checksum.'
            )
        if name.endswith('.xsw.json.gz'):
            validate_codebook(json.loads(gzip.decompress(raw)))


def previous_manifest(repo, ref):
    # Distinguish the first addition of XS from an unreadable/missing Git ref.
    paths = subprocess.run(
        ['git', 'ls-tree', '--name-only', ref, '--', MANIFEST_PATH],
        cwd=repo, check=True, capture_output=True, text=True,
    ).stdout.strip()
    if not paths:
        return None
    raw = subprocess.run(
        ['git', 'show', f'{ref}:{MANIFEST_PATH}'], cwd=repo,
        check=True, capture_output=True, text=True,
    ).stdout
    return json.loads(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-ref', help='Reject removal or repinning of identities from this Git revision')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    manifest = json.loads((repo / MANIFEST_PATH).read_text())
    previous = previous_manifest(repo, args.base_ref) if args.base_ref else None
    try:
        validate(repo / 'data/xs', manifest, previous)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'XS data validation failed: {error}\n')
    print(f"Validated {len(manifest['files'])} immutable XS assets")


if __name__ == '__main__':
    main()
