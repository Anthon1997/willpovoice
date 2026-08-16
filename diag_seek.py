from pathlib import Path
t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=== progress_slider: creacion y conexiones ===")
for i, ln in enumerate(t.splitlines(), 1):
    if "progress_slider" in ln and ("connect" in ln or "QSlider" in ln or "setRange" in ln):
        print(f"{i}: {ln.strip()[:110]}")

for name in ["_on_slider_moved", "_on_position_changed", "_on_duration_changed"]:
    i = t.find(f"def {name}")
    if i != -1:
        j = t.find("\ndef ", i + 10)
        print(f"\n----- def {name} -----")
        print(t[i:j if j != -1 else i + 900])

print("\n=== seek en el engine/player (core) ===")
import glob
for f in glob.glob("core/*.py"):
    c = Path(f).read_text(encoding="utf-8")
    for k in ["seek", "set_position", "setPosition"]:
        if k in c:
            i = c.find(f"def {k}")
            if i != -1:
                j = c.find("\n    def ", i + 10)
                print(f"\n----- {f}: def {k} -----")
                print(c[i:j if j != -1 else i + 700])
