# 贡献作品

在 `data/videos.json` 追加一项，参考已有条目的字段。

- `slug` 使用不重复的小写英文、数字与连字符。
- `title`、`description`、`category` 描述作品内容。
- `author` 填 X 用户名，不带 @；`post_url` 填原帖永久链接。
- `model` 填 `Kimi K3.1 Pro`，`model_evidence` 记录原作者的明确说明。
- `prompt_status` 选择 `full`、`partial` 或 `not-shared`。前两种须填 `prompt` 与 `prompt_source`；没有公开则填 null，不自行补写。
- `video_index` 选择原帖中的第几个视频，从 1 开始。
- `frame_ratio` 为抽帧相对位置，范围为大于等于 0、小于 1，默认 0.4。
- `added`、`checked` 填实际收录与核对日期，格式为 YYYY-MM-DD。
- `note` 记录对比视频、外部工具等影响理解的信息。

先核对作者原帖与视频，再运行下列命令。不要将登录资料、cookie、原视频缓存或本地日志提交到仓库。

```sh
python3 scripts/gallery.py validate
python3 scripts/gallery.py build --only your-slug
python3 -m unittest discover -s tests
```

原帖仅写 K3、K2.5 或版本不明的作品请先核实，不归入 K3.1 Pro。更正出处或移除作品可提交 Issue，附对应原帖或目录条目。
