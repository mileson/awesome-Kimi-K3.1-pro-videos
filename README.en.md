# Awesome Kimi K3.1 Pro Videos

Watch [the videos on SkillU](https://skillu.dev/ai-videos/kimi-k3-1-pro/?utm_source=github&utm_medium=readme&utm_campaign=kimi-k3-1-pro-videos) or browse [the GitHub gallery](README.md) for Kimi K3.1 Pro animations, 3D scenes, and video workflows. Each entry links to its creator's original X post and records whether a prompt is fully shared, partially shared, or not shared.

## Rebuild the gallery

Requires Python 3.10+, FFmpeg and ffprobe on PATH.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/gallery.py build
```

Append an entry to `data/videos.json`, then rebuild. Videos stay in the ignored `.cache/` directory. Extracted frames, `assets/wall.jpg`, the clickable README grid, and prompt pages are generated locally. Unchanged entries reuse cached frames. `--only SLUG` selects an entry, `--force` refreshes its video and frame, and `render` rebuilds documents without network access. Download failures produce a nonzero exit status while preserving existing previews.

Third-party videos, frames, prompts and trademarks remain the property of their respective owners. The MIT license covers the original tooling, not third-party media. See [contribution instructions](CONTRIBUTING.md).

## Browse by format

- [Motion graphics & animation](README.md#motion)
- [3D scenes](README.md#3d)
- [Games & interactive](README.md#games)
- [Video workflows](README.md#video)
- [Official showcase](README.md#official)

Explore available creation skills on [SkillU](https://skillu.dev/skills/?utm_source=github&utm_medium=readme&utm_campaign=kimi-k3-1-pro-videos). A related Skill is a suggested creation tool, not a claim about the original creator's toolchain.

## Website integration

`data/site-feed.json` is regenerated with every build. It includes category counts, poster URLs, original posts, prompt availability, and optional related Skill and remake records. The [integration guide](docs/website-integration.md) explains the fields and media handoff.

```sh
python3 scripts/gallery.py export-site
```

The command packages cached videos, frames, the feed and SHA-256 checksums into `.cache/skillu-import.zip` for the website maintainer. It does not upload or publish media automatically.

## Get video creation skills

These are independent SkillU tools for making your own work.

| Skill | Get it |
| --- | --- |
| [Kinetic Title Video](https://skillu.dev/skills/kinetic-title-video/) | [Free download](https://skillu.dev/api/dl/kinetic-title-video) |
| [Terminal Typing Video](https://skillu.dev/skills/terminal-typing-video/) | [Free download](https://skillu.dev/api/dl/terminal-typing-video) |
| [Pipeline Flow Video](https://skillu.dev/skills/pipeline-flow-video/) | [Free download](https://skillu.dev/api/dl/pipeline-flow-video) |
| [Animated Stats Video](https://skillu.dev/skills/animated-stats-video/) | [Free download](https://skillu.dev/api/dl/animated-stats-video) |
