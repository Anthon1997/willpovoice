from pathlib import Path
import ast

p = Path("adapters/sapi_adapter.py")
t = p.read_text(encoding="utf-8")

print("=== ¿Existe speak_xml? ===")
print("speak_xml" in t)

print("\n=== Métodos def ===")
import re
for m in re.finditer(r"def (\w+)\(self[^)]*\):", t):
    ln = t[:m.start()].count("\n")+1
    print(f"L{ln}: {m.group(0)}")

# Si no existe speak_xml, agregarlo antes de def stop
if "def speak_xml" not in t:
    i = t.find("def stop(self):")
    if i > 0:
        method = '''    def speak_xml(self, text: str, asynchronous: bool = False) -> None:
        """
        Reproduce texto SSML/XML con tags de idioma.
        
        Args:
            text: texto SSML con tags <lang xml:lang="...">
            asynchronous: si True, no bloquea el hilo
        """
        if not text or not text.strip():
            raise ValueError("El texto a reproducir no puede estar vacío.")

        self._new_sapi()
        flags = self.SVSFIsXML

        if asynchronous:
            flags |= self.SVSFlagsAsync

        try:
            self.sapi.Speak(text, flags)
        except Exception as exc:
            self.logger.exception("Error al reproducir texto SSML.")
            raise SpeechError("No se pudo reproducir el texto SSML.") from exc

    '''
        t = t[:i] + method + t[i:]
        p.write_text(t, encoding="utf-8", newline="\n")
        ast.parse(t)
        print("\nOK: método speak_xml agregado")
    else:
        print("\nERROR: no se encontró def stop")
else:
    print("\nspeak_xml ya existe")
