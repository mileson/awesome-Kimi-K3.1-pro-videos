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
    text = '''# Awesome Kimi K3.1 Pro Videos

收集用 Kimi K3.1 Pro 制作的动画、3D 场景与视频，保留作者原帖和公开提示词。点击预览观看原视频。

[English](README.en.md) · [贡献作品](CONTRIBUTING.md) · [目录数据](data/videos.json)

'''
    text += f"已收录 **{len(rows)}** 个作品，其中 **{sum(bool(r.get('prompt')) for r in rows)}** 个有公开的完整或部分提示词。\n\n"
    if ready:
        text += '## 视频帧图片墙\n\n![Kimi K3.1 Pro 视频帧合集](assets/wall.jpg)\n\n'
    config=json.loads((ROOT/'data/site.json').read_text())
    destination=config.get('gallery_url') or config['skills_url']
    tracked=destination+'?utm_source=github&utm_medium=readme&utm_campaign=kimi-k3-1-pro-videos'
    text=text.replace('![Kimi K3.1 Pro 视频帧合集](assets/wall.jpg)', '[![Kimi K3.1 Pro 视频帧合集](assets/wall.jpg)]('+tracked+')')
    text += '[浏览 SkillU 视频合集]('+tracked+')\n\n' if config.get('gallery_url') else '[在 SkillU 浏览可获取的 Skill]('+tracked+')\n\n'
    text += '## 目录\n\n'
    for key,zh,en in GROUPS:
        count=sum(MAP[r['category']]==key for r in rows)
        if count:text += f'- [{zh}](#{key}) · {count}\n'
    text += '- [使用提示词](#使用提示词)\n- [添加作品与重新生成](#添加作品与重新生成)\n\n'
    for key,zh,en in GROUPS:
        group=[r for r in rows if MAP[r['category']]==key]
        if not group:continue
        text += f'<a id="{key}"></a>\n\n## {zh}\n\n<table>\n'
        for i,row in enumerate(group):
            if i%3==0:text += '<tr>\n'
            slug=row['slug']; label=html.escape(row['title']);url=row['post_url']
            card=(config.get('gallery_url')+'?utm_source=github&utm_medium=readme&utm_campaign=kimi-k3-1-pro-videos#'+slug) if config.get('gallery_url') else url
            preview=f'<img src="assets/frames/{slug}.jpg" width="100%" alt="{label}">' if row in ready else '观看视频'
            status={'full':'完整 Prompt','partial':'Prompt 片段','not-shared':'作品说明'}[row['prompt_status']]
            text+=f'<td width="33%" valign="top"><a href="{card}">{preview}</a><br><b>{label}</b><br><a href="{url}">@{row["author"]}</a> · <a href="prompts/{slug}.md">{status}</a><br><sub>{html.escape(row["description"])}</sub></td>\n'
            if i%3==2 or i==len(group)-1:text+='</tr>\n'
        text+='</table>\n\n'
    text+='## 使用提示词\n\n打开标有完整 Prompt 或 Prompt 片段的作品页，复制作者公开的内容，交给运行 Kimi K3.1 Pro 的 Agent。根据作品需要准备素材和运行环境，再预览、调整与导出。需要额外视频工具的流程会在作品页标注。\n\n'
    text+='[查看 SkillU 的相关 Skill]('+config['skills_url']+') · [网站导出数据](data/site-feed.json)\n\n'
    text += '''## 添加作品与重新生成

需要 Python 3.10+、FFmpeg 和 ffprobe。视频缓存在本地 `.cache/`，仓库只保存抽取的预览帧和目录。

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
# 向 data/videos.json 追加条目后，一条命令更新图片墙、README 和提示词页面
.venv/bin/python scripts/gallery.py build
# 只处理一个作品；仍会重新生成完整索引
.venv/bin/python scripts/gallery.py build --only pelican-bicycle
# 改选该作品的帧位置后重新抽帧
.venv/bin/python scripts/gallery.py build --only pelican-bicycle --force
# 不下载视频，只更新文档与已有图片的合集
.venv/bin/python scripts/gallery.py render
.venv/bin/python scripts/gallery.py validate
```

抽帧默认取视频 40% 的位置，可用 `frame_ratio` 调整。多视频原帖通过 `video_index` 选择，从 1 开始。相同来源与帧位置会复用缓存；失败时保留已有图片，命令以非零状态退出并列出失败项。

## 收录规则

作者原帖须明确关联 Kimi K3.1 Pro；保留原始出处。公开完整提示词、公开片段和未公开三种状态分别记录，不从视频反推作者提示词。涉及其他模型的对比视频会在作品页注明。作者自报的效果、耗时和费用不作为统一测评结论。

代码采用 MIT 许可。第三方视频、预览帧、提示词和商标的权利归原作者，不因收录而变为 MIT 许可；需要复用时请查阅原帖许可或联系作者。作品归属或收录有误可提交 Issue 更正或移除。

组织方式参考 [Awesome Opus 5.5 Videos](https://github.com/yihui-dev/awesome-opus5-5-videos)。本项目独立维护。
'''
    (ROOT/'README.md').write_text(text)
    for row in rows:
        prompt = row.get('prompt')
        body = f'# {row["title"]}\n\n[观看原视频]({row["post_url"]}) · [@{row["author"]}](https://x.com/{row["author"]})\n\n'
        body += f'{row["description"]}\n\n模型依据　{row["model_evidence"]}\n\n'
        if row.get('note'): body += row['note']+'\n\n'
        body += '## Prompt\n\n'
        body += ('作者公开'+('完整提示词' if row['prompt_status']=='full' else '片段')+'\n\n````text\n'+prompt+'\n````\n\n[提示词来源]('+row['prompt_source']+')\n') if prompt else '作者未在已核对的原帖中公开提示词。\n'
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
