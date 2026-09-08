# H95F10F14 Shared Render Work Scheduler

This layer centralizes admission for speculative render work without replacing mature workers. Visible/current work is always admitted. N+1/N+2 glyph jobs and future-row Atlas prewarm yield/drop while H61, full-song Atlas, translation depth, blur material, or GUI-install backlog is active. No worker is terminated and no effect formula changes.
