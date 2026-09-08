"""Local lyric-file normalization with no Qt/network dependencies.

Outputs the host's Enhanced-LRC form so the mature renderer can consume local LRC,
YRC, QRC, KRC, WebVTT and TTML without adding another runtime data path.
"""
from __future__ import annotations

import base64
import html
import re
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

_KRC_KEY = bytes([
    0x40, 0x47, 0x61, 0x77, 0x5E, 0x32, 0x74, 0x47,
    0x51, 0x36, 0x31, 0x2D, 0xCE, 0xD2, 0x6E, 0x69,
])
_YRC_LINE_RE = re.compile(r"^\s*\[(\d+)\s*,\s*(\d+)\s*\](.*)$")
_YRC_WORD_RE = re.compile(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)(.*?)(?=\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)|$)")
_KRC_LINE_RE = re.compile(r"^\[(\d+)\s*,\s*(\d+)\](.*)$")
_KRC_WORD_RE = re.compile(r"<(\d+)\s*,\s*(\d+)\s*,\s*[^>]*>([^<]*)")
_QRC_WORD_MARK_RE = re.compile(r"\(\s*(\d+)\s*,\s*(\d+)\s*\)")
_VTT_CUE_RE = re.compile(r"^\s*((?:\d{1,2}:)?\d{1,2}:\d{2}(?:\.\d{1,3})?)\s*-->\s*((?:\d{1,2}:)?\d{1,2}:\d{2}(?:\.\d{1,3})?)")
_VTT_INLINE_RE = re.compile(r"<(\d{1,2}:\d{2}(?:\.\d{1,3})?|\d{1,2}:\d{2}:\d{2}(?:\.\d{1,3})?)>")


def _fmt(ms: int) -> str:
    ms = max(0, int(ms))
    minute, rem = divmod(ms, 60000)
    second, milli = divmod(rem, 1000)
    return f"{minute:02d}:{second:02d}.{milli:03d}"


def _clock_ms(value: str):
    s = str(value or "").strip()
    if not s:
        return None
    try:
        if s.endswith("ms"):
            return max(0, int(round(float(s[:-2]))))
        if s.endswith("s"):
            return max(0, int(round(float(s[:-1]) * 1000.0)))
        parts = s.replace(",", ".").split(":")
        if len(parts) == 3:
            h, m, sec = int(parts[0]), int(parts[1]), float(parts[2])
        elif len(parts) == 2:
            h, m, sec = 0, int(parts[0]), float(parts[1])
        else:
            return None
        return max(0, int(round((h * 3600 + m * 60 + sec) * 1000.0)))
    except Exception:
        return None


def _decode_text(data: bytes) -> str:
    if data.startswith(b"\xef\xbb\xbf"):
        return data.decode("utf-8-sig", errors="replace")
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16", errors="replace")
    for enc in ("utf-8", "gb18030", "utf-16-le", "utf-16-be"):
        try:
            text = data.decode(enc)
            if text.count("\x00") <= max(2, len(text) // 30):
                return text
        except Exception:
            pass
    return data.decode("utf-8", errors="replace")


def _decode_krc_blob(data: bytes) -> str:
    if not data.startswith(b"krc1"):
        return _decode_text(data)
    dec = bytes(b ^ _KRC_KEY[i % len(_KRC_KEY)] for i, b in enumerate(data[4:]))
    return zlib.decompress(dec).decode("utf-8", errors="replace")


def _strip_control(text: str) -> str:
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", html.unescape(str(text or "")))


def _yrc(text: str) -> str:
    out = []
    for raw in str(text or "").replace("\r", "").split("\n"):
        m = _YRC_LINE_RE.match(raw.strip("\ufeff "))
        if not m:
            continue
        line_start = int(m.group(1)); parts = []
        for wm in _YRC_WORD_RE.finditer(m.group(3) or ""):
            start = int(wm.group(1)); dur = max(0, int(wm.group(2))); token = _strip_control(wm.group(4))
            if token:
                parts.append(f"<{_fmt(start)}>{token}<{_fmt(start + dur)}>")
        if parts:
            out.append(f"[{_fmt(line_start)}]" + "".join(parts))
    return "\n".join(out).strip()


def _krc(text: str) -> str:
    out = []
    for raw in str(text or "").replace("\r", "").split("\n"):
        m = _KRC_LINE_RE.match(raw.strip("\ufeff "))
        if not m:
            continue
        line_start = int(m.group(1)); parts = []
        for wm in _KRC_WORD_RE.finditer(m.group(3) or ""):
            rel = max(0, int(wm.group(1))); dur = max(0, int(wm.group(2))); token = _strip_control(wm.group(3))
            if token:
                start = line_start + rel
                parts.append(f"<{_fmt(start)}>{token}<{_fmt(start + dur)}>")
        if parts:
            out.append(f"[{_fmt(line_start)}]" + "".join(parts))
    return "\n".join(out).strip()


def _extract_qrc(text: str) -> str:
    raw = str(text or "").lstrip("\ufeff").strip()
    if "LyricContent=" in raw:
        m = re.search(r"<Lyric_1\b[^>]*\bLyricContent\s*=\s*([\"'])(.*?)\1", raw, re.S | re.I)
        if not m:
            return ""
        raw = html.unescape(m.group(2) or "").replace("&#xA;", "\n").replace("&#10;", "\n")
    out = []
    for row in raw.replace("\r", "").split("\n"):
        m = _YRC_LINE_RE.match(row.strip("\ufeff "))
        if not m:
            continue
        line_start = int(m.group(1)); body = m.group(3) or ""; cursor = 0; parts = []
        for wm in _QRC_WORD_MARK_RE.finditer(body):
            token = _strip_control(body[cursor:wm.start()]); cursor = wm.end()
            if token:
                start = max(0, int(wm.group(1))); dur = max(0, int(wm.group(2)))
                parts.append(f"<{_fmt(start)}>{token}<{_fmt(start + dur)}>")
        if parts:
            out.append(f"[{_fmt(line_start)}]" + "".join(parts))
    return "\n".join(out).strip()


def _vtt(text: str) -> str:
    rows = str(text or "").replace("\r", "").split("\n")
    out = []; i = 0
    while i < len(rows):
        m = _VTT_CUE_RE.match(rows[i])
        if not m:
            i += 1; continue
        start = _clock_ms(m.group(1)); end = _clock_ms(m.group(2)); i += 1
        body = []
        while i < len(rows) and rows[i].strip():
            body.append(rows[i].strip()); i += 1
        raw = " ".join(body).strip()
        raw = re.sub(r"</?c(?:\.[^>]*)?>", "", raw)
        if start is None or not raw:
            continue
        inline = list(_VTT_INLINE_RE.finditer(raw))
        if inline:
            plain_parts = []; parts = []; cursor = 0; active = start
            for mark in inline:
                segment = _strip_control(re.sub(r"<[^>]+>", "", raw[cursor:mark.start()]))
                if segment:
                    parts.append(f"<{_fmt(active)}>{segment}")
                active = _clock_ms(mark.group(1)) or active
                cursor = mark.end()
            segment = _strip_control(re.sub(r"<[^>]+>", "", raw[cursor:]))
            if segment:
                parts.append(f"<{_fmt(active)}>{segment}")
            if end is not None and parts:
                parts.append(f"<{_fmt(end)}>")
            plain = "".join(parts)
            if plain:
                out.append(f"[{_fmt(start)}]{plain}")
        else:
            clean = _strip_control(re.sub(r"<[^>]+>", "", raw)).strip()
            if clean:
                out.append(f"[{_fmt(start)}]{clean}")
    return "\n".join(out).strip()


def _local_name(tag: str) -> str:
    return str(tag or "").split("}")[-1].lower()


def _ttml(text: str) -> str:
    try:
        root = ET.fromstring(str(text or ""))
    except Exception:
        return ""
    out = []
    for p in root.iter():
        if _local_name(p.tag) != "p":
            continue
        start = _clock_ms(p.attrib.get("begin", "")); end = _clock_ms(p.attrib.get("end", ""))
        if start is None:
            continue
        # Prefer leaf timed spans anywhere below <p>.  Apple-Music-like TTML and other
        # exporters may wrap timed spans in styling/role containers; limiting this to direct
        # children silently loses their word timing.  Leaf selection avoids duplicating text
        # from a timed parent and its timed children.
        timed_desc = []
        for node in p.iter():
            if node is p or _local_name(node.tag) not in {"span", "ruby", "rb"}:
                continue
            if not (node.attrib.get("begin") or node.attrib.get("end")):
                continue
            has_timed_child = any(
                child is not node
                and _local_name(child.tag) in {"span", "ruby", "rb"}
                and (child.attrib.get("begin") or child.attrib.get("end"))
                for child in node.iter()
            )
            if not has_timed_child:
                timed_desc.append(node)
        parts = []
        if timed_desc:
            for span in timed_desc:
                # Preserve intentional spaces between English words.  Only use strip() to
                # decide emptiness; removing the whitespace itself would glue tokens together.
                token = _strip_control("".join(span.itertext()))
                if not token.strip():
                    continue
                s = _clock_ms(span.attrib.get("begin", "")); e = _clock_ms(span.attrib.get("end", ""))
                if s is None:
                    s = start
                parts.append(f"<{_fmt(s)}>{token}")
                if e is not None:
                    parts.append(f"<{_fmt(e)}>")
        else:
            token = _strip_control("".join(p.itertext())).strip()
            if token:
                parts.append(token)
        if parts:
            if end is not None and not any(part == f"<{_fmt(end)}>" for part in parts[-2:]):
                # End marker is harmless for line-only TTML and useful for precise spans.
                if any(part.startswith("<") for part in parts):
                    parts.append(f"<{_fmt(end)}>")
            out.append(f"[{_fmt(start)}]" + "".join(parts))
    return "\n".join(out).strip()


def normalize_local_lyric_bytes(data: bytes, filename: str = ""):
    name = str(filename or "")
    ext = Path(name).suffix.lower()
    if ext == ".krc" and bytes(data or b"").startswith(b"krc1"):
        raw = _decode_krc_blob(bytes(data or b"")); fmt = "krc"
    else:
        raw = _decode_text(bytes(data or b"")); fmt = ext.lstrip(".") or "text"
    probe = raw.lstrip("\ufeff \t\r\n")
    if not ext:
        if probe.startswith("WEBVTT"): fmt = "vtt"
        elif probe.startswith("<") and ("<tt" in probe[:500] or ":tt" in probe[:500]): fmt = "ttml"
        elif "<Lyric_1" in probe or "LyricContent=" in probe: fmt = "qrc"
        elif _KRC_LINE_RE.search(probe): fmt = "krc"
        elif _YRC_LINE_RE.search(probe) and _YRC_WORD_RE.search(probe): fmt = "yrc"
    precise = False
    normalized = ""
    if fmt in {"yrc"}:
        normalized = _yrc(raw); precise = bool(normalized)
    elif fmt in {"krc"}:
        normalized = _krc(raw); precise = bool(normalized)
    elif fmt in {"qrc"}:
        normalized = _extract_qrc(raw); precise = bool(normalized)
    elif fmt in {"vtt", "webvtt"}:
        normalized = _vtt(raw); precise = bool(re.search(r"<\d{1,3}:\d{2}\.\d{3}>", normalized))
    elif fmt in {"ttml", "xml"}:
        normalized = _ttml(raw); precise = bool(re.search(r"<\d{1,3}:\d{2}\.\d{3}>", normalized))
    else:
        normalized = raw.strip(); fmt = fmt if fmt not in {"text", "txt"} else "lrc"
        precise = bool(re.search(r"<\s*\d{1,3}:\d{1,2}(?:\.\d{1,3})?\s*>", normalized))
    if not normalized.strip():
        raise ValueError(f"无法从 {fmt or 'unknown'} 文件解析出歌词")
    return {
        "text": normalized.strip(),
        "format": fmt,
        "precise": bool(precise),
        "source_name": Path(name).name if name else "",
        "bytes": len(data or b""),
    }


def normalize_local_lyric_file(path):
    p = Path(path)
    data = p.read_bytes()
    return normalize_local_lyric_bytes(data, p.name)
