from pathlib import Path

t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=== _player_play_clicked actual ===")
i = t.find("def _player_play_clicked(self):")
if i != -1:
    j = t.find("\ndef ", i + 10)
    if j == -1: j = len(t)
    print(t[i:j])

print("\n=== _connect_signals (player_play) ===")
i = t.find("def _connect_signals")
if i != -1:
    j = t.find("\n\ndef ", i)
    if j == -1: j = len(t)
    print(t[i:j])
