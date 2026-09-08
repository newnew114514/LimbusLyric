# H64 — Capacity-Aware Blur Decay

Field H63 log `20260904-172810` showed that the user changed visible subtitle capacity to 6 and the runtime correctly reported `visible_stack=6 / fade_lane=6`, yet dense playback repeatedly topped out at five live rows. The reason was not capacity enforcement: H62's independent history-age blur clock retired the oldest history row at `age-blur-invisible` just before the sixth row arrived.

H64 changes only `blur_decay` residency semantics. During active lyric flow, the configured visible subtitle count becomes a soft fill target: age-defocus speed scales with current live fill and natural age retirement is parked below invisibility. Capacity overflow remains the authority that moves the oldest row into the normal fading/release lane. During provider-idle/instrumental gaps (`full_text` blank), H64 steps aside and the original H62 natural age dissolve remains active.

This does not make the slider a hard minimum. Sparse songs, pauses, seeks, track changes and idle gaps do not fabricate rows. It only prevents blur-decay from deleting available history one line before the user's requested stack can fill.
