from pathlib import Path
import ast

# ---- 1. app/version.py (fuente unica de version) ----
Path("app/version.py").write_text(
    'APP_VERSION = "1.2.1"\n'
    '# Tu repo de GitHub: "usuario/WillpoVoice" (vacio = sin chequeo)\n'
    'GITHUB_REPO = ""\n',
    encoding="utf-8",
)
print("1. app/version.py creado.")

# ---- 2. core/updater.py ----
Path("core/updater.py").write_text(r'''from __future__ import annotations

import json
import re
import urllib.request

from app.version import APP_VERSION, GITHUB_REPO


def _parse_version(tag: str) -> tuple:
    nums = re.findall(r"\d+", tag)
    return tuple(int(x) for x in nums[:3]) if nums else (0, 0, 0)


def check_update(timeout: int = 8) -> dict | None:
    if not GITHUB_REPO:
        return None
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "WillpoVoice",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8"))
    tag = data.get("tag_name", "")
    if _parse_version(tag) <= _parse_version(APP_VERSION):
        return None
    assets = data.get("assets", [])
    exe = next(
        (a for a in assets if a.get("name", "").lower().endswith(".exe")),
        None,
    )
    return {
        "version": tag,
        "notes": data.get("body", "") or "Sin notas de version.",
        "url": exe.get("browser_download_url") if exe else data.get("html_url", ""),
        "size": exe.get("size", 0) if exe else 0,
    }
''', encoding="utf-8")
print("2. core/updater.py creado.")

# ---- 3. modern_window: chequeo al arrancar ----
p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

old_hook = "        QTimer.singleShot(300, self._deferred_license)"
new_hook = old_hook + """
    if not getattr(self, "_update_checked", False):
        self._update_checked = True
        QTimer.singleShot(1500, self._check_updates)"""
if old_hook in t and "_update_checked" not in t:
    t = t.replace(old_hook, new_hook, 1)
    print("3. Chequeo de actualizaciones al arrancar.")

# ---- 4. Worker + dialogo + metodos ----
if "class UpdateWorker" not in t:
    t += '''

class UpdateWorker(QThread):
    found = Signal(object)
    none = Signal()

    def run(self):
        try:
            from core import updater
            info = updater.check_update()
            if info:
                self.found.emit(info)
            else:
                self.none.emit()
        except Exception:
            self.none.emit()


class DownloadWorker(QThread):
    progress = Signal(int)
    ok = Signal(str)
    fail = Signal(str)

    def __init__(self, url, dest):
        super().__init__()
        self.url = url
        self.dest = dest

    def run(self):
        try:
            import urllib.request
            req = urllib.request.Request(
                self.url, headers={"User-Agent": "WillpoVoice"})
            with urllib.request.urlopen(req, timeout=60) as r, \\
                    open(self.dest, "wb") as f:
                total = int(r.headers.get("Content-Length", 0))
                got = 0
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
                    got += len(chunk)
                    if total:
                        self.progress.emit(int(got * 100 / total))
            self.ok.emit(self.dest)
        except Exception as exc:
            self.fail.emit(str(exc))


class UpdateDialog(QDialog):
    def __init__(self, parent, info):
        super().__init__(parent)
        self.info = info
        CARD = "#141922"
        BORDER = "#262d3a"
        TEXT = "#e6edf3"
        MUTED = "#8b949e"
        PURPLE = "#7c5cff"
        self.setWindowTitle("Actualizacion disponible")
        self.setModal(True)
        self.setFixedWidth(480)
        self.setStyleSheet(
            f"UpdateDialog {{ background: #0b0f17; }} QLabel {{ color: {TEXT}; }}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(26, 22, 26, 20)
        lay.setSpacing(10)
        t1 = QLabel(f"Nueva version disponible:  {info['version']}")
        t1.setStyleSheet("font-size: 16px; font-weight: 700;")
        lay.addWidget(t1)
        notes = QPlainTextEdit()
        notes.setReadOnly(True)
        notes.setPlainText(info["notes"])
        notes.setFixedHeight(140)
        notes.setStyleSheet(
            f"QPlainTextEdit {{ background: {CARD}; color: {MUTED};"
            f" border: 1px solid {BORDER}; border-radius: 10px;"
            " padding: 10px; font-size: 11px; }"
        )
        lay.addWidget(notes)
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(8)
        self.bar.hide()
        lay.addWidget(self.bar)
        self.status = QLabel("")
        self.status.setStyleSheet(f"color: {MUTED}; font-size: 10.5px;")
        lay.addWidget(self.status)
        row = QHBoxLayout()
        row.setSpacing(10)
        self.dl_btn = QPushButton("Descargar e instalar")
        self.dl_btn.setFixedHeight(42)
        self.dl_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dl_btn.setStyleSheet(
            "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 #6d5df0, stop:1 {PURPLE}); color: white; border: none;"
            " border-radius: 10px; font-size: 13px; font-weight: 700; }"
            " QPushButton:hover { background: #8d75ff; }"
            " QPushButton:disabled { background: #333a4a; }"
        )
        self.dl_btn.clicked.connect(self.start_download)
        row.addWidget(self.dl_btn, 1)
        later = QPushButton("Ahora no")
        later.setFixedHeight(42)
        later.setCursor(Qt.CursorShape.PointingHandCursor)
        later.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {MUTED};"
            f" border: 1px solid {BORDER}; border-radius: 10px;"
            " font-size: 13px; font-weight: 600; }"
            f" QPushButton:hover {{ color: {TEXT}; }}"
        )
        later.clicked.connect(self.reject)
        row.addWidget(later, 1)
        lay.addLayout(row)

    def start_download(self):
        import tempfile
        from pathlib import Path as _P
        ver = "".join(c for c in self.info["version"] if c.isalnum() or c == ".")
        dest = str(_P(tempfile.gettempdir()) / f"WillpoVoice-Setup-{ver}.exe")
        self.dl_btn.setEnabled(False)
        self.bar.show()
        self.status.setText("Descargando actualizacion...")
        self._dl = DownloadWorker(self.info["url"], dest)
        self._dl.progress.connect(self.bar.setValue)
        self._dl.ok.connect(self.install_and_quit)
        self._dl.fail.connect(self.on_fail)
        self._dl.start()

    def on_fail(self, msg):
        self.status.setText("Error al descargar: " + msg)
        self.dl_btn.setEnabled(True)

    def install_and_quit(self, path):
        from PySide6.QtCore import QProcess
        from PySide6.QtWidgets import QApplication
        self.status.setText("Instalando... la app se cerrara.")
        QProcess.startDetached(
            path, ["/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"])
        QApplication.quit()


def _check_updates(self):
    self._update_worker = UpdateWorker()
    self._update_worker.found.connect(self._on_update_found)
    self._update_worker.start()


def _on_update_found(self, info):
    dlg = UpdateDialog(self, info)
    dlg.exec()


MainWindow._check_updates = _check_updates
MainWindow._on_update_found = _on_update_found
'''
    print("4. Worker + dialogo de actualizacion agregados.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
