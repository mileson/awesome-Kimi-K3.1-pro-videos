# SkillU 网站接入

`data/videos.json` 是策展源，`data/site-feed.json` 是生成的网页数据。每次运行 `render` 或 `build` 都会同步更新导出；不要直接编辑生成文件。

## 字段与展示

- `schema_version` 当前为 1。`categories` 带中英文分类名及实际条目数。
- `poster_url` 可直接读取公开预览图；`poster_path` 对应导入包内相对位置。
- `playback.post_url` 为 X 原帖，`post_id` 可供网站使用官方嵌入。
- `video_url` 只填写已核实可长期使用的媒体地址。为空时可嵌入原帖，或从媒体包的 `video_path` 导入视频后改用网站媒体地址；不要把下载器临时签名地址写入目录。
- `prompt_status` 区分完整、部分和未公开。只有非空 `prompt` 才显示复制按钮。
- `related_skills` 只能关联网站真实存在且适配该作品的 Skill，使用对象 `{slug, name, url}`。关联代表可用的创作工具，不意味着原作者使用过它。
- `remake` 无真实复刻时为 null，不展示比较开关。有作品时使用 `{url, video_url, poster_url, author}`，并在发布前核对各链接。
- `website_url` 在内页上线、路径核实后生成；此前保持 null。

## 导入媒体

```sh
python3 scripts/gallery.py export-site
```

输出 `.cache/skillu-import.zip`，包含 6 个本地视频、对应封面、数据与 SHA-256 清单。媒体包保持在忽略目录，交给网站维护者导入现有媒体托管。导入后按清单核对文件大小与哈希，抽查播放、拖动、移动端和失败时的原帖入口。

媒体包里的 `video_path` 是包内相对路径，公开 JSON 本身不代表该路径已经上线。网站应将其转换为真实的媒体地址；不要直接把该路径挂到未部署的目录。

上线后在 `data/site.json` 设置真实的 `gallery_url`，重新生成 README 与导出数据。图片墙和作品卡片随后会指向内页，并保留 UTM 与作品锚点。网站应保留 `id=slug` 的卡片锚点、GitHub 来源链接和作者原帖。
