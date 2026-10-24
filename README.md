# Awesome Kimi K3.1 Pro Videos

收集用 Kimi K3.1 Pro 制作的动画、3D 场景与视频，保留作者原帖和公开提示词。点击预览观看原视频。

[English](README.en.md) · [贡献作品](CONTRIBUTING.md) · [目录数据](data/videos.json)

已收录 **6** 个作品，其中 **2** 个有公开的完整或部分提示词。

## 视频帧图片墙

![Kimi K3.1 Pro 视频帧合集](assets/wall.jpg)

## 作品索引

<table>
<tr>
<td width="33%" valign="top"><a href="https://x.com/crystalsssup/status/2113684128734625948"><img src="assets/frames/robotic-hand.jpg" width="280" alt="机械手的 2,317 个部件"></a><br><b>机械手的 2,317 个部件</b><br><a href="https://x.com/crystalsssup">@crystalsssup</a> · 3D<br><a href="prompts/robotic-hand.md">作品与提示词</a></td>
<td width="33%" valign="top"><a href="https://x.com/zstmfhy/status/2113804589174862231"><img src="assets/frames/pelican-bicycle.jpg" width="280" alt="鹈鹕骑自行车"></a><br><b>鹈鹕骑自行车</b><br><a href="https://x.com/zstmfhy">@zstmfhy</a> · SVG 动画<br><a href="prompts/pelican-bicycle.md">作品与提示词</a></td>
<td width="33%" valign="top"><a href="https://x.com/bubbubbdex/status/2113701194187059221"><img src="assets/frames/spider-city.jpg" width="280" alt="蜘蛛侠城市穿行"></a><br><b>蜘蛛侠城市穿行</b><br><a href="https://x.com/bubbubbdex">@bubbubbdex</a> · 游戏<br><a href="prompts/spider-city.md">作品与提示词</a></td>
</tr>
<tr>
<td width="33%" valign="top"><a href="https://x.com/Kimi_Moonshot/status/2113681863109939271"><img src="assets/frames/official-showcase.jpg" width="280" alt="Kimi K3.1 Pro 官方展示"></a><br><b>Kimi K3.1 Pro 官方展示</b><br><a href="https://x.com/Kimi_Moonshot">@Kimi_Moonshot</a> · 官方展示<br><a href="prompts/official-showcase.md">作品与提示词</a></td>
<td width="33%" valign="top"><a href="https://x.com/renoiseai/status/2113693742163218695"><img src="assets/frames/motion-trailer.jpg" width="280" alt="Renoise 影片创作"></a><br><b>Renoise 影片创作</b><br><a href="https://x.com/renoiseai">@renoiseai</a> · 视频创作<br><a href="prompts/motion-trailer.md">作品与提示词</a></td>
<td width="33%" valign="top"><a href="https://x.com/renoiseai/status/2113689744014209045"><img src="assets/frames/motion-with-intent.jpg" width="280" alt="Motion With Intent"></a><br><b>Motion With Intent</b><br><a href="https://x.com/renoiseai">@renoiseai</a> · 动态图形<br><a href="prompts/motion-with-intent.md">作品与提示词</a></td>
</tr>
</table>

## 添加作品与重新生成

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
