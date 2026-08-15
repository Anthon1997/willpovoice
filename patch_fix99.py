from pathlib import Path

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 0. Asegurar que el mapeo de fotos tenga las nuevas
if '"elvira": "ms_elvira.png"' not in t:
    t = t.replace(
        '    "seraphina": "ms_seraphina.png",\n}',
        '    "seraphina": "ms_seraphina.png",\n'
        '    "william": "ms_william.png",\n'
        '    "vivienne": "ms_vivienne.png",\n'
        '    "thalita": "ms_thalita.png",\n'
        '    "elvira": "ms_elvira.png",\n'
        '    "alonso": "ms_alonso.png",\n'
        '    "dalia": "ms_dalia.png",\n}',
        1,
    )
    print("0. Mapeo de fotos completado.")

# 1. Reemplazar la ULTIMA definicion de _build_voice_rows (la que manda)
marker = "    def _build_voice_rows(self, voices):"
idx = t.rfind(marker)
if idx == -1:
    print("AVISO: _build_voice_rows no encontrado.")
else:
    end = t.find("\n    def ", idx + len(marker))
    if end == -1:
        end = len(t)
    new_method = '''    def _build_voice_rows(self, voices):
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

        def photo_for(name):
            low = name.lower()
            for key, fname in PREMIUM_PHOTOS.items():
                if key in low:
                    return self._resource_path(
                        Path("assets") / "icons" / fname
                    )
            first = (
                name.replace("Microsoft ", "")
                .split(" ")[0]
                .strip()
                .lower()
            )
            female_names = {
                "carmen", "belen", "mercedes", "flor", "noor", "mar",
                "soledad", "paz", "nieves", "consuelo", "rocio",
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
                row = VoiceRow(self, v, premium, photo_for(v))
                layout.addWidget(row)
                rows.append(row)
                self._voice_rows.append((row, v))
            self._section_rows[gid] = rows
        layout.addStretch()
        self._sync_row_selection()
'''
    t = t[:idx] + new_method + t[end:]
    print("1. Ultima definicion de _build_voice_rows reemplazada.")

p.write_text(t, encoding="utf-8")

import ast
try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
