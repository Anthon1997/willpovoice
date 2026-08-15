from pathlib import Path

t = Path("ui/modern_window.py").read_text(encoding="utf-8")

for m in ("def _load_voices", "def _switch_page"):
    i = t.find(m)
    j = t.find("\ndef ", i + 10)
    print(f"===== {m} =====")
    print(t[i:j if j != -1 else i + 1200])
