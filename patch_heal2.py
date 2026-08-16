from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

old = '''    inst = os.path.join(base, "engine", "Installer.exe")
    if not os.path.exists(inst):
        return
    self._repair_tried = True
    import ctypes
    ret = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", inst,
        "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART", None, 0)'''
new = '''    dll = os.path.join(base, "engine", "x64",
                       "NaturalVoiceSAPIAdapter.dll")
    if not os.path.exists(dll):
        return
    self._repair_tried = True
    import ctypes
    ret = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", "regsvr32.exe",
        '/s "' + dll + '"', None, 0)'''
if old in t:
    t = t.replace(old, new, 1)
    print("self-heal con regsvr32 OK")
else:
    print("ANCLA no encontrada")

p.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("SINTAXIS OK")
