from __future__ import annotations

import ast
import copy
import sys
import textwrap
from pathlib import Path


if len(sys.argv) != 2:
    raise SystemExit("usage: CHECK_RC_AUDIT_CLOSURE_REPLAY.py <main.py>")

main_path = Path(sys.argv[1])
source = main_path.read_text(encoding="utf-8")
tree = ast.parse(source, filename=str(main_path))


def method(class_name: str, name: str) -> str:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == name:
                    return ast.get_source_segment(source, child)
    raise AssertionError(f"missing {class_name}.{name}")


def replay_class(name: str, methods: list[str], globals_dict=None):
    namespace = dict(globals_dict or {})
    body = "class %s:\n%s" % (
        name,
        "\n".join(textwrap.indent(method("ControlPanel", item), "    ") for item in methods),
    )
    exec(body, namespace)
    return namespace[name]


class Combo:
    def __init__(self, text="", data=None):
        self.text = text
        self.data = data
        self.index = 0
        self.items = {"all": 0, "qq": 1, "netease": 2, "kugou": 3}

    def currentText(self):
        return self.text

    def currentData(self):
        return self.data

    def findData(self, value):
        return self.items.get(value, -1)

    def setCurrentIndex(self, value):
        self.index = int(value)
        self.data = {0: "all", 1: "qq", 2: "netease", 3: "kugou"}.get(self.index)

    def blockSignals(self, _blocked):
        return None


Panel = replay_class(
    "ReplayPanel",
    [
        "_song_style_scope_key",
        "_track_identity",
        "_same_track",
        "_song_style_identity_for_track",
        "_diy_payload_for_scope",
        "_diy_row_mode",
        "_diy_preferred_individual_scope",
        "_diy_set_combo_scope",
        "_ensure_diy_per_source_slots",
        "_apply_song_style_for_track",
        "_record_loaded_track",
        "_diy_edit_scope",
        "_save_current_song_style",
        "_quick_edit_song_font",
    ],
    {
        "write_error_log": lambda *args, **kwargs: None,
        "_clean_name": lambda value: str(value or "").strip().lower(),
        "EVIDENCE_CLOCK_ENABLED": False,
    },
)
Panel._song_style_scope_key = staticmethod(Panel._song_style_scope_key)
Panel._track_identity = staticmethod(Panel._track_identity)
Panel._same_track = staticmethod(Panel._same_track)


def make_panel(player: str, lyric_source: str):
    panel = Panel()
    panel.player_combo = Combo(player)
    panel.source_combo = Combo(lyric_source)
    panel.diy_scope_combo = Combo(data="qq")
    panel.song_styles = {
        "song|artist": {
            "song": "song",
            "artist": "artist",
            "mode": "per_player",
            "rules": {
                "qq": {"slot": "qq"},
                "netease": {"slot": "netease"},
                "kugou": {"slot": "kugou"},
            },
        }
    }
    panel._ensure_random_style_for_track = lambda *_args: {"slot": "random"}
    panel._refresh_song_style_list = lambda *_args: None
    panel._select_song_style_item = lambda *_args: None
    panel._schedule_config_save = lambda *_args: None
    panel._launch_current_lyrics = lambda *_args, **_kwargs: None
    panel._song_style_payload_from_diy = lambda: {"slot": "modified"}
    panel._is_started = False
    panel.status = type("Status", (), {"setText": lambda self, _text: None})()
    return panel


matrix = (
    ("QQ音乐", "网易云", "qq"),
    ("网易云音乐", "酷狗", "netease"),
    ("酷狗", "QQ音乐", "kugou"),
)
for player, lyric_source, expected_scope in matrix:
    panel = make_panel(player, lyric_source)
    panel._record_loaded_track("song", "artist", lyric_source)
    assert panel._loaded_source == lyric_source, (player, lyric_source, panel._loaded_source)
    assert panel._loaded_player == player, (player, lyric_source, panel._loaded_player)
    assert panel._active_song_style["slot"] == expected_scope, (player, lyric_source, panel._active_song_style)
    assert panel.diy_scope_combo.currentData() == expected_scope, (player, panel.diy_scope_combo.currentData())

    # Modify/save only the actual player's slot, then reconstruct the panel and reload it.
    before = copy.deepcopy(panel.song_styles["song|artist"]["rules"])
    panel._save_current_song_style()
    after = panel.song_styles["song|artist"]["rules"]
    assert after[expected_scope] == {"slot": "modified"}
    for other in {"qq", "netease", "kugou"} - {expected_scope}:
        assert after[other] == before[other], (player, other, before[other], after[other])
    reloaded = make_panel(player, lyric_source)
    reloaded.song_styles = copy.deepcopy(panel.song_styles)
    reloaded._record_loaded_track("song", "artist", lyric_source)
    assert reloaded._active_song_style == {"slot": "modified"}


# Schema-v5 runtime: ALL is first-class only when the row mode is ALL.
assert Panel._song_style_scope_key("unknown-player") == ""
for player, _source, scope in matrix:
    panel = make_panel(player, "QQ音乐")
    panel.song_styles = {"song|artist": {"mode": "all", "rules": {"all": {"slot": "unified"}, scope: {"slot": "individual"}}}}
    assert panel._diy_payload_for_scope(panel.song_styles["song|artist"], "all") == {"slot": "unified"}
    assert panel._apply_song_style_for_track("song", "artist", player) == {"slot": "unified"}
    panel.song_styles["song|artist"]["mode"] = "per_player"
    assert panel._apply_song_style_for_track("song", "artist", player) == {"slot": "individual"}


# Font secondary editing must remain a cancel-safe transaction.  The V29 maintenance
# dialog now edits family + bold + italic together, so verify no rules mutation occurs
# before QDialog acceptance rather than replaying the old single-family picker.
font_edit = method("ControlPanel", "_quick_edit_song_font")
font_gate = font_edit.index("if dlg.exec_() != QDialog.Accepted")
font_commit = font_edit.index("row.setdefault('rules'", font_gate)
assert "row.setdefault('rules'" not in font_edit[:font_gate]
assert font_commit > font_gate
for token in ("QFontComboBox", "QCheckBox('粗体'", "QCheckBox('斜体'", "style['font_bold']", "style['font_italic']"):
    assert token in font_edit, token
assert '恢复全局字体' not in font_edit

# The color/effect dialog must not attach an empty rules dict before acceptance.
appearance = method("ControlPanel", "_quick_edit_song_appearance")
dialog_gate = appearance.index("if dlg.exec_() != QDialog.Accepted")
commit = appearance.index("row.setdefault('rules'", dialog_gate)
assert "row.setdefault('rules'" not in appearance[:dialog_gate]
assert commit > dialog_gate


# Execute the real geometry restoration method against deterministic screen geometries.
class Rect:
    def __init__(self, left, top, width, height):
        self._left = int(left)
        self._top = int(top)
        self._width = int(width)
        self._height = int(height)

    def left(self): return self._left
    def top(self): return self._top
    def width(self): return self._width
    def height(self): return self._height
    def right(self): return self._left + self._width - 1
    def bottom(self): return self._top + self._height - 1


class Screen:
    def __init__(self, rect): self.rect = rect
    def availableGeometry(self): return self.rect


class FakeApplication:
    current = []

    @classmethod
    def screens(cls): return list(cls.current)

    @classmethod
    def primaryScreen(cls): return cls.current[0]


GeometryPanel = replay_class(
    "GeometryPanel",
    ["_restore_window_geometry"],
    {"QApplication": FakeApplication},
)


def geometry_case(screens, settings, expected_screen, exact_xy=None):
    FakeApplication.current = [Screen(Rect(*rect)) for rect in screens]
    panel = GeometryPanel()
    panel.minimumWidth = lambda: 240
    panel.minimumHeight = lambda: 180
    panel.resize = lambda w, h: setattr(panel, "size", (int(w), int(h)))
    panel.move = lambda x, y: setattr(panel, "position", (int(x), int(y)))
    assert panel._restore_window_geometry(dict(settings)) is True
    x, y = panel.position
    w, h = panel.size
    er = Rect(*expected_screen)
    assert er.left() <= x <= er.right() - w + 1, (panel.position, panel.size, expected_screen)
    assert er.top() <= y <= er.bottom() - h + 1, (panel.position, panel.size, expected_screen)
    if exact_xy is not None:
        assert panel.position == exact_xy, (panel.position, exact_xy)


primary = (0, 0, 1920, 1080)
geometry_case([primary], {"panel_x": 200, "panel_y": 160, "panel_width": 800, "panel_height": 600}, primary, (200, 160))
secondary = (1920, 0, 1600, 900)
geometry_case([primary, secondary], {"panel_x": 2100, "panel_y": 120, "panel_width": 900, "panel_height": 650}, secondary, (2100, 120))
negative_x = (-1280, 0, 1280, 1024)
geometry_case([primary, negative_x], {"panel_x": -1100, "panel_y": 100, "panel_width": 800, "panel_height": 600}, negative_x, (-1100, 100))
negative_y = (0, -1200, 1600, 1200)
geometry_case([primary, negative_y], {"panel_x": 200, "panel_y": -1050, "panel_width": 800, "panel_height": 700}, negative_y, (200, -1050))
portrait = (1920, 0, 1080, 1920)
geometry_case([primary, portrait], {"panel_x": 2050, "panel_y": 400, "panel_width": 800, "panel_height": 1000}, portrait, (2050, 400))
geometry_case([primary], {"panel_x": 4200, "panel_y": 300, "panel_width": 900, "panel_height": 700}, primary)


# QQ transport identity is already checked; lyric provider must not block cache restoration.
RestorePanel = replay_class(
    "RestorePanel",
    ["_restore_qq_suspended_loaded_track"],
    {"write_error_log": lambda *args, **kwargs: None},
)
for lyric_source in ("网易云", "酷狗"):
    panel = RestorePanel()
    panel._auto_overlay_suspended = True
    panel.player_combo = Combo("QQ音乐")
    panel._loaded_source = lyric_source
    panel._loaded_song = "old song"
    panel._loaded_artist = "artist"
    panel._same_track = lambda *args: True
    panel.text_input = type("Text", (), {"toPlainText": lambda self: "[00:00.00]cached"})()
    panel.lyric_window = type("Lyric", (), {"song_duration": 219000})()
    binds = []
    panel.media_sync = type("Sync", (), {"bind_track": lambda self, *args: binds.append(args)})()
    launches = []
    panel._launch_current_lyrics = lambda **kwargs: launches.append(kwargs)
    panel.status = type("Status", (), {"setText": lambda self, _text: None})()
    assert panel._restore_qq_suspended_loaded_track("old song", "artist") is True
    assert binds and launches

print("RC AUDIT CLOSURE REPLAY: PASS")
print("  player/lyric-source matrix read-modify-save-reload: PASS")
print("  schema-v5 ALL/per-player runtime selection: PASS")
print("  font + appearance cancel transactions: PASS")
print("  primary/secondary/negative-X/negative-Y/portrait/removed-screen geometry: PASS")
print("  QQ cross-source suspended transaction restore: PASS")
