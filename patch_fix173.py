from pathlib import Path

p = Path("core/text_normalizer.py")
t = p.read_text(encoding="utf-8")

old = '''    text = re.sub(
        r"(\b\d{1,3}(?:\.\d{3})+(?:,\d+)?\b|\b\d+(?:[.,]\d+)?)\s*%",
        lambda m: _num_match(m.group(1)) + " por ciento",
        text,
    )'''

new = '''    text = re.sub(
        r"(\b\d{1,3}(?:\.\d{3})+(?:,\d+)?\b|\b\d+(?:[.,]\d+)?)\s*%",
        lambda m: _num_match(m.group(1)) + " por ciento",
        text,
    )
    text = re.sub(r"\s*%", "", text)'''

if old in t:
    t = t.replace(old, new, 1)
    print("1. Regex de % corregida (remueve símbolo duplicado).")

p.write_text(t, encoding="utf-8")

# Prueba
import subprocess
result = subprocess.run(
    [".\.venv\Scripts\python.exe", "-c",
     "from core.text_normalizer import normalize_for_tts as n; "
     "print(n('Tengo 123 manzanas, el 45% de 2026, mas 3,14 y 45.678 kilos'))"],
    capture_output=True,
    text=True,
)
print(result.stdout)
