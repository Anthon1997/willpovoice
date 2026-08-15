from pathlib import Path

mt = Path("ui/modern_window.py").read_text(encoding="utf-8")

for marker in ("def _select_voice", "def _on_combo_voice", "def showEvent"):
    i = mt.find(marker)
    if i != -1:
        j = mt.find("\ndef ", i + 10)
        print(f"===== {marker} =====")
        print(mt[i:j if j != -1 else i + 900])

lm = Path("core/license_manager.py").read_text(encoding="utf-8")
i = lm.find("def check_status")
if i != -1:
    j = lm.find("\ndef ", i + 10)
    print("===== check_status =====")
    print(lm[i:j if j != -1 else i + 900])
