# H77 Application Shell + Inspector System

H77 is a presentation-only productization layer on top of the H76 runtime checkpoint. It does not own player transport, provider selection, seek, lyric timing, desktop exit lifecycles, Atlas material, or fade/blur progress.

## Why this layer exists

H73-H76 improved navigation, preview, motion and visual restraint, but the control panel still read primarily as a polished settings utility. The remaining issue was structural: current song context was visually subordinate to application chrome, while most parameters still used the classic label+widget form language.

H77 changes the application shell rather than adding decorative animation.

## Interface utility

The title-bar utility is now `界面` instead of `背景`. It owns two control-panel-only concerns:

- interface scale: 100 / 110 / 125 / 150 percent, proxied to the mature H12 scale owner;
- custom panel background: enable, image selection, strength and clear, proxied to the existing background owners.

The H75 `应用界面` card and the legacy `界面背景` card stay alive only as hidden compatibility/config owners and are excluded from global settings search. No setting key is migrated or duplicated.

## Now Playing shell

The existing Hero is restyled rather than replaced. Existing `front_track_label`, `front_detail_label` and sync badge remain the only state sources. The track title becomes the visual primary; application branding and `NOW PLAYING` are quiet eyebrow information.

No new polling or media-state observer is introduced.

## Inspector grammar

H77 does not rebuild mature controls. It normalizes existing setting-row layouts in place:

- consistent vertical padding and spacing;
- semantic inspector labels and compact value labels;
- hairline separators between real parameter rows;
- low-contrast combo/spin/edit surfaces;
- slimmer slider track and handle language.

This keeps every original widget, signal and config owner intact while reducing the visual feeling of a traditional Qt form.

## Editorial page hierarchy

Each workspace header receives a quiet English kicker (`PLAYBACK`, `APPEARANCE`, `MOTION`, `SYSTEM`, `SONG OVERRIDE`) above the existing Chinese page title/description. This is presentation only and does not change the stable tab indices.

## Motion policy

H77 adds no new general animation system. It reuses H76's 165ms page settle and 180ms flyout motion for the new Interface popup. No looped/decorative animation is added.

## Open-source design review

H77 was informed by public design patterns in Zed, Penpot, Microsoft Fluent UI and GitHub Desktop: strong workspace/context hierarchy, inspector-style controls, centralized appearance settings, tokenized/restrained motion. No third-party implementation code, SVG runtime, icon font, UI framework or new dependency is imported.

## Compatibility boundary

- H76 replay is scope-capped at the H77 marker only; H76 runtime behavior is unchanged.
- H77 must not reference MediaSessionSync, LyricSearchEngine, FadingLine, fading_lines, begin_fade, seek authority, QImage filtering, worker threads or provider implementations.
- Existing H12 background/scale owners remain authoritative.
