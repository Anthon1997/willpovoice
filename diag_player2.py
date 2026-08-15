from pathlib import Path
t = Path("ui/modern_window.py").read_text(encoding="utf-8")

# Buscar la zona del reproductor (boton play + slider + tiempos)
for kw in ("progress_slider", "time_cur", "time_tot", "_set_player_icon",
           "player_timer", "player_btn", "_player_play_clicked"):
    i = t.find(kw)
    if i != -1:
        print(f"\n===== {kw} (primera ocurrencia en {i}) =====")
        print(t[max(0, i-300):i+600])

# Ver el metodo _set_player_icon y _tick completo
for name in ("def _set_player_icon", "def _tick", "def _tick_player"):
    i = t.find(name)
    if i != -1:
        j = t.find("\ndef ", i + 10)
        print(f"\n===== {name} =====")
        print(t[i:j if j != -1 else i + 900])
