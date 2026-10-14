from pathlib import Path
import re
src = Path("ui/modern_window.py").read_text(encoding="utf-8")
i = src.find("def speak_text(self):")
end = src.find("\ndef ", i+10)
print("=== speak_text COMPLETO ===")
print(src[i:end])
