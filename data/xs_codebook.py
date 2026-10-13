#!/usr/bin/env python3
"""Build and validate immutable canonical Huffman word codebooks for XS."""

import argparse
import gzip
import hashlib
import heapq
import json
from pathlib import Path
import re


def canonical_codes(entries):
    codes = {}
    value, previous = 0, 0
    for word, length in sorted(entries, key=lambda item: (item[1], item[0])):
        value <<= length - previous
        if value >= 1 << length:
            raise ValueError('Oversubscribed Huffman lengths')
        codes[word] = (value, length)
        value += 1
        previous = length
    if len(entries) > 1 and value != 1 << previous:
        raise ValueError('Incomplete Huffman tree')
    return codes


def validate_codebook(book):
    if book.get('format') != 'xs-word-codebook' or book.get('version') != 1:
        raise ValueError('Unsupported XS word codebook')
    if book.get('language') != 'en' or book.get('lexicon') not in ('CSW24', 'NWL23'):
        raise ValueError('Unsupported codebook language or lexicon')
    if book.get('id') != f"en-{book['lexicon']}-v1":
        raise ValueError('Invalid codebook identity')
    entries = book.get('words')
    if not isinstance(entries, list) or not 1 <= len(entries) <= 300000:
        raise ValueError('Invalid codebook entries')
    previous = ''
    for entry in entries:
        if not isinstance(entry, list) or len(entry) != 2:
            raise ValueError('Invalid word entry')
        word, length = entry
        if not isinstance(word, str) or not re.fullmatch('[A-Z]{2,15}', word) or word <= previous:
            raise ValueError('Invalid, duplicate, or unsorted word')
        if type(length) is not int or not 1 <= length <= 32:
            raise ValueError('Invalid code length')
        previous = word
    return canonical_codes(entries)


def build(raw_counts, lexicon):
    counts = {}
    for line in raw_counts.decode('ascii').splitlines():
        word, count = line.split('\t')
        if word in counts or not re.fullmatch('[A-Z]{2,15}', word) or int(count) <= 0:
            raise ValueError('Invalid training count')
        counts[word] = int(count)
    if not counts:
        raise ValueError('Empty training counts')
    # Match MAGPIE's word-codec pilot: ties use the smallest word in the subtree.
    heap = [(count, word, word) for word, count in counts.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        first, second = heapq.heappop(heap), heapq.heappop(heap)
        heapq.heappush(heap, (first[0] + second[0], min(first[1], second[1]), (first[2], second[2])))
    lengths = {}
    pending = [(heap[0][2], 0)]
    while pending:
        node, depth = pending.pop()
        if isinstance(node, str):
            lengths[node] = max(1, depth)
        else:
            pending.extend((child, depth + 1) for child in node)
    book = {
        'format': 'xs-word-codebook', 'version': 1,
        'id': f'en-{lexicon}-v1', 'language': 'en', 'lexicon': lexicon,
        'source_counts_sha256': hashlib.sha256(raw_counts).hexdigest(),
        'word_occurrences': sum(counts.values()),
        'words': [[word, lengths[word]] for word in sorted(lengths)],
    }
    validate_codebook(book)
    return book


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--counts', required=True, help='Aggregated word/count TSV, optionally gzipped')
    parser.add_argument('--lexicon', required=True, choices=('CSW24', 'NWL23'))
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    source = Path(args.counts)
    raw = gzip.decompress(source.read_bytes()) if source.suffix == '.gz' else source.read_bytes()
    book = build(raw, args.lexicon)
    payload = json.dumps(book, ensure_ascii=True, separators=(',', ':')).encode('ascii') + b'\n'
    # Fixed mtime and no source filename; bytes do not depend on machine paths.
    with Path(args.output).open('wb') as target:
        with gzip.GzipFile(filename='', mode='wb', compresslevel=9, mtime=0, fileobj=target) as compressed:
            compressed.write(payload)
    print(f"Wrote {len(book['words'])} words to {args.output}")


if __name__ == '__main__':
    main()
