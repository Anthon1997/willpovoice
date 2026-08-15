from pathlib import Path

t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=== ocurrencias ===")
for m in ("pos_slider", "play_btn", "pause", "QMediaPlayer",
          "_tick", "time_label", "vol_slider", "stop"):
    print(f"{m}: {t.count(m)}")

i = t.find("pos_slider")
if i != -1:
    print("\n===== ZONA BARRA REPRODUCTOR =====")
    print(t[max(0, i - 2500):i + 2500])

for name in ("def _player_play_clicked", "def _play_clicked",
             "def speak_text", "def _stop_clicked", "def _on_tick"):
    i = t.find(name)
    if i != -1:
        j = t.find("\ndef ", i + 10)
        print(f"\n===== {name} =====")
        print(t[i:j if j != -1 else i + 1500])

te = Path("core/tts_engine.py").read_text(encoding="utf-8")
for name in ("def speak", "def stop", "def pause", "def resume"):
    i = te.find(name)
    if i != -1:
        j = te.find("\ndef ", i + 10)
        print(f"\n===== tts_engine {name} =====")
        print(te[i:j if j != -1 else i + 800])
