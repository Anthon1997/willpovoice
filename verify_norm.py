from pathlib import Path
src = Path("core/text_normalizer.py").read_text(encoding="utf-8")
i = src.find("def normalize_for_tts")
print(src[i-200:i+800] if i>=0 else "NO ENCONTRADO")
