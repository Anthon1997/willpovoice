from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# 1) Añadir DISCORD_URL cerca de las YAPE URLs
if "DISCORD_URL" not in t:
    for anchor in ("YAPE_URL_MENSUAL", "YAPE_URL_LIFETIME"):
        idx = t.find(anchor)
        if idx != -1:
            eol = t.find("\n", idx)
            t = t[:eol+1] + 'DISCORD_URL = "https://discord.com/invite/HpTZ9x8MG"\n' + t[eol+1:]
            log.append("DISCORD_URL inyectada")
            break
    else:
        # si no hay YAPE URLs, al inicio tras los imports
        i = t.find("\n\n")
        t = t[:i+2] + 'DISCORD_URL = "https://discord.com/invite/HpTZ9x8MG"\n' + t[i+2:]
        log.append("DISCORD_URL inyectada (inicio)")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("SINTAXIS OK")
print("parches:", log)
