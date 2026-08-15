from pathlib import Path

t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=== Inventario de funciones y asignaciones ===")
checks = [
    "def _select_voice", "def _load_entry", "def _delete_entry",
    "def _toggle_fav", "def _rebuild_cards", "def _load_history",
    "def _append_rec_cards", "def _append_all_cards",
    "def _toggle_preview", "def _stop_preview", "def _check_preview_end",
    "def _on_preview_finished", "class PreviewWorker",
    "def _player_play_clicked", "def _tick_player", "def speak_text",
    "def _on_combo_voice", "def _load_voices",
]
for c in checks:
    print("OK   " if c in t else "FALTA " , c)

print("\n=== Asignaciones a MainWindow ===")
for c in ["MainWindow._select_voice", "MainWindow._load_entry",
          "MainWindow._delete_entry", "MainWindow._toggle_fav",
          "MainWindow._toggle_preview", "MainWindow._stop_preview",
          "MainWindow._check_preview_end", "MainWindow._on_preview_finished",
          "MainWindow._rebuild_cards", "MainWindow._load_history"]:
    print("OK   " if c in t else "FALTA ", c)

print("\n=== Region tras _check_preview_end (800 chars) ===")
i = t.find("def _check_preview_end")
if i != -1:
    print(t[i:i + 800])
else:
    print("  _check_preview_end NO EXISTE")
