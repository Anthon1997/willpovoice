from pathlib import Path
t = Path("ui/modern_window.py").read_text(encoding="utf-8")
i = t.find("class UpdateDialog")
print(t[i:i + 4200])
