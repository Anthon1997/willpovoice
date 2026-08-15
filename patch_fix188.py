from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

anchor = "MainWindow._set_player_icon = _set_player_icon"
nuevas = """MainWindow._on_position_changed = _on_position_changed
MainWindow._on_duration_changed = _on_duration_changed
MainWindow._on_media_status_changed = _on_media_status_changed
MainWindow._on_slider_moved = _on_slider_moved
MainWindow._on_volume_changed = _on_volume_changed
MainWindow._on_synth_ready = _on_synth_ready
MainWindow._on_synth_error = _on_synth_error
MainWindow._set_player_icon = _set_player_icon"""

if anchor in t and "MainWindow._on_position_changed" not in t:
    t = t.replace(anchor, nuevas, 1)
    print("Asignaciones de metodos del reproductor agregadas.")
else:
    print("AVISO: ancla no encontrada o ya asignado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
