#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LimbusLyric v123 — non-invasive Kugou clock probe.

This tool does NOT inject into kgmusic.exe and does not read process memory.
It enumerates Win32 HWNDs and asks oleacc.dll for native MSAA/IAccessible objects,
then reports time-like text (mm:ss or hh:mm:ss) while the song is playing.

Usage:
    python CHECK_KUGOU_CLOCK_V123.py
    python CHECK_KUGOU_CLOCK_V123.py --seconds 20 --duration-ms 251000

Send the generated KUGOU_CLOCK_PROBE_*.log back with the LimbusLyric error log.
"""
import argparse
import ctypes
import datetime as _dt
import os
import re
import subprocess
import sys
import time

TIME_RE = re.compile(r'(?<!\d)(?:(\d{1,2}):)?([0-5]?\d):([0-5]\d)(?!\d)')
PAIR_RE = re.compile(r'(?<!\d)(?:(\d{1,2}):)?([0-5]?\d):([0-5]\d)\s*[/／|]\s*(?:(\d{1,2}):)?([0-5]?\d):([0-5]\d)(?!\d)')


def _time_ms(m, off=0):
    h = int(m.group(1 + off) or 0)
    minute = int(m.group(2 + off))
    sec = int(m.group(3 + off))
    return (h * 3600 + minute * 60 + sec) * 1000


def process_pids():
    out = set()
    for image in ('kgmusic.exe', 'kugou.exe'):
        try:
            text = subprocess.check_output(
                ['tasklist', '/FI', f'IMAGENAME eq {image}', '/FO', 'CSV', '/NH'],
                text=True, encoding='utf-8', errors='ignore',
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
            )
            for line in text.splitlines():
                m = re.match(r'\s*"[^"]+","(\d+)"', line)
                if m:
                    out.add(int(m.group(1)))
        except Exception:
            pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=14.0)
    ap.add_argument('--interval', type=float, default=0.70)
    ap.add_argument('--duration-ms', type=int, default=0,
                    help='Optional expected song duration; matching labels are marked MATCH_DURATION.')
    ap.add_argument('--max-nodes', type=int, default=900)
    args = ap.parse_args()

    stamp = _dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    log_path = os.path.abspath(f'KUGOU_CLOCK_PROBE_{stamp}.log')
    lines = []
    def log(msg=''):
        text = str(msg)
        lines.append(text)
        print(text, flush=True)

    log('LimbusLyric Kugou Clock Probe v123')
    log(f'python={sys.version.split()[0]} executable={sys.executable}')
    log('mode=Win32 HWND + native MSAA/IAccessible; no injection; no process-memory reads')
    log(f'duration_ms={args.duration_ms or "unknown"} seconds={args.seconds} interval={args.interval}')

    if os.name != 'nt':
        log('ERROR: This diagnostic must be run on Windows.')
        return 2

    try:
        import win32gui
        import win32process
    except Exception as exc:
        log(f'ERROR: pywin32 unavailable: {type(exc).__name__}: {exc}')
        log('Install requirements_core.txt first.')
        return 3

    try:
        import comtypes
        from comtypes.client import GetModule
        try:
            GetModule('oleacc.dll')
        except Exception as exc:
            log(f'NOTE: GetModule(oleacc.dll) returned {type(exc).__name__}: {exc}')
        from comtypes.gen.Accessibility import IAccessible
        try:
            comtypes.CoInitialize()
        except Exception:
            pass
    except Exception as exc:
        log(f'ERROR: comtypes/MSAA unavailable: {type(exc).__name__}: {exc}')
        log('Try: python -m pip install comtypes')
        return 4

    pids = process_pids()
    log(f'kugou_pids={sorted(pids)}')
    if not pids:
        log('ERROR: kgmusic.exe / kugou.exe not found. Start Kugou first.')
        return 5

    hwnd_rows = []
    seen_hwnds = set()
    def add_hwnd(hwnd):
        try:
            hwnd = int(hwnd)
            if hwnd in seen_hwnds or not win32gui.IsWindow(hwnd):
                return
            _tid, pid = win32process.GetWindowThreadProcessId(hwnd)
            if int(pid) not in pids:
                return
            seen_hwnds.add(hwnd)
            rect = tuple(int(v) for v in win32gui.GetWindowRect(hwnd))
            if rect[2] <= rect[0] or rect[3] <= rect[1]:
                return
            cls = str(win32gui.GetClassName(hwnd) or '')
            title = str(win32gui.GetWindowText(hwnd) or '')
            hwnd_rows.append((hwnd, rect, cls, title))
        except Exception:
            pass
    def top_cb(hwnd, _):
        try:
            _tid, pid = win32process.GetWindowThreadProcessId(hwnd)
            if int(pid) not in pids:
                return True
            add_hwnd(hwnd)
            try:
                win32gui.EnumChildWindows(hwnd, lambda ch, __: (add_hwnd(ch), True)[1], None)
            except Exception:
                pass
        except Exception:
            pass
        return True
    win32gui.EnumWindows(top_cb, None)
    hwnd_rows.sort(key=lambda row: max(1,row[1][2]-row[1][0]) * max(1,row[1][3]-row[1][1]), reverse=True)
    hwnd_rows = hwnd_rows[:64]
    for hwnd, rect, cls, title in hwnd_rows:
        log(f'HWND hwnd={hwnd} class={cls!r} rect={rect} title={title!r}')

    OBJID_WINDOW = 0
    OBJID_CLIENT = -4

    def acc_prop(acc, name, child_id=0):
        try:
            return getattr(acc, name)(int(child_id))
        except Exception:
            return None

    def acc_rect(acc, child_id=0):
        try:
            left, top, width, height = acc.accLocation(int(child_id))
            left=int(left); top=int(top); width=int(width); height=int(height)
            if width > 0 and height > 0:
                return left, top, left+width, top+height
        except Exception:
            pass
        return (0,0,0,0)

    last_values = {}
    seen_signatures = set()
    hit_any = False

    def one_scan(sample_no):
        nonlocal hit_any
        rows = []
        visited = set()
        node_count = 0
        roots = 0
        errors = 0

        def add_row(acc, child_id, depth, hwnd, hwnd_rect, cls):
            nonlocal node_count
            node_count += 1
            if node_count > args.max_nodes:
                return
            values=[]
            for key in ('accName','accValue','accDescription'):
                raw=acc_prop(acc,key,child_id)
                try: text=str(raw or '').strip().replace('\x00','')
                except Exception: text=''
                if text and text not in values and len(text) <= 1200:
                    values.append(text)
            if values:
                rows.append({
                    'texts': values, 'role': acc_prop(acc,'accRole',child_id),
                    'rect': acc_rect(acc,child_id), 'depth': depth,
                    'hwnd': hwnd, 'hwnd_rect': hwnd_rect, 'class': cls, 'child': child_id,
                })

        def walk(acc, depth, hwnd, hwnd_rect, cls):
            nonlocal errors
            if acc is None or depth > 8 or node_count >= args.max_nodes:
                return
            try: ident=int(ctypes.cast(acc,ctypes.c_void_p).value or 0)
            except Exception: ident=id(acc)
            if ident and ident in visited: return
            if ident: visited.add(ident)
            add_row(acc,0,depth,hwnd,hwnd_rect,cls)
            try: count=int(getattr(acc,'accChildCount',0) or 0)
            except Exception: count=0
            count=max(0,min(count,240))
            for child_id in range(1,count+1):
                if node_count >= args.max_nodes: break
                try:
                    add_row(acc,child_id,depth+1,hwnd,hwnd_rect,cls)
                    child=acc.accChild(child_id)
                    if child is not None:
                        try: child_acc=child.QueryInterface(IAccessible)
                        except Exception: child_acc=None
                        if child_acc is not None:
                            walk(child_acc,depth+1,hwnd,hwnd_rect,cls)
                except Exception:
                    errors += 1

        for hwnd, rect, cls, title in hwnd_rows:
            if node_count >= args.max_nodes: break
            for objid in (OBJID_CLIENT,OBJID_WINDOW):
                try:
                    ptr=ctypes.POINTER(IAccessible)()
                    hr=ctypes.oledll.oleacc.AccessibleObjectFromWindow(
                        ctypes.c_void_p(int(hwnd)),ctypes.c_uint32(int(objid) & 0xFFFFFFFF),
                        ctypes.byref(IAccessible._iid_),ctypes.byref(ptr))
                    if int(hr) != 0 or not ptr: continue
                    roots += 1
                    walk(ptr,0,hwnd,rect,cls)
                except Exception:
                    errors += 1

        found=[]
        for row in rows:
            for text in row['texts']:
                if not TIME_RE.search(text):
                    continue
                found.append((text,row))
        log(f'SAMPLE {sample_no:02d} roots={roots} nodes={node_count} text_nodes={len(rows)} time_nodes={len(found)} errors={errors}')
        for text,row in found[:40]:
            vals=[]
            for m in TIME_RE.finditer(text):
                vals.append(_time_ms(m))
            marks=[]
            if args.duration_ms and any(abs(v-args.duration_ms) <= max(1800,args.duration_ms*0.015) for v in vals):
                marks.append('MATCH_DURATION')
            sig=(row['hwnd'],row['child'],row['role'],row['rect'],text)
            numeric_sig=(row['hwnd'],row['child'],row['role'],row['rect'])
            prev=last_values.get(numeric_sig)
            if prev is not None and vals:
                prev_vals=prev[0]
                if prev_vals and vals[0] > prev_vals[0]: marks.append(f'ADVANCE={vals[0]-prev_vals[0]}ms')
                elif prev_vals and vals[0] == prev_vals[0]: marks.append('STATIC')
            if vals: last_values[numeric_sig]=(vals,time.monotonic())
            hit_any=True
            if sig not in seen_signatures or marks:
                seen_signatures.add(sig)
                log('  MSAA_TIME '
                    f'text={text!r} values_ms={vals} role={row["role"]} depth={row["depth"]} '
                    f'rect={row["rect"]} hwnd={row["hwnd"]} class={row["class"]!r} '
                    f'marks={",".join(marks) if marks else "-"}')
        return len(found)

    deadline=time.monotonic()+max(1.0,args.seconds)
    sample=0
    try:
        while time.monotonic() < deadline:
            sample += 1
            one_scan(sample)
            time.sleep(max(0.20,args.interval))
    finally:
        try: comtypes.CoUninitialize()
        except Exception: pass
        with open(log_path,'w',encoding='utf-8') as f:
            f.write('\n'.join(lines)+'\n')

    log('')
    if hit_any:
        log('RESULT: MSAA exposed time-like text. Check ADVANCE and MATCH_DURATION markers; this can become a real clock anchor.')
    else:
        log('RESULT: No MSAA time-like text was exposed during this run. Internal/CEF/provider bridge investigation is then the stronger next path.')
    # Save the final result lines too.
    try:
        with open(log_path,'w',encoding='utf-8') as f:
            f.write('\n'.join(lines)+'\n')
    except Exception:
        pass
    log(f'LOG: {log_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
