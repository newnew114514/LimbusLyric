# LimbusLyric

LimbusLyric 是一款面向 Windows 的桌面歌词显示工具，重点提供多播放器适配、逐字歌词、跨来源歌词补全、桌面字幕视觉效果与可自定义的显示体验。

## 下载

正式版本请从 GitHub Releases 下载：

- https://github.com/newnew114514/LimbusLyric/releases

当前公开版本：**v1.8.9.134**。

普通用户建议下载最新版本的 `LimbusLyric_Setup_*.exe`。

## 主要功能

- 桌面歌词显示与逐字歌词
- 多行字幕以及多种入场 / 退场视觉效果
- 字体、字号范围、颜色、描边、发光、景深等显示设置
- 普通歌词与精确歌词自动获取、自动升级
- 多来源歌词补全与版本匹配
- QQ 音乐、网易云音乐、酷狗音乐、Spotify 等播放器适配
- 自定义播放器适配基础能力
- 自动检查 GitHub 最新正式版本
- OBS / 录屏相关输出与显示支持

## 系统要求

- Windows 10 / Windows 11
- Python 3.12 推荐用于源码运行与发布构建
- 部分播放器能力依赖播放器自身在 Windows 上暴露的媒体信息、UI Automation 或相关系统接口

## 从源码运行

安装基础依赖：

```text
python -m pip install -r requirements_core.txt
```

然后运行：

```text
LimbusLyric_START.cmd
```

也可以直接运行主 Python 文件：

```text
python LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py
```

可选功能依赖见：

- `requirements_optional_sync.txt`
- `requirements_word_timing_optional.txt`
- `requirements_audio_emphasis_optional.txt`
- `requirements_netease_native.txt`

## 发布构建

发布工程包含 release gate、PyInstaller 与安装器构建脚本。GitHub 仓库额外包含 `README.md`、`LICENSE`、`.gitignore` 等仓库元数据，因此首次从 GitHub checkout 做发布构建前，请先重新生成源码清单：

```text
python installer/PREPARE_SOURCE_MANIFEST.py .
```

随后运行：

```text
BUILD_END_USER_INSTALLER.cmd
```

普通源码运行不需要执行这一步。

## 问题反馈

如遇到歌词获取、播放器兼容、字幕显示或其他问题，请联系：

**1826555940@qq.com**

反馈时建议附上 LimbusLyric 版本、Windows 版本、播放器、问题歌曲、复现步骤以及对应日志。

## 支持开发

LimbusLyric 由个人持续开发和维护。软件内提供“支持开发”入口，支持完全自愿，不会解锁额外功能，也不会影响正常使用。

## 第三方内容

部分界面图形设计参考了 Tabler Icons，相关说明见 `THIRD_PARTY_UI_ICONS_H73.md`。第三方库及其许可证仍分别遵循各自上游许可条款。

## License

LimbusLyric 源代码以 **GNU General Public License v3.0** 发布。完整条款见 [`LICENSE`](LICENSE)。

SPDX: `GPL-3.0-only`
