import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from validate_xs_data import validate


class ImmutableAssetsTest(unittest.TestCase):
    def test_target_update_requires_frozen_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory) / 'data'
            live = data / 'lexica/CSW24.kwg'
            live.parent.mkdir(parents=True)
            original = b'original lexicon'
            live.write_bytes(original)
            root = data / 'xs'
            alias = root / 'english-v1/CSW24.kwg'
            alias.parent.mkdir(parents=True)
            alias.symlink_to('../../lexica/CSW24.kwg')
            manifest = {'version': 1, 'files': {'english-v1/CSW24.kwg': {
                'sha256': hashlib.sha256(original).hexdigest(), 'bytes': len(original),
            }}}
            validate(root, manifest)
            live.write_bytes(b'replacement lexicon')
            with self.assertRaisesRegex(ValueError, 'XS data changed'):
                validate(root, manifest)
            # Freeze before allowing the normal lexicon target to evolve.
            alias.unlink()
            alias.write_bytes(original)
            validate(root, manifest, copy.deepcopy(manifest))
            changed = copy.deepcopy(manifest)
            changed['files']['english-v1/CSW24.kwg']['sha256'] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'identity changed or removed'):
                validate(root, changed, manifest)
            removed = copy.deepcopy(manifest)
            removed['files'] = {'another-v2/file': changed['files']['english-v1/CSW24.kwg']}
            with self.assertRaisesRegex(ValueError, 'identity changed or removed'):
                validate(root, removed, manifest)
            alias.unlink()
            with self.assertRaises(FileNotFoundError):
                validate(root, manifest)


if __name__ == '__main__':
    unittest.main()
