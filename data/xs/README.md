# Immutable XS codec data

`english-v1/` preserves the NWL23 and CSW24 KWG lexica and KLV2 leave values
from MAGPIE-DATA commit `ee46dfdb7d878584ab48e7158edc516aba3bdfc1` for XSP/XSG.
The profile name identifies these exact bytes, not whichever files happen to
be current under `data/lexica`. All four files initially use relative symlinks
to avoid duplicating existing data.

The same profile also contains two **actual word codebook files**, trained on
one million native static-equity games per lexicon:

| File | Observed words | Word occurrences | Gzipped bytes |
| --- | ---: | ---: | ---: |
| `english-v1/CSW24.xsw.json.gz` | 172,959 | 48,537,742 | 604,693 |
| `english-v1/NWL23.xsw.json.gz` | 129,591 | 46,850,830 | 455,807 |

CSW24 is the shared English default and can encode NWL positions; NWL23 is an
optional separately trained model. A position's rules lexicon does not select
its word codebook implicitly: encoded data must identify the book used. These
files are for word-based XSP. The current XSG pilot uses static move ranks and
does not need a separate trained word book or draw-frequency file.

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

## Word codebook format and provenance

Each `.xsw.json.gz` decompresses to a JSON object with `format` equal to
`xs-word-codebook`, format `version` 1, an immutable `id` (`en-CSW24-v1` or
`en-NWL23-v1`), `language`, `lexicon`, the SHA256 of the uncompressed training
count TSV, total `word_occurrences`, and `words`. Each word entry is
`[UPPERCASE_WORD, CODE_LENGTH]`, stored in alphabetical order.

To reconstruct codes, sort entries by `(CODE_LENGTH, WORD)`. Starting with code
0 and previous length 0, shift the code left by the increase in length, assign
the resulting integer at that bit length, increment the code, and continue.
Emit bits most significant first. `data/xs_codebook.py` implements this and
rejects duplicate words and over/undersubscribed Huffman trees. Both files use
the exact canonical codes from MAGPIE's word-codec pilot, not just similar
frequencies. Unknown words and isolated letters require the position codec's
literal fallback; no escape word is included in these tables.

Training used four 250,000-game seed ranges starting at 0, 250000, 500000, and
750000, with WMP on and WIT/RIT off. Counts include each newly formed maximal
word of length at least two, including crosswords; blanks normalize to letters.
Held-out evaluation games are excluded. The native generator and pilot are in
[MAGPIE PR #799](https://github.com/jvc56/MAGPIE/pull/799). The engine source at
training corresponds to MAGPIE commit `dab7e7f2`; the lexicon/leave file hashes
match the four assets pinned here.

Rebuild from an aggregated training count TSV (one `WORD<TAB>COUNT` per line):

```sh
python3 data/xs_codebook.py --lexicon CSW24 \
  --counts csw24-million-word-counts.tsv.gz \
  --output /tmp/CSW24.xsw.json.gz
```

Training data is not required for encoding or decoding. Preserve the published
codebooks rather than regenerating them during installation. The gzip streams
have zero timestamps and no filenames. Their complete bytes are pinned by the
XS manifest; a different compressor implementation can produce different gzip
bytes even for identical JSON, so regenerated files are not substitutes for
published assets without checksum verification.

## Distribution and consumers

These aliases are available in repository checkouts. This change does not
rewrite existing versioned tarballs or switch any codec consumer. Future data
bundles that offer XS support must include `data/xs` and either retain its
relative links with their targets or dereference them into frozen files. Keep
every published profile in those bundles.

Ranked XSG decoding must also pin its engine/ranking contract and standard board
and tile-distribution inputs. Preserving KWG/KLV2 bytes is necessary but does
not by itself guarantee that a different engine version generates identical
move ranks. Word-based XSP should use the immutable codebooks provided here.
