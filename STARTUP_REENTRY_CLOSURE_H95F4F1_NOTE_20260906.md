# H95F4F1 · Startup Re-entry Closure

H95F4 introduced a real second frontend shell, but its startup applicator reused H95F3's Studio restoration helper after H95F4 had already wrapped the global H95F1 density hook. During `ControlPanel` construction this could synchronously recurse on the Qt GUI thread:

`H95F4 apply frontend -> H95F3 Studio apply -> global H95F1 density -> H95F4 density wrapper -> H95F4 apply frontend`.

Because panel construction happens while the startup card is stationary and before the reveal callback, the GUI event loop could not advance far enough to finish the startup animation. The visible symptom was `[8/8] Starting CURRENT build...` followed by an indefinitely displayed splash card.

H95F4F1 adds an exception-safe re-entry guard around the existing H95F4 frontend applicator. Nested density/theme reconciliation is coalesced into the outer shell transaction; no playback, lyric, cover, Spotify, sync-doctor, or frontend visual contract is changed.

A canonical replay executes the real guard function with a synthetic nested H95F4/H95F3 density call and verifies the underlying applicator is called exactly once and the guard is cleared on both normal and exceptional exits.
