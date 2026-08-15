from pathlib import Path
import re, ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 1. Metodo que resuelve la foto de cada voz (propia o por genero)
if "def _voice_photo" not in t:
    t = t.replace(
        "    def _build_voice_rows(self, voices):",
        '''    def _voice_photo(self, voice_name, premium):
        low = voice_name.lower()
        for key, fname in PREMIUM_PHOTOS.items():
            if key in low:
                return self._resource_path(Path("assets") / "icons" / fname)
        first = (
            voice_name.replace("Microsoft ", "")
            .split(" ")[0]
            .strip()
            .lower()
        )
        female_names = {
            "carmen", "belen", "mercedes", "flor", "noor", "mar",
            "soledad", "paz", "nieves",
        }
        male_names = {"joshua", "luca", "elias", "noah", "jonah"}
        if first in female_names:
            female = True
        elif first in male_names:
            female = False
        else:
            female = first.endswith("a")
        fname = "face_f.png" if female else "face_m.png"
        return self._resource_path(Path("assets") / "icons" / fname)

    def _build_voice_rows(self, voices):''',
        1,
    )
    print("1. _voice_photo agregado (foto propia o por genero).")

# 2. Reemplazar _build_voice_rows completo: sin duplicados y
#    voces premium (con foto propia) solo en Recomendadas
new_build = '''    def _build_voice_rows(self, voices):
        container = getattr(self, "voice_rows_container", None)
        if container is None:
            return
        layout = self.voice_rows_layout
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget() if item else None
            if w is not None:
                w.deleteLater()
        self._voice_rows = []
        self._section_rows = {}
        self._section_headers = {}

        premium_keys = set(PREMIUM_PHOTOS)

        def group_of(name):
            lower = name.lower()
            if "multilingual" in lower:
                return "multi"
            if any(k in lower for k in premium_keys):
                return "multi"
            if "spanish" in lower or "español" in lower or "(es" in lower:
                return "es"
            if "desktop" in lower:
                return "desktop"
            return "en"

        seen = set()
        unique_voices = []
        for v in voices:
            if v not in seen:
                seen.add(v)
                unique_voices.append(v)

        sections = [
            ("multi", "RECOMENDADAS - PREMIUM", "#ffd75e"),
            ("es", "ESPANOL", "#8fa0bd"),
            ("desktop", "ESTANDAR - SIN INTERNET", "#8fa0bd"),
            ("en", "INGLES", "#8fa0bd"),
        ]
        for gid, title, color in sections:
            members = [v for v in unique_voices if group_of(v) == gid]
            if not members:
                continue
            header = QLabel(title)
            header.setStyleSheet(
                f"color: {color}; font-size: 10px; font-weight: 700; "
                "letter-spacing: 1px; background: transparent; "
                "padding: 8px 4px 2px 4px;"
            )
            self._section_headers[gid] = header
            layout.addWidget(header)
            rows = []
            for v in members:
                premium = gid == "multi"
                photo = self._voice_photo(v, premium)
                row = VoiceRow(self, v, premium, photo)
                layout.addWidget(row)
                rows.append(row)
                self._voice_rows.append((row, v))
            self._section_rows[gid] = rows
        layout.addStretch()
        self._sync_row_selection()

'''

t = re.sub(
    r"    def _build_voice_rows\(self, voices\):[\s\S]*?(?=\n    def )",
    "\n" + new_build,
    t,
    count=1,
)
print("2. _build_voice_rows reescrito: sin repetidos, premium unico.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
