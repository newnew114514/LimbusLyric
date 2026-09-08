# H95F4F3 · 页面内预览 + 经典标题栏材质隔离

- 字幕（外观）与动效预览从 H80 的 `settings_shell` 顶层舞台移回各自标签页内容区第一行。展开/收起只改变当前页内容高度，不再推动原生 TabBar / Studio 导航位置。
- 退役旧 `h80StudioStageHost` 的可见高度，但保留原预览控件与渲染逻辑。
- 修复 H95F4F2 动态祖先选择器在 Qt 中可能缓存的问题：经典/现代切换时不再只改变父级 `h95f4Frontend` 属性，而是对标题栏、标题文字、窗口按钮、Panel 内容、Legacy Header、QTabWidget/TabBar 分别设置 `h95f4LegacyChrome` 并逐个 repolish。
- 经典前端窗口按钮恢复 V29 的功能性边界：`rgba(5,6,9,196)` 底、1px 亮边、5px 圆角；最小化/最大化 hover 灰化，关闭 hover 为 `#7c2e3b`。
- 经典标题栏恢复 V29 半透明顶栏语言；现代 Studio 不命中新材质选择器，继续使用当前现代样式。
- 仅展示层改动；播放器、歌词、同步医生、封面、Spotify、Seek 与打包逻辑不变。
