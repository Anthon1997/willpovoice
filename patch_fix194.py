from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

nombres = [
    "_tick_player", "_on_position_changed", "_on_duration_changed",
    "_on_media_status_changed", "_on_slider_moved", "_on_volume_changed",
    "_on_synth_ready", "_on_synth_error", "_spin_tick", "_draw_spin",
    "_player_play_clicked", "_set_player_icon", "speak_text",
    "_check_updates", "_on_update_found",
]
for name in nombres:
    has_def = f"def {name}(" in t
    has_asg = f"MainWindow.{name} = {name}" in t
    if has_def and not has_asg:
        t += f"\nMainWindow.{name} = {name}\n"
        print("Asignado a MainWindow:", name)
    elif has_def and has_asg:
        pass
    else:
        print("Sin def (se omite):", name)

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
