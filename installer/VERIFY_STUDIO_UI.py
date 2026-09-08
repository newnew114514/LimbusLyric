"""Run with the application's Python environment. Uses an isolated temporary profile."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile

def check(root, screenshots):
    sys.path.insert(0, str(root))
    main = next(root.glob('LimbusLyric*.py'))
    spec = importlib.util.spec_from_file_location('studio_app', main)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    from PyQt5.QtTest import QTest
    app = m.QApplication([])
    panel = m.ControlPanel(defer_startup_tasks=True)
    panel.setAttribute(m.Qt.WA_DontShowOnScreen, True)
    panel.resize(1060, 940)
    panel.show()
    QTest.qWait(350)
    screenshots.mkdir(parents=True, exist_ok=True)
    assert panel.front_track_label.font().pixelSize() == 27, 'Studio typography was overwritten'
    for index, name in enumerate(('playback', 'lyrics', 'motion', 'settings', 'song')):
        QTest.mouseClick(panel._sidebar_buttons[index], m.Qt.LeftButton)
        QTest.qWait(220)
        assert panel.main_tabs.currentIndex() == index
        assert panel._sidebar_buttons[index].isChecked()
        assert panel.h80_studio_stage_host.isVisible() == (index in (1, 2))
        panel.grab().save(str(screenshots / (name + '.png')))
    panel.main_tabs.setCurrentIndex(1)
    panel.h74_weight_slider.setValue(63)
    assert panel.h12_weight.value() == 63, 'Preview control lost its original binding'
    panel.h74_appearance_preview.repaint()
    panel.main_tabs.setCurrentIndex(2)
    panel.h74_motion_preview.replay()
    assert panel.h74_motion_preview._timer.isActive()
    QTest.qWait(70)
    assert panel.h74_motion_preview._progress > 0
    panel.settings_filter.setText('no-such-setting-78654321')
    QTest.qWait(220)
    assert panel.settings_empty.isVisible()
    panel.settings_filter.clear()
    QTest.qWait(220)
    assert not panel.settings_empty.isVisible()
    assert panel.h80_studio_stage_host.isVisible()
    for percent in (125, 150, 100):
        m._h12_apply_scale(panel, percent)
        QTest.qWait(120)
        assert panel.front_track_label.font().pixelSize() == round(27 * percent / 100), 'Scaling lost studio style'
        assert 'cdb47b' in panel.styleSheet()
    panel.resize(800, 760)
    QTest.qWait(150)
    assert panel.main_tabs.height() > 80, 'Compact window lost its scrollable inspector'
    assert panel.start_btn.isVisible()
    assert all(button.height() >= button.sizeHint().height() for button in panel._sidebar_buttons)
    panel.grab().save(str(screenshots / 'compact.png'))
    panel.resize(1060, 940)
    panel.main_tabs.setCurrentIndex(1)
    m._h12_apply_scale(panel, 100)
    QTest.qWait(150)
    assert panel.front_track_label.font().pixelSize() == 27
    # A loaded-title presentation fixture; no playback or provider state is fabricated.
    panel.front_track_label.setText('让每一句，都有回响。')
    panel.front_detail_label.setText('LimbusLyric · 字幕外观工作室')
    panel.h74_weight_slider.setValue(75)
    panel.grab().save(str(screenshots / 'studio-preview.png'))
    print('PASS: 5 pages, search reset, live binding, preview replay, 100/125/150% scaling, compact layout.', flush=True)

if __name__ == '__main__':
    if '--child' in sys.argv:
        try:
            check(Path(sys.argv[2]), Path(sys.argv[3]))
        except BaseException:
            import traceback
            traceback.print_exc()
            sys.stdout.flush(); sys.stderr.flush()
            os._exit(1)
        os._exit(0)  # App owns background workers; parent reclaims the isolated profile.
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    screenshots = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else root / 'studio-check-screens'
    with tempfile.TemporaryDirectory(prefix='limbus-studio-') as profile:
        env = dict(os.environ, LOCALAPPDATA=profile, QT_QPA_PLATFORM='windows')
        result = subprocess.run([sys.executable, __file__, '--child', str(root), str(screenshots)], env=env, timeout=90)
    raise SystemExit(result.returncode)

