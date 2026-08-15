from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

if "multi_persons" in t:
    print("El dedup ya existia; se deja como esta.")
else:
    dedup = (
        "\n            lowered = [v.lower() for v in voices]\n"
        "            multi_persons = {\n"
        "                k for k in PREMIUM_PHOTOS\n"
        "                if any(k in n and \"multilingual\" in n for n in lowered)\n"
        "            }\n"
        "            dedup = []\n"
        "            for v in voices:\n"
        "                low = v.lower()\n"
        "                person = next((k for k in PREMIUM_PHOTOS if k in low), None)\n"
        "                if person in multi_persons and \"multilingual\" not in low:\n"
        "                    continue\n"
        "                dedup.append(v)\n"
        "            voices = dedup"
    )
    t2, n = re.subn(
        r"(voices\.sort\(key=lambda n: \(not self\._is_premium\(n\), n\.lower\(\)\)\))",
        lambda m: m.group(1) + dedup,
        t,
        count=1,
    )
    if n:
        t = t2
        print("Dedup insertado tras el sort.")
    else:
        print("AVISO: linea sort no encontrada.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
