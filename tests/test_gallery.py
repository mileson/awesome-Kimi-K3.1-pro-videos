import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
spec = importlib.util.spec_from_file_location('gallery',Path(__file__).parents[1]/'scripts/gallery.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

class CatalogTests(unittest.TestCase):
    def test_duplicate_and_path_traversal_rejected(self):
        rows=g.load()
        for bad in [rows+[rows[0]], [dict(rows[0],slug='../escape')]]:
            with tempfile.TemporaryDirectory() as d:
                path=Path(d)/'videos.json';path.write_text(json.dumps(bad))
                with patch.object(g,'DATA',path),self.assertRaises(ValueError): g.load()

    def test_missing_prompt_not_invented(self):
        rows=g.load();bad=dict(rows[0],prompt=None,prompt_status='full')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'videos.json';path.write_text(json.dumps([bad]))
            with patch.object(g,'DATA',path),self.assertRaises(ValueError): g.load()

    def test_cached_frame_avoids_network_and_ffmpeg(self):
        row=g.load()[0]
        with tempfile.TemporaryDirectory() as d,patch.object(g,'ROOT',Path(d)):
            cache=Path(d)/'.cache'/row['slug'];cache.mkdir(parents=True)
            target=Path(d)/'assets/frames'/(row['slug']+'.jpg');target.parent.mkdir(parents=True);target.touch()
            fp=g.hashlib.sha256(json.dumps({k:row.get(k) for k in ('post_url','video_index','frame_ratio')},sort_keys=True).encode()).hexdigest()
            (cache/'fingerprint').write_text(fp)
            with patch.object(g,'run',side_effect=AssertionError('must reuse')): self.assertEqual(g.frame(row),target)

if __name__=='__main__': unittest.main()
