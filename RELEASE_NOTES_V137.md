LimbusLyric v1.8.9.137

本版本在 v1.8.9.136 基础上收口歌词首屏/逐字升级、搜索身份与封面回退，以及安装版首次附着时偶发需要再次点击“开始”的问题。

更新内容
- 修复普通歌词已经成功装载后，后续逐字增强任务取消却被误判成整首歌词失败，导致 frozen 安装版偶发隐藏歌词、需要再次点击“开始”才能继续显示的问题。
- 加强网易云歌词文本搜索的标题身份校验，避免同歌手不同歌曲被文本排名误选并污染后续歌词/封面身份。
- QQ 音乐在播放器时长尚未证明时，允许已通过同源文本与时长证据的酷狗逐字歌词提前进行“仅显示”升级；播放器 transport/seek 权威不变。
- 网易云封面搜索增加备用 GET 路径；备用结果仍经过原有标题/歌手/时长/专辑身份保护，不降低封面匹配安全门槛。
- 正式版显示版本收口为 v1.8.9.137，软件内不再使用“测试版”标识。
- 本次没有加入此前讨论的共享渲染掉帧优化，避免在发布前扩大改动范围。

验证
- 自动歌词 transition/result ownership 回放通过。
- 快速首屏 → 精确歌词热替换回放通过。
- 酷狗首次附着 / QQ seek 边沿回放通过。
- 快切 transport-generation/burst 回放通过。
- v1.8.9.136 Start/翻译状态回放通过。
- Packaging Contract 与 Release Invariants 通过。
- Windows GitHub Actions PyInstaller frozen build 与 packaging smoke test 通过。
- 最终主源码 SHA-256：e05f6e6000c6ebf845ae6dbc93cabfdc09139e99f2cdd8899395b29285acce12
- 安装包 SHA-256：b4051ce1de50ba4705ecd2cb28fd6e5dd9aa0b57453cdb35a2c148c0776b615d

说明
- 可直接覆盖安装旧版本，现有用户配置无需重建。
- Windows 10 / Windows 11，x64。
- 如遇歌词获取、自动切歌、封面或播放器兼容问题，请附播放器、歌曲、复现步骤及对应日志。

Source code
LimbusLyric 源代码以 GNU General Public License v3.0 only（GPL-3.0-only）发布。
