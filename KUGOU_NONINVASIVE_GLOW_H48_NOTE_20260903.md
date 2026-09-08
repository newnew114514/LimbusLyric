# H48 KuGou noninvasive accessibility + warmup glow

Field evidence from `LimbusLyric_20260903-052119_pid3604.log`:

- packaged Windows build 26200 entered KuGou's generic accessibility wake after playback appeared (`hwnds=2`, `touched=4`);
- the selected glow color was resolved, then the renderer explicitly logged `atlas_inflight=1` and `glow/vector=skip`.

The fix is deliberately narrow:

- skip only the generic KuGou accessibility wake in packaged Windows; keep the already-exposed shallow HostV2 Range and every non-UIA clock/evidence lane;
- do not treat ordinary Atlas warmup as overload; keep the existing measured 120 ms hard-paint fuse.

Regression command:

```text
python installer/CHECK_KUGOU_NONINVASIVE_GLOW_H48_REPLAY.py <main.py> [field.log]
```
