from pathlib import Path

t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=== _tick_player actual ===")
i = t.find("def _tick_player(self):")
if i != -1:
    j = t.find("\ndef ", i + 10)
    if j == -1: j = len(t)
    print(t[i:j])
