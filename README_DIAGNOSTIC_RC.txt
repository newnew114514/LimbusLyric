LimbusLyric RC11 — QQ 同名/近似同名版本切换专项
2026-08-15

复测重点：
- 在 QQ 音乐两个“少女A”版本之间来回切。
- 旧版本的 242 秒时间轴不得在新 221 秒版本刚开始时重新接管。
- 日志若检测到 duration mismatch，应先有 qq-track-switch-hint；
  新元数据绑定时可见“QQ切歌隔离跨绑定保留”。
- 隔离期间若旧 GSMTC fallback 仍可读，应出现 mode=qq-track-switch-fallback-hold，
  但歌词公开位置继续走新曲目的 auto-local，不应跳回旧曲目的一百多秒。
- 快速再切到下一首时，如果旧 QQ 歌词网络结果回来但 duration 已与当前 transport 不符，
  应出现“QQ自动歌词结果时长身份冲突丢弃”。

其它播放器：
- 酷狗保持旧工作版逻辑，不要为了本轮 QQ 测试改它。
- 网易云保持 Native detector 默认路径。

日志：LimbusLyric.exe 同目录\logs
