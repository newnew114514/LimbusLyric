from __future__ import annotations

import APPLY_V136_FIELD_FIXES as patch

_original_replace_once = patch.replace_once


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    if label == 'R9.2 activation anchor' and text.count(old) == 2:
        pos = text.rfind(old)
        if pos < 0:
            raise SystemExit('V136 PATCH: R9.2 call anchor not found')
        return text[:pos] + new + text[pos + len(old):]
    return _original_replace_once(text, old, new, label)


patch.replace_once = _replace_once
patch.apply()
