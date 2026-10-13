import copy
import unittest

from xs_codebook import build, validate_codebook


class CodebookTest(unittest.TestCase):
    def test_canonical_bits_and_round_trip(self):
        book = build(b'AA\t8\nAB\t4\nAC\t2\nAD\t1\n', 'CSW24')
        codes = validate_codebook(book)
        self.assertEqual(codes, {'AA': (0, 1), 'AB': (2, 2), 'AC': (6, 3), 'AD': (7, 3)})
        words = ['AD', 'AA', 'AC', 'AB', 'AA']
        stream = ''.join(format(codes[word][0], f"0{codes[word][1]}b") for word in words)
        inverse = {format(value, f'0{length}b'): word for word, (value, length) in codes.items()}
        decoded, pending = [], ''
        for bit in stream:
            pending += bit
            if pending in inverse:
                decoded.append(inverse[pending])
                pending = ''
        self.assertEqual(decoded, words)
        self.assertEqual(pending, '')

    def test_invalid_and_ambiguous_codebooks(self):
        original = build(b'AA\t4\nAB\t2\nAC\t1\n', 'NWL23')
        for entries in (
            [['AA', 1], ['AB', 1], ['AC', 1]],
            [['AA', 3], ['AB', 3]],
            [['AA', 1], ['AA', 1]],
            [['AA', 0]], [['AA', 33]], [['aA', 1]],
        ):
            book = copy.deepcopy(original)
            book['words'] = entries
            with self.assertRaises(ValueError):
                validate_codebook(book)
        book = copy.deepcopy(original)
        book['version'] = 2
        with self.assertRaises(ValueError):
            validate_codebook(book)


if __name__ == '__main__':
    unittest.main()
