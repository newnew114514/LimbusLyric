from pathlib import Path

p = Path(__file__).with_name('APPLY_V136_FIELD_FIXES.py')
s = p.read_text(encoding='utf-8')
old = "    text = replace_once(text, activation, activation + block, 'R9.2 activation anchor')"
new = """    idx = text.rfind(activation)
    if idx < 0:
        raise SystemExit('V136 PATCH: R9.2 activation call missing')
    text = text[:idx] + activation + block + text[idx + len(activation):]"""
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('V136 PATCHER ANCHOR FIX: expected patch line missing')
p.write_text(s, encoding='utf-8', newline='\n')
print('V136 PATCHER ANCHOR FIX: PASS')
