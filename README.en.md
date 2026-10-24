# Awesome Kimi K3.1 Pro Videos

Browse [the visual gallery](README.md) for Kimi K3.1 Pro animations, 3D scenes, and video workflows. Each entry links to its creator's original X post and records whether a prompt is fully shared, partially shared, or not shared.

## Rebuild the gallery

Requires Python 3.10+, FFmpeg and ffprobe on PATH.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/gallery.py build
```

Append an entry to `data/videos.json`, then rebuild. Videos stay in the ignored `.cache/` directory. Extracted frames, `assets/wall.jpg`, the clickable README grid, and prompt pages are generated locally. Unchanged entries reuse cached frames. `--only SLUG` selects an entry, `--force` refreshes its video and frame, and `render` rebuilds documents without network access. Download failures produce a nonzero exit status while preserving existing previews.

Third-party videos, frames, prompts and trademarks remain the property of their respective owners. The MIT license covers the original tooling, not third-party media. See [contribution instructions](CONTRIBUTING.md).
