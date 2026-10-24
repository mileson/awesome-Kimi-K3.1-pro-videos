"""Deterministic website feed and optional self-contained media handoff."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

REPO='https://github.com/mileson/awesome-Kimi-K3.1-pro-videos'
RAW='https://raw.githubusercontent.com/mileson/awesome-Kimi-K3.1-pro-videos/main'
GROUPS=[('motion','动态图形与动画','Motion graphics & animation'),('3d','3D 场景','3D scenes'),('games','游戏与交互','Games & interactive'),('video','视频工作流','Video workflows'),('official','官方展示','Official showcase')]
MAP={'SVG 动画':'motion','动态图形':'motion','3D':'3d','游戏':'games','视频创作':'video','官方展示':'official'}


def feed(root, rows):
    config=json.loads((root/'data/site.json').read_text())
    entries=[]
    for row in rows:
        slug=row['slug']; poster='assets/frames/'+slug+'.jpg'
        entries.append({**row,'category_id':MAP[row['category']], 'post_id':row['post_url'].rsplit('/',1)[1],
          'poster_url':RAW+'/'+poster,'poster_path':poster,
          'prompt_url':REPO+'/blob/main/prompts/'+slug+'.md' if row.get('prompt') else None,
          'website_url':config.get('gallery_url')+'#'+slug if config.get('gallery_url') else None,
          'video_url':row.get('video_url'),'video_path':'videos/'+slug+'.mp4',
          'playback':{'provider':'x','post_url':row['post_url']},
          'related_skills':row.get('related_skills',[]),'remake':row.get('remake')})
    result={'schema_version':1,'title':'Kimi K3.1 Pro Videos','repository_url':REPO,
       'gallery_url':config.get('gallery_url'),'skills_url':config['skills_url'],
       'updated':max((r['checked'] for r in rows),default=None),
       'categories':[{'id':a,'label_zh':b,'label_en':c,'count':sum(e['category_id']==a for e in entries)} for a,b,c in GROUPS],
       'counts':{'videos':len(rows),'prompts':sum(bool(r.get('prompt')) for r in rows),'remakes':sum(bool(r.get('remake')) for r in rows)},
       'videos':entries}
    (root/'data/site-feed.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


def bundle(root, rows, output):
    # Validate all inputs before writing a partial handoff.
    files=[]
    for row in rows:
        slug=row['slug']
        for source,dest in [(root/'.cache'/slug/'video.mp4','videos/'+slug+'.mp4'),(root/'assets/frames'/(slug+'.jpg'),'assets/frames/'+slug+'.jpg')]:
            if not source.is_file(): raise FileNotFoundError(str(source))
            files.append((source,dest))
    output=output.resolve()
    if root.resolve() not in output.parents or '.cache' not in output.relative_to(root.resolve()).parts:
        raise ValueError('Media output must stay in this repository .cache directory')
    data=feed(root,rows);output.mkdir(parents=True,exist_ok=True)
    checks=[]
    for source,dest in files:
        target=output/dest;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        checks.append({'path':dest,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    (output/'site-feed.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (output/'checksums.json').write_text(json.dumps(checks,indent=2)+'\n')
    archive=output.with_suffix('.zip')
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_STORED) as z:
        for name in ['site-feed.json','checksums.json']+[x['path'] for x in checks]:z.write(output/name,name)
    return archive
