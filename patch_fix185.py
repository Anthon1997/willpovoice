from pathlib import Path
import ast

p = Path("core/text_normalizer.py")
t = p.read_text(encoding="utf-8")

# ---- 1. Quitar C++ del mapa TECH (que lo maneje la capa de simbolos) ----
old_tech = '''TECH = {
    "C++": " ce plus plus ",
    "c++": " ce plus plus ",
    "Python": "Paiton",'''
new_tech = '''TECH = {
    "Python": "Paiton",'''
if old_tech in t:
    t = t.replace(old_tech, new_tech, 1)
    print("1. C++ fuera de TECH (signos respetados).")

# ---- 2. Menos con espacios -> 'menos' ----
old_sym = '''    ("&", " y "),
    ("+", " mas "),'''
new_sym = '''    ("&", " y "),
    ("+", " mas "),
    (" - ", " menos "),'''
if old_sym in t:
    t = t.replace(old_sym, new_sym, 1)
    print("2. Signo menos respetado (' - ' -> 'menos').")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
