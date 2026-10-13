# Immutable XS codec data

`english-v1/` preserves the NWL23 and CSW24 KWG lexica and KLV2 leave values
from MAGPIE-DATA commit `ee46dfdb7d878584ab48e7158edc516aba3bdfc1` for XSP/XSG.
The profile name identifies these exact bytes, not whichever files happen to
be current under `data/lexica`. All four files initially use relative symlinks
to avoid duplicating existing data.

`manifest.json` records each stable path, byte length, and SHA256. The XS
validation workflow runs for all pull requests and main pushes: it checks
resolved contents and rejects removing or changing any existing identity from
the base revision. Run locally with:

```sh
python3 data/validate_xs_data.py --base-ref origin/main
```

## Updating normal lexica or leave values

Before replacing or removing a live file referenced by an XS symlink, replace
that symlink with a regular file containing its **original bytes**. Then update
the normal file. Keep the XS path and manifest checksum unchanged. Do not write
through the symlink: that would replace the live target as well.

New XS data revisions get new paths (for example `english-v2/`) and additional
manifest entries. Never repin or remove published XS profiles. Older links must
continue to resolve the same lexica and leave values.

## Distribution and consumers

These aliases are available in repository checkouts. This change does not
rewrite existing versioned tarballs or switch any codec consumer. Future data
bundles that offer XS support must include `data/xs` and either retain its
relative links with their targets or dereference them into frozen files. Keep
every published profile in those bundles.

Ranked XSG decoding must also pin its engine/ranking contract and standard board
and tile-distribution inputs. Preserving KWG/KLV2 bytes is necessary but does
not by itself guarantee that a different engine version generates identical
move ranks. Word-based XSP additionally requires its immutable word codebook.
