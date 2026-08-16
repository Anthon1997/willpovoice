from pathlib import Path
t = Path("ui/modern_window.py").read_text(encoding="utf-8")

for name in ["_load_voices", "_on_combo_voice"]:
    i = t.find(f"def {name}")
    if i != -1:
        j = t.find("\ndef ", i + 10)
        print(f"----- def {name} -----")
        print(t[i:j if j != -1 else i+2000])
        print()

print("=== voice_combo: creacion y addItem ===")
for i, ln in enumerate(t.splitlines(), 1):
    if "voice_combo" in ln and ("addItem" in ln or "clear" in ln or "QComboBox" in ln or "setCurrent" in ln):
        print(f"{i}: {ln.strip()[:110]}")
