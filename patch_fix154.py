from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

old = """def _avatar_pixmap_cached(self, name, ring):
    cache = self.__dict__.setdefault("_avatar_cache", {})
    key = (name, ring)
    if key in cache:
        return cache[key]
    pix = _orig_avatar(self, name, ring)
    cache[key] = pix
    return pix"""
new = """def _avatar_pixmap_cached(self, name, *args, **kwargs):
    cache = self.__dict__.setdefault("_avatar_cache", {})
    key = (name, args, tuple(sorted(kwargs.items())))
    if key in cache:
        return cache[key]
    pix = _orig_avatar(self, name, *args, **kwargs)
    cache[key] = pix
    return pix"""
if old in t:
    t = t.replace(old, new, 1)
    print("Wrapper flexible (args/kwargs) aplicado.")
else:
    print("AVISO: wrapper no encontrado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
