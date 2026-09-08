# H95F4 · True Legacy Frontend

H95F3误把“旧版前端”实现成了现代 Studio 壳的紧凑布局，并把选择器放进了第 2 个设置页。H95F4纠正为真正的第二套前端壳。

## 旧版前端结构

参考用户提供的 V29/H10F4 源码最终前端行为：简单歌曲状态头 + `QTabWidget` 自身标签栏 + 设置页。旧版模式下隐藏现代唱片 Hero、LISTENING ROOM、topNav、workspaceHeader、工作区抓手和分区 rail；恢复 `播放 / 字幕 / 动效 / 高级 / 单曲DIY` 老式标签栏。

旧版模式只替换展示壳，不恢复旧播放器/歌词/封面实现。当前 QQ、网易云、酷狗、Spotify、同步医生、统一歌词模型、封面身份保护、背景磨砂和所有现有设置仍使用当前实现。

## 切换入口

H95F3误放在字幕/外观页的“前端布局”卡已隐藏退役。新版/旧版切换位于右上角“界面”弹窗的“前端版本”区域；玫瑰/森林继续作为独立配色主题。

## H95F3保留内容

H95F3的预览高度修复继续保留；只退役其“经典紧凑”用户界面模式。

## 回归

新增 `CHECK_TRUE_LEGACY_FRONTEND_H95F4_REPLAY.py`，锁定：Legacy 必须替换而非压缩现代 Hero；必须隐藏 modern topNav/workspace/grip；必须恢复 native tab bar；Studio 必须完整恢复；选择器必须位于右上角 Interface popup；H95F3 页内选择卡必须退役。
