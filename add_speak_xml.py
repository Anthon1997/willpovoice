from pathlib import Path
import ast

p = Path("adapters/sapi_adapter.py")
t = p.read_text(encoding="utf-8")

# Buscar la firma exacta
i = t.find("def stop(self) -> None:")
print(f"Posición de stop: {i}")

if i > 0 and "def speak_xml" not in t:
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
    print("OK: método speak_xml agregado antes de stop")
else:
    print(f"speak_xml ya existe: {'def speak_xml' in t}")
