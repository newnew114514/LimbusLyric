# H95F6 · 双轨双语 / 当前播放器同步 Inspector / Modern Glass

H95F6 是 H95F5 的整合收口，不改变播放器 Transport、歌词 Provider、原始 QRC/KRC/YRC/LRC 时间戳或 Seek authority。

## 双语渲染

- 主歌词继续使用现有精准时间轴；翻译仍通过成熟 `trans_only=True` 搜索链获取，只持有行级时间证据。
- H95F5 的 post-paint secondary text 被禁用；翻译改成第二条视觉 Lane。
- 第二 Lane 复制当前行已经解析后的用户预设：字体家族、粗细/斜体、文字色、描边、阴影、发光、角度、透视/景深、随机样式结果。
- 翻译按主轨字符进度映射入场，复用 `_flow_fade_ranges` / `_flow_motion_ranges`、当前 shake 与 audio-emphasis 状态；历史翻译复用行级退场并补齐 per-char / wipe 方向退场。
- `翻译相对字号` 与 `双语间距` 只属于双语排版，不重新定义文字风格。

## UI 归位

- H95F5 的“ 双语字幕与活动区域 ”混合卡退役隐藏。
- `原歌词 + 翻译（双语）` 移到播放页原“仅显示翻译”下面；两者互斥。
- 字幕活动区域独立成卡，继续代理 H95F5 的全屏 / 上半 / 下半 / 自定义范围与安全边距。

## 同步与输出

- 四个播放器 offset 不再同时展示；只显示当前 `player_combo` 对应的一个同步微调 Inspector。
- NetEase / QQ / KuGou / Spotify 的旧 authoritative spin 和配置键保持不变，因此切换播放器后会恢复该播放器上次设置。
- `歌词输出` 仍是全局 Overlay / OBS / 捕获排除设置。
- Sync Doctor correction key 从 `song|artist` 升级为 `player::song|artist`；旧 H95 数据在第一次命中时惰性迁移到当前播放器并删除 unscoped key，避免跨播放器串修正。

## Modern Glass

- Modern Studio 标题栏改为明确的半透明深色玻璃：Classic alpha 176，Studio/forest alpha 170。
- Legacy Chrome 继续由 H95F4F3 的独立 property/QSS 管理；H95F6 只对 `h95f6ModernGlass=true` 生效。
