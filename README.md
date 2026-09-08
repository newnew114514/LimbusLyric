# LimbusLyric

LimbusLyric 是一款面向 Windows 的桌面歌词显示工具，重点提供多播放器适配、逐字歌词、跨来源歌词补全、桌面字幕视觉效果与可自定义的显示体验。

## 下载

正式版本请从 GitHub Releases 下载：

- https://github.com/newnew114514/LimbusLyric/releases

建议普通用户下载最新版本的 `LimbusLyric_Setup_*.exe`。

## 主要功能

- 桌面歌词显示与逐字歌词
- 多行字幕与多种入场 / 退场视觉效果
- 字体、字号范围、颜色、描边、发光、景深等显示设置
- 普通歌词与精确歌词自动获取、自动升级
- 多来源歌词补全与版本匹配
- QQ 音乐、网易云音乐、酷狗音乐、Spotify 等播放器适配
- 自定义播放器适配基础能力
- 自动检查 GitHub 最新正式版本
- OBS / 录屏相关输出与显示支持

## 系统要求

- Windows 10 / Windows 11
- 部分播放器功能依赖对应播放器自身在 Windows 上暴露的媒体信息或无障碍接口

## 从源码运行

项目当前以 Python 为主要实现语言。

核心依赖见：

- `requirements_core.txt`
- `requirements_optional_sync.txt`
- `requirements_word_timing_optional.txt`
- `requirements_audio_emphasis_optional.txt`
- `requirements_netease_native.txt`

Windows 下可参考仓库中的启动与构建脚本。发布构建入口为：

```text
BUILD_END_USER_INSTALLER.cmd
```

构建脚本会先执行项目的 release gate 检查，再生成最终安装包。

## 问题反馈

如遇到歌词获取、播放器兼容、字幕显示或其他问题，请联系：

**1826555940@qq.com**

反馈时建议附上：

- LimbusLyric 版本
- Windows 版本
- 使用的播放器
- 出现问题的歌曲
- 问题复现步骤
- 对应日志

## 支持开发

LimbusLyric 由个人持续开发和维护。软件内提供“支持开发”入口，支持完全自愿，不会解锁额外功能，也不会影响正常使用。

## 源码与发布包

源码位于本仓库；面向普通用户的安装包通过 GitHub Releases 发布。

发布包与源码是两个独立入口，请不要直接把构建缓存、日志、虚拟环境或本地用户配置提交到仓库。

## 许可证

开源许可证将在源码公开整理完成后明确标注。
