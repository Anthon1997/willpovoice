from pathlib import Path
import ast

pa = Path("adapters/sapi_adapter.py")
a = pa.read_text(encoding="utf-8")

# ---- 1. Helper: nueva instancia SAPI conservando voz/rate/volumen ----
if "def _new_sapi" not in a:
    helper = '''    def _new_sapi(self) -> None:
        \"\"\"
        Crea una instancia SAPI nueva conservando voz, rate y
        volumen. Las voces Online quedan envenenadas tras un
        purgado en mitad de la lectura; una instancia fresca
        garantiza que el siguiente Speak arranque.
        \"\"\"
        import win32com.client
        voz, rate, vol = None, 0, 100
        try:
            voz = self.sapi.Voice
            rate = self.sapi.Rate
            vol = self.sapi.Volume
        except Exception:
            pass
        nuevo = win32com.client.Dispatch("SAPI.SpVoice")
        try:
            if voz is not None:
                nuevo.Voice = voz
        except Exception:
            pass
        try:
            nuevo.Rate = rate
            nuevo.Volume = vol
        except Exception:
            pass
        self.sapi = nuevo

'''
    anchor = a.find("    def speak(")
    if anchor != -1:
        a = a[:anchor] + helper + a[anchor:]
        print("1. Helper _new_sapi agregado.")

# ---- 2. speak() usa instancia fresca ----
old = """        flags = 0

        if asynchronous:
            flags |= self.SVSFlagsAsync

        try:
            self.sapi.Speak(text, flags)"""
new = """        self._new_sapi()
        flags = 0

        if asynchronous:
            flags |= self.SVSFlagsAsync

        try:
            self.sapi.Speak(text, flags)"""
if old in a:
    a = a.replace(old, new, 1)
    print("2. speak() reconstruye instancia SAPI fresca.")

pa.write_text(a, encoding="utf-8")

try:
    ast.parse(a)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
