import importlib.util
import sys
sys.path.insert(0,str(__import__("pathlib").Path(__file__).parents[1]/"scripts"))
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

class SiteFeedTests(unittest.TestCase):
    def test_feed_is_deterministic_and_does_not_invent_media_or_remakes(self):
        import site_export
        rows=g.load()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'data').mkdir()
            (root/'data/site.json').write_text('{"gallery_url":null,"skills_url":"https://skillu.dev/skills/"}')
            a=site_export.feed(root,rows);before=(root/'data/site-feed.json').read_bytes()
            b=site_export.feed(root,rows)
            self.assertEqual(before,(root/'data/site-feed.json').read_bytes())
            self.assertEqual(sum(x['count'] for x in a['categories']),len(rows))
            self.assertTrue(all(v['video_url'] is None and v['remake'] is None for v in a['videos']))
            self.assertEqual(a['counts']['prompts'],2)

    def test_website_deep_links_only_after_route_is_configured(self):
        import site_export
        rows=g.load()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'data').mkdir()
            (root/'data/site.json').write_text('{"gallery_url":"https://skillu.dev/ai-videos/kimi-k3-1-pro/","skills_url":"https://skillu.dev/skills/"}')
            result=site_export.feed(root,rows)
            self.assertEqual(result['videos'][0]['website_url'],'https://skillu.dev/ai-videos/kimi-k3-1-pro/#robotic-hand')
