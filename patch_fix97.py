from pathlib import Path
import shutil

# 1. Copiar caras desde Downloads
src = Path(r"C:\Users\antho\Downloads")
dst = Path("assets") / "icons"
for f in ("face_m.png", "face_f.png"):
    s = src / f
    if s.exists():
        shutil.copy(s, dst / f)
        print("1. Copiada:", f)
    else:
        print("1. AVISO: no existe en Downloads:", f)

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 2. Listas de nombres por genero
if "MALE_NAMES" not in t:
    gender = '''

FEMALE_NAMES = (
    "helena", "sabina", "elena", "elvira", "dalia", "paloma", "zira",
    "susan", "jenny", "aria", "michelle", "ashley", "heera",
    "katja", "hortense", "elsa", "laura", "conchita", "lucia",
    "valeria", "sofia", "paula", "camila", "francisca", "marina",
    "irene", "joana", "carmen", "penelope", "yara", "mariana",
    "isabela", "nuria", "libby", "maisie", "natasha", "clara",
    "cora", "layla", "sonia", "xiaoxiao", "yaoyao", "vivienne",
    "thalita", "emma", "ava", "seraphina", "ines", "maria",
    "ana", "diana", "sara", "vera", "nina",
)

MALE_NAMES = (
    "tomas", "jorge", "alvaro", "alonso", "raul", "pablo", "juan",
    "diego", "carlos", "enrique", "david", "guy", "davis",
    "brandon", "eric", "stephane", "stefan", "willem", "cosimo",
    "george", "harry", "ryan", "thomas", "andrew", "brian",
    "florian", "giuseppe", "hyunsu", "remy", "william", "liam",
    "noah", "james", "pedro", "mateo", "sebastian", "oscar",
    "hugo", "ivan", "sergio", "andres", "felipe",
)
'''
    t = t.replace(
        '    "dalia": "ms_dalia.png",\n}',
        '    "dalia": "ms_dalia.png",\n}' + gender,
        1,
    )
    print("2. Listas de genero agregadas.")

# 3. Asignar cara f/m a voces sin foto propia
old = '''                premium = gid == "multi"
                photo = None
                low = v.lower()
                for key, fname in PREMIUM_PHOTOS.items():
                    if key in low:
                        photo = self._resource_path(
                            Path("assets") / "icons" / fname
                        )
                        break'''
new = '''                premium = gid == "multi"
                photo = None
                low = v.lower()
                for key, fname in PREMIUM_PHOTOS.items():
                    if key in low:
                        photo = self._resource_path(
                            Path("assets") / "icons" / fname
                        )
                        break
                if photo is None:
                    if any(m in low for m in MALE_NAMES):
                        photo = self._resource_path(
                            Path("assets") / "icons" / "face_m.png"
                        )
                    elif any(f in low for f in FEMALE_NAMES):
                        photo = self._resource_path(
                            Path("assets") / "icons" / "face_f.png"
                        )'''
if old in t:
    t = t.replace(old, new, 1)
    print("3. Caras asignadas por genero a voces estandar.")
else:
    print("3. AVISO: bloque de foto no encontrado.")

p.write_text(t, encoding="utf-8")

import ast
try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
