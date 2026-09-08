# Runtime UX + Core R2.3.1

Field hotfix for the missing Studio preview entry introduced in R2.3.

Root cause: H78 prepends `h78WorkspaceMark` to `workspaceHeader`, so the workspace title column is no longer guaranteed to be `workspace_header.layout().itemAt(0).layout()`. R2.3 assumed index 0 and returned without creating the title-adjacent Preview button.

Fix: locate the nested header layout that actually owns `workspace_title`, then insert the Preview toggle beside the title. No preview renderer, page ordering, player clock, lyric provider, renderer, or historical wrapper topology is changed.
