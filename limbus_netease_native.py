# -*- coding: utf-8 -*-
"""Read-only NetEase CloudMusic 3.x native clock adapter for LimbusLyric.

Default NetEase path. The optional ``netease-cloudmusic-detector`` dependency reads
CloudMusic's own local state/log files. No DLL injection, no BetterNCM requirement,
no Qt dependency, and no writes to NetEase files are performed here.
"""
from __future__ import annotations

import asyncio
import math
import threading
import time

try:
    from cloudmusic_detector import AsyncCloudMusic
    NATIVE_DETECTOR_IMPORT_ERROR = ""
except Exception as exc:  # soft dependency in source/debug builds
    AsyncCloudMusic = None
    NATIVE_DETECTOR_IMPORT_ERROR = f"{type(exc).__name__}: {exc}"


class NeteaseNativeClockAdapter:
    def __init__(self):
        self.available = AsyncCloudMusic is not None
        self._cm = None
        self._start_task = None
        self._stop_task = None
        self._stopping = False
        self._start_error = ""
        self._retry_after_mono = 0.0
        self._retry_delay_sec = 30.0
        self._start_timeout_sec = 20.0
        self._stop_timeout_sec = 1.5
        self._start_state = 'idle'
        self._start_started_mono = 0.0
        self._lock = threading.Lock()
        self._track_serial = 0
        self._state_serial = 0
        self._seek_serial = 0
        self._event_serial = 0
        self._last_event_mono = 0.0
        self._loop = None
        self._event = None
        self._seek_callback_bound = False

    async def _stop_cm_bounded(self, cm):
        if cm is None:
            return True
        try:
            await asyncio.wait_for(cm.stop(), timeout=float(self._stop_timeout_sec))
            return True
        except asyncio.TimeoutError:
            return False
        except asyncio.CancelledError:
            raise
        except Exception:
            return False

    def _set_start_state(self, state, *, error=None, started_mono=None):
        self._start_state = str(state or 'idle')
        if started_mono is not None:
            self._start_started_mono = float(started_mono or 0.0)
        if error is not None:
            self._start_error = str(error or '')

    def _signal_event(self, kind):
        with self._lock:
            self._event_serial += 1
            if kind == 'track':
                self._track_serial += 1
            elif kind == 'state':
                self._state_serial += 1
            elif kind == 'seek':
                self._seek_serial += 1
            self._last_event_mono = time.monotonic() * 1000.0
            loop = self._loop
            event = self._event
        if loop is not None and event is not None:
            try:
                loop.call_soon_threadsafe(event.set)
            except Exception:
                pass

    def _on_track_change(self, *_args, **_kwargs):
        self._signal_event('track')

    def _on_state_change(self, *_args, **_kwargs):
        self._signal_event('state')

    def _on_seek(self, *_args, **_kwargs):
        # Target extraction is intentionally left to cm.state.position. The callback is only
        # a low-latency wake/serial witness, so signature changes cannot corrupt the clock.
        self._signal_event('seek')

    def start_background(self):
        if not self.available or self._stopping:
            return False
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return False
        # A full MediaSessionSync Stop destroys its worker event loop.  Never reuse an
        # asyncio.Event that was created for that retired loop on the next Start.
        with self._lock:
            bound_loop = self._loop
            active_cm = self._cm is not None
            start_active = self._start_task is not None and not self._start_task.done()
            stop_active = self._stop_task is not None and not self._stop_task.done()
            if bound_loop is not loop:
                # Rebinding while live detector tasks still belong to another loop would be
                # unsafe.  Normal full-stop clears them in stop_async() before a new worker
                # loop is created; if a caller violates that lifecycle, fail closed.
                if bound_loop is not None and (active_cm or start_active or stop_active):
                    return False
                self._loop = loop
                self._event = asyncio.Event()
            elif self._event is None:
                self._event = asyncio.Event()
        if self._stop_task is not None and not self._stop_task.done():
            return False
        if self._cm is not None:
            return True
        if self._start_task is not None and not self._start_task.done():
            return not bool(self._start_task.cancelling())
        now = time.monotonic()
        if now < float(self._retry_after_mono or 0.0):
            return False
        self._set_start_state('starting', error='', started_mono=now)
        self._start_task = loop.create_task(self._start())
        return True

    async def _start(self):
        if self._cm is not None or AsyncCloudMusic is None:
            return
        cm = None
        if self._start_state != 'starting':
            self._set_start_state('starting', error='', started_mono=time.monotonic())
        try:
            cm = AsyncCloudMusic()
            try:
                cm.on_track_change(self._on_track_change)
            except Exception:
                pass
            try:
                cm.on_state_change(self._on_state_change)
            except Exception:
                pass
            try:
                on_seek = getattr(cm, 'on_seek', None)
                if callable(on_seek):
                    on_seek(self._on_seek)
                    self._seek_callback_bound = True
            except Exception:
                self._seek_callback_bound = False
            await asyncio.wait_for(cm.start(), timeout=float(self._start_timeout_sec))
            self._cm = cm
            self._set_start_state('ready', error='', started_mono=0.0)
            self._retry_after_mono = 0.0
            self._signal_event('state')
        except asyncio.TimeoutError:
            timeout_ms = int(round(float(self._start_timeout_sec) * 1000.0))
            self._set_start_state('timeout', error=f'start-timeout:{timeout_ms}ms')
            self._retry_after_mono = time.monotonic() + float(self._retry_delay_sec)
            try:
                await self._stop_cm_bounded(cm)
            except Exception:
                pass
            self._cm = None
        except asyncio.CancelledError:
            self._set_start_state('cancelled')
            try:
                await self._stop_cm_bounded(cm)
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
            self._cm = None
            raise
        except Exception as exc:
            self._set_start_state('error', error=f"{type(exc).__name__}: {exc}")
            self._retry_after_mono = time.monotonic() + float(self._retry_delay_sec)
            try:
                await self._stop_cm_bounded(cm)
            except Exception:
                pass
            self._cm = None

    async def stop_async(self):
        self._stopping = True
        task, self._start_task = self._start_task, None
        if task is not None and not task.done():
            if not task.cancelling():
                task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass

        stop_task, self._stop_task = self._stop_task, None
        if stop_task is not None and not stop_task.done():
            try:
                await stop_task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass

        cm, self._cm = self._cm, None
        if cm is not None:
            try:
                await self._stop_cm_bounded(cm)
            except Exception:
                pass
        self._retry_after_mono = 0.0
        self._seek_callback_bound = False
        self._set_start_state('stopped', error='', started_mono=0.0)
        # Wake any waiter on the retiring loop, then sever loop-owned primitives.  The next
        # Start will create a fresh Event for its fresh worker event loop.
        with self._lock:
            event = self._event
            self._event = None
            self._loop = None
        if event is not None:
            try:
                event.set()
            except Exception:
                pass
        self._stopping = False

    def stop_background(self):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # GUI-thread stop is completed by MediaSessionSync's worker-loop stop_async().
            return False
        if self._start_task is not None and not self._start_task.done():
            # Keep ownership until cancellation cleanup completes; repeated polling must
            # not cancel that cleanup again or let a new detector overtake it.
            if not self._start_task.cancelling():
                self._start_task.cancel()
        if self._cm is None:
            return True
        if self._stop_task is None or self._stop_task.done():
            self._stop_task = loop.create_task(self._stop())
        return True

    async def _stop(self):
        cm, self._cm = self._cm, None
        if cm is None:
            self._set_start_state('stopped', error='', started_mono=0.0)
            return
        try:
            await self._stop_cm_bounded(cm)
        except Exception:
            pass
        self._seek_callback_bound = False
        self._set_start_state('stopped', error='', started_mono=0.0)
        self._signal_event('state')

    async def wait_for_event(self, timeout=0.16):
        """Wake MediaSessionSync early for track/state/seek events.

        Steady playback still uses a short timeout so ``state.position`` is sampled regularly.
        """
        try:
            timeout = max(0.03, min(0.5, float(timeout)))
        except Exception:
            timeout = 0.16
        event = self._event
        if event is None:
            await asyncio.sleep(timeout)
            return False
        if event.is_set():
            event.clear()
            return True
        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
            event.clear()
            return True
        except asyncio.TimeoutError:
            return False

    @staticmethod
    def _track_id(track):
        # Detector builds use negative/non-finite sentinels (notably -1) while the
        # local log has not resolved the real song yet. A sentinel is not identity.
        # Keep positive numeric IDs and non-empty opaque IDs for forward compatibility.
        for key in ("id", "song_id", "songId", "track_id", "trackId"):
            try:
                value = getattr(track, key, None)
            except Exception:
                value = None
            text = str(value or "").strip()
            if not text or text.casefold() in {"none", "null", "unknown", "undefined", "nan"}:
                continue
            try:
                numeric = float(text)
            except Exception:
                numeric = None
            if numeric is not None and (not math.isfinite(numeric) or numeric <= 0.0):
                continue
            return text
        return ""

    @staticmethod
    def _artist(track):
        for key in ("artist_str", "artist", "artists_str"):
            try:
                value = getattr(track, key, None)
            except Exception:
                value = None
            if value:
                return str(value)
        try:
            artists = getattr(track, "artists", None)
            if artists:
                names = []
                for item in artists:
                    name = getattr(item, "name", None) if not isinstance(item, str) else item
                    if name:
                        names.append(str(name))
                return "/".join(names)
        except Exception:
            pass
        return ""

    def snapshot(self):
        cm = self._cm
        if cm is None:
            start_state = str(self._start_state or 'idle')
            start_age_ms = 0.0
            if start_state == 'starting' and float(self._start_started_mono or 0.0) > 0.0:
                start_age_ms = max(0.0, (time.monotonic() - float(self._start_started_mono)) * 1000.0)
            return {
                "ready": False,
                "available": bool(self.available),
                "error": self._start_error or NATIVE_DETECTOR_IMPORT_ERROR,
                "start_state": start_state,
                "start_age_ms": start_age_ms,
            }
        try:
            state = cm.state
            track = getattr(state, "track", None) or getattr(cm, "track", None)
            if track is None:
                return {"ready": False, "available": True, "error": "track-unavailable", "start_state": "ready", "start_age_ms": 0.0}
            # cloudmusic_detector may transiently expose a truthy placeholder Track while
            # its local-log parser has not recovered the actual song yet. A native clock is
            # usable only after the detector owns at least one track-identity field.
            title = str(getattr(track, "name", "") or "").strip()
            track_id = self._track_id(track).strip()
            if not title and not track_id:
                return {
                    "ready": False, "available": True, "error": "track-identity-unavailable",
                    "title": "", "track_id": "", "start_state": "ready", "start_age_ms": 0.0,
                }
            position = float(getattr(state, "position", 0.0) or 0.0)
            if not math.isfinite(position) or position < 0.0:
                return {"ready": False, "available": True, "error": "invalid-position", "start_state": "ready", "start_age_ms": 0.0}
            duration = float(getattr(track, "duration", 0.0) or 0.0)
            duration_ms = duration * 1000.0 if 0.0 < duration < 10000.0 else duration
            # cloudmusic_detector normally reports seconds, but field evidence from 2.0.6
            # showed an occasional epoch/wall-clock-like value and some versions may expose
            # milliseconds. Normalize against the current track duration before publishing
            # any position/seek authority. Never let an absurd timestamp reach MediaSync.
            sec_candidate = position * 1000.0
            raw_candidate = position
            position_ms = None
            if duration_ms > 0.0 and math.isfinite(duration_ms):
                tolerance = max(5000.0, duration_ms * 0.03)
                if 0.0 <= sec_candidate <= duration_ms + tolerance:
                    position_ms = sec_candidate
                elif 0.0 <= raw_candidate <= duration_ms + tolerance:
                    position_ms = raw_candidate
            else:
                # Without duration, accept only human-scale playback positions. Seconds are
                # preferred; a large value may be an already-millisecond position.
                max_ms = 12.0 * 60.0 * 60.0 * 1000.0
                if 0.0 <= sec_candidate <= max_ms:
                    position_ms = sec_candidate
                elif 0.0 <= raw_candidate <= max_ms:
                    position_ms = raw_candidate
            if position_ms is None or not math.isfinite(position_ms):
                return {
                    "ready": False, "available": True, "error": "invalid-position-range",
                    "start_state": "ready", "start_age_ms": 0.0,
                }
            is_playing = bool(getattr(state, "is_playing", False))
            with self._lock:
                track_serial = int(self._track_serial)
                state_serial = int(self._state_serial)
                seek_serial = int(self._seek_serial)
                event_serial = int(self._event_serial)
                last_event_mono = float(self._last_event_mono)
            return {
                "ready": True,
                "available": True,
                "position_ms": position_ms,
                "duration_ms": duration_ms if duration_ms > 0.0 else None,
                "status": "playing" if is_playing else "paused",
                "title": title,
                "artist": self._artist(track),
                "track_id": track_id,
                "track_serial": track_serial,
                "state_serial": state_serial,
                "seek_serial": seek_serial,
                "event_serial": event_serial,
                "last_event_mono": last_event_mono,
                "seek_callback_bound": bool(self._seek_callback_bound),
                "start_state": "ready",
                "start_age_ms": 0.0,
            }
        except Exception as exc:
            return {
                "ready": False,
                "available": True,
                "error": f"{type(exc).__name__}: {exc}",
                "start_state": str(self._start_state or 'error'),
                "start_age_ms": 0.0,
            }
