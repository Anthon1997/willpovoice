from pathlib import Path
t = Path("ui/modern_window.py").read_text(encoding="utf-8")
i = t.find("class PreviewWorker")
print(t[i:i+2600])
