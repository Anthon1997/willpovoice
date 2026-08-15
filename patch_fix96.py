from pathlib import Path
import shutil
import ast

# 1. Copiar fotos ms_*.png desde Downloads al proyecto
src = Path(r"C:\Users\antho\Downloads")
dst = Path("assets") / "icons"
dst.mkdir(parents=True, exist_ok=True)
copied = []
for f in src.glob("ms_*.png"):
    shutil.copy(f, dst / f.name)
    copied.append(f.name)
print("1. Fotos copiadas:", copied if copied else "(ninguna encontrada)")

# 2. Mover voces con foto al apartado Premium/Recomendadas
p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

old_group = '''        def group_of(name):
            lower = name.lower()
            if "multilingual" in lower:
                return "multi"'''
new_group = '''        def group_of(name):
            lower = name.lower()
            if "multilingual" in lower or any(
                k in lower for k in PREMIUM_PHOTOS
            ):
                return "multi"'''
if old_group in t:
    t = t.replace(old_group, new_group, 1)
    print("2. Elvira/Alonso/Dalia/William/Vivienne/Thalita -> Recomendadas.")
else:
    print("2. AVISO: group_of no encontrado.")

# 3. Nombres limpios para voces premium no-multilingual
old_dn = '''    def _display_name(self):
        n = self.voice_name.replace("Microsoft ", "")
        if "Multilingual" in n:
            first = n.split("Multilingual")[0].strip()
            return f"{first} (Multilingual)"
        return n'''
new_dn = '''    def _display_name(self):
        n = self.voice_name.replace("Microsoft ", "")
        if "Multilingual" in n:
            first = n.split("Multilingual")[0].strip()
            return f"{first} (Multilingual)"
        n = n.replace("Online (Natural)", "").replace("(Natural)", "")
        return n.strip()'''
if old_dn in t:
    t = t.replace(old_dn, new_dn, 1)
    print("3. Nombres limpios (Elvira - Spanish (Spain)).")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
