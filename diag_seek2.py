from pathlib import Path
t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=== self.player: que es y como se crea ===")
for i, ln in enumerate(t.splitlines(), 1):
    if "self.player" in ln and ("=" in ln) and ("QMedia" in ln or "Player" in ln or "player =" in ln):
        print(f"{i}: {ln.strip()[:110]}")

print("\n=== _resume_offset / _seconds / offset usos ===")
for i, ln in enumerate(t.splitlines(), 1):
    if "_resume_offset" in ln or "_resume_at" in ln:
        print(f"{i}: {ln.strip()[:110]}")

for name in ["speak_text", "_player_play_clicked", "_on_media_status_changed", "_spin_tick"]:
    i = t.find(f"def {name}")
    if i != -1:
        j = t.find("\ndef ", i + 10)
        print(f"\n----- def {name} -----")
        print(t[i:j if j != -1 else i + 2500])
