#!/usr/bin/env python3
"""Build a source-linked video catalog and frame wall. Downloads stay local."""
import argparse
import hashlib
import html
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from PIL import Image, ImageOps, ImageDraw
from site_export import feed, bundle, GROUPS, MAP

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/videos.json'


def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=180).stdout


def load():
    rows = json.loads(DATA.read_text())
    seen = set()
    for row in rows:
        slug = row['slug']
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', slug) or slug in seen:
            raise ValueError('Invalid or duplicate slug: ' + slug)
        seen.add(slug)
        if not re.fullmatch(r'[A-Za-z0-9_]+', row['author']):
            raise ValueError('Invalid author')
        if row.get('prompt') and not re.fullmatch(r'https://x\.com/[A-Za-z0-9_]+/status/\d+', row.get('prompt_source') or ''):
            raise ValueError('Missing prompt source')
        if not isinstance(row.get('video_index', 1), int) or row.get('video_index', 1) < 1:
            raise ValueError('Invalid video_index')
        if not 0 <= float(row.get('frame_ratio', .4)) < 1:
            raise ValueError('Invalid frame_ratio')
        if not re.fullmatch(r'https://x\.com/[A-Za-z0-9_]+/status/\d+', row['post_url']):
            raise ValueError('Invalid source URL')
        if row['prompt_status'] not in ('full', 'partial', 'not-shared'):
            raise ValueError('Invalid prompt status')
        if bool(row.get('prompt')) != (row['prompt_status'] != 'not-shared'):
            raise ValueError('Prompt/status mismatch')
        if row.get('model') != 'Kimi K3.1 Pro' or not row.get('model_evidence'):
            raise ValueError('Missing model evidence')
    return rows


def frame(row, force=False):
    cache = ROOT / '.cache' / row['slug']
    cache.mkdir(parents=True, exist_ok=True)
    target = ROOT / 'assets/frames' / (row['slug'] + '.jpg')
    fingerprint = hashlib.sha256(json.dumps({k: row.get(k) for k in ('post_url', 'video_index', 'frame_ratio')}, sort_keys=True).encode()).hexdigest()
    stamp = cache / 'fingerprint'
    if not force and target.exists() and stamp.exists() and stamp.read_text() == fingerprint:
        return target
    video = cache / 'video.mp4'
    if not video.exists() or not stamp.exists() or stamp.read_text() != fingerprint or force:
        staged = cache / 'download.mp4'
        staged.unlink(missing_ok=True)
        run(['yt-dlp', '--socket-timeout', '20', '--retries', '1', '--playlist-items', str(row.get('video_index', 1)), '-f', 'best[ext=mp4][height<=720]/best[ext=mp4]/best', '-o', str(staged), row['post_url']])
        if not staged.exists():
            raise RuntimeError('No video downloaded')
        staged.replace(video)
    duration = float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', str(video)]).strip())
    ratio = float(row.get('frame_ratio', .4))
    if not 0 <= ratio < 1:
        raise ValueError('frame_ratio must be >= 0 and < 1')
    staged_frame = cache / 'frame.jpg'
    run(['ffmpeg', '-v', 'error', '-y', '-threads', '1', '-ss', str(duration * ratio), '-i', str(video), '-frames:v', '1', '-vf', 'scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2', str(staged_frame)])
    with Image.open(staged_frame) as im:
        im.verify()
    staged_frame.replace(target)
    stamp.write_text(fingerprint)
    return target


def render(rows):
    ready = [r for r in rows if (ROOT / 'assets/frames' / (r['slug'] + '.jpg')).exists()]
    if ready:
        cols = min(3, len(ready)); w, h = 480, 300
        wall = Image.new('RGB', (cols*w, math.ceil(len(ready)/cols)*h), '#10131b')
        draw = ImageDraw.Draw(wall)
        for i, row in enumerate(ready):
            x,y = i%cols*w, i//cols*h
            with Image.open(ROOT/'assets/frames'/(row['slug']+'.jpg')) as im:
                wall.paste(ImageOps.pad(im.convert('RGB'), (w-12, 258), color='#10131b'), (x+6,y+6))
            draw.text((x+12,y+273), f"{i+1:02}  @{row['author']}", fill='white')
        wall.save(ROOT/'assets/wall.jpg', quality=88)
    feed(ROOT, rows)
    config=json.loads((ROOT/'data/site.json').read_text())
    destination=config.get('gallery_url') or config['skills_url']
    tracked=destination+'?utm_source=github&utm_medium=readme&utm_campaign=kimi-k3-1-pro-videos'
    text = '# Awesome Kimi K3.1 Pro Videos\n\n'
    if ready:
        text += '[![Kimi K3.1 Pro videos](assets/wall.jpg)]('+tracked+')\n\n'
    text += 'Videos, animations, 3D scenes, and games made with **Kimi K3.1 Pro**, with prompts shared by their creators and links to the original posts.\n\nPick a video, copy its prompt, and try it with your own agent.\n\n'
    text += '**[▶ Watch all '+str(len(rows))+' videos on SkillU]('+tracked+')**\n\n'
    text += f'- **{len(rows)}** videos to browse by category\n- **{sum(bool(r.get("prompt")) for r in rows)}** shared prompts in [prompts/](prompts/)\n- Every entry links to the creator’s original post\n\n'
    text += '## Contents\n\n'
    for key,zh,en in GROUPS:
        count=sum(MAP[r['category']]==key for r in rows)
        if count:text += f'- [{en}](#{key}) · {count}\n'
    text += '- [How to use a prompt](#how-to-use-a-prompt)\n- [Credits](#credits)\n\n'
    for key,zh,en in GROUPS:
        group=[r for r in rows if MAP[r['category']]==key]
        if not group:continue
        text += f'<a id="{key}"></a>\n\n## {en}\n\n<table>\n'
        for i,row in enumerate(group):
            if i%3==0:text += '<tr>\n'
            slug=row['slug']; label=html.escape(row.get('title_en', row['title']));url=row['post_url']
            card=(config.get('gallery_url')+'?utm_source=github&utm_medium=readme&utm_campaign=kimi-k3-1-pro-videos#'+slug) if config.get('gallery_url') else url
            preview=f'<img src="assets/frames/{slug}.jpg" width="100%" alt="{label}">' if row in ready else 'Watch video'
            status={'full':'Prompt','partial':'Partial prompt','not-shared':'Original post'}[row['prompt_status']]
            prompt_link = f'prompts/{slug}.md' if row.get('prompt') else url
            text+=f'<td width="33%" valign="top"><a href="{card}">{preview}</a><br><b>{label}</b><br><a href="{url}">@{row["author"]}</a> · <a href="{prompt_link}">{status}</a><br><sub>{html.escape(row.get("description_en", row["description"]))}</sub></td>\n'
            if i%3==2 or i==len(group)-1:text+='</tr>\n'
        text+='</table>\n\n'
    text += '## How to use a prompt\n\n1. Open a prompt file and copy the block under **Prompt**.\n2. Paste it into an agent running Kimi K3.1 Pro.\n3. Ask it to create the animation or scene, then preview and export the result.\n\nSome creators shared only part of their prompt or described the result in their post; those files say so.\n\n'
    text += '## Credits\n\nEvery video and prompt belongs to its creator, linked from each entry. To request a correction or removal, open an issue.\n\n'
    text += 'Browse the full collection on **[SkillU]('+tracked+')**, or [get video creation skills]('+config['skills_url']+') to make your own.\n'
    (ROOT/'README.md').write_text(text)
    (ROOT/'README.en.md').write_text(text)
    for row in rows:
        prompt = row.get('prompt')
        body = f'# {row.get("title_en", row["title"])}\n\n[Watch original video]({row["post_url"]}) · [@{row["author"]}](https://x.com/{row["author"]})\n\n'
        body += f'{row.get("description_en", row["description"])}\n\n'
        if row.get('note_en'): body += row['note_en']+'\n\n'
        body += '## Prompt\n\n'
        body += (('Full prompt shared by the creator' if row['prompt_status']=='full' else 'Prompt excerpt shared by the creator')+'\n\n````text\n'+prompt+'\n````\n\n[Prompt source]('+row['prompt_source']+')\n') if prompt else 'The creator did not share a prompt in the original post.\n'
        (ROOT/'prompts'/(row['slug']+'.md')).write_text(body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build','render','validate','export-site'])
    parser.add_argument('--output',default='.cache/skillu-import');
    parser.add_argument('--only'); parser.add_argument('--force', action='store_true')
    args = parser.parse_args(); rows=load()
    if args.only and args.only not in {r['slug'] for r in rows}: parser.error('Unknown slug')
    if args.command=='export-site':
        print(bundle(ROOT,rows,ROOT/args.output));return 0
    failures=[]
    if args.command=='build':
        for row in rows:
            if args.only and row['slug']!=args.only: continue
            try:
                frame(row,args.force); print('OK',row['slug'],flush=True)
            except (subprocess.SubprocessError, OSError, ValueError, RuntimeError) as exc:
                failures.append(row['slug']); print('FAILED',row['slug'],type(exc).__name__,file=sys.stderr,flush=True)
    if args.command!='validate': render(rows)
    print(f'{len(rows)} entries validated; {len(failures)} failures')
    return bool(failures)

if __name__=='__main__': sys.exit(main())
