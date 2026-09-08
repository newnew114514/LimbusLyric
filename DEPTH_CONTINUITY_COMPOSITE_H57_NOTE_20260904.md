# H57 — Depth Continuity + Composite Defocus Atlas

## Field evidence

A real H56 session with six visible subtitle lanes showed two presentation regressions:

1. A fixed-depth row could visibly jump when it moved from the active row into history.
   The active renderer applies `perspective -> anchor translate -> depth scale`, while the
   H54/H56 history path applied a global scale before the row's projective perspective.
   Projective transforms do not commute with that scale, so an unchanged row could move.

2. A blurred row could become sharp during its own lifetime.
   H56 intentionally stopped Defocus/Bloom when exit progress became non-zero or when render
   pressure reached the hard fallback. That changes the optical material of an already-visible
   row and is visually discontinuous.

The same field session also showed paint time rising with visible history count, because a deep
H56 row can issue Bloom + Defocus + crisp fragment batches every frame.

## H57 policy

H57 keeps H54's good model: each lyric gets one random immutable Z layer at birth.

For every depth row H57 builds one immutable *composite* Atlas:
- optional Bloom low-pass layer,
- Defocus low-pass layer,
- remaining crisp core,
all aligned around the original logical glyph anchor and baked into one glyph cell.

The composite is cached for the row and transferred to history. Runtime rendering therefore
uses one fragment batch per row/frame rather than separate Bloom/Defocus/crisp batches.

The same composite material is used for:
- the active lyric,
- held history,
- every established exit effect.

Render pressure never changes an existing row from blurred to sharp. If a composite cannot be
built within the bounded construction budget, that row stays on the sharp authoritative Atlas
for that cache key instead of changing material later.

Historical/fading rows use exactly the active-row transform order:
`perspective -> translate(anchor) -> fixed Z scale`.
The mature H51/H20 exit renderer is then invoked in that already transformed local coordinate
system, with x/y/perspective temporarily neutralized, so per-character and classic exits keep
working without double transforms.

## Boundaries

H57 is presentation-only:
- no MediaSessionSync changes,
- no provider/clock/seek changes,
- no new Python package dependency,
- no QOpenGLWidget/QML migration,
- H56 low-pass helpers remain the source of filtered glyph pixels,
- H55/H54 translated-copy haze remains retired.
