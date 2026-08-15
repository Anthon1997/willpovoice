from pathlib import Path
import ast

pa = Path("adapters/sapi_adapter.py")
a = pa.read_text(encoding="utf-8")

old = """    def set_voice(self, query: str) -> bool:
        \"\"\"
        Selecciona una voz por coincidencia parcial.
        \"\"\"
        self.stop()
        token = self._get_voice_token(query)

        if token is None:
            raise VoiceNotFoundError(
                f"No se encontró una voz que coincida con: {query}"
            )

        try:
            self.sapi.Voice = token
            self.logger.info("Voz seleccionada: %s", query)
            return True"""
new = """    def set_voice(self, query: str) -> bool:
        \"\"\"
        Selecciona una voz por coincidencia parcial.
        Si la voz ya es la actual, no toca el stream (evita
        envenenar la sintesis con purgados redundantes).
        \"\"\"
        token = self._get_voice_token(query)

        if token is None:
            raise VoiceNotFoundError(
                f"No se encontró una voz que coincida con: {query}"
            )

        try:
            actual = self.sapi.Voice.GetDescription()
            objetivo = token.GetDescription()
        except Exception:
            actual, objetivo = "", "x"
        if actual and objetivo and actual == objetivo:
            return True

        self.stop()
        try:
            self.sapi.Voice = token
            self.logger.info("Voz seleccionada: %s", query)
            return True"""
if old in a:
    a = a.replace(old, new, 1)
    pa.write_text(a, encoding="utf-8")
    print("set_voice ahora es no-op si la voz ya es la actual.")
else:
    print("AVISO: set_voice no encontrado exacto.")

try:
    ast.parse(a)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
