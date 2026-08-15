from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. _select_voice sin bloqueo ----
old_sv = """def _select_voice(self, name):
    self._selected_voice = name
    if hasattr(self, "pro_badge"):
        self.pro_badge.setVisible(self._is_premium(name))
    for i in range(self.voice_combo.count()):
        if self.voice_combo.itemData(i, Qt.ItemDataRole.UserRole) == name:
            self.voice_combo.blockSignals(True)
            self.voice_combo.setCurrentIndex(i)
            self.voice_combo.blockSignals(False)
            break
    try:
        self.engine.select_voice(name)
    except Exception:
        pass
    self._rebuild_cards()
    self._rebuild_all_page()
    self._rebuild_fav_page()"""
new_sv = """def _select_voice(self, name):
    self._selected_voice = name
    if hasattr(self, "pro_badge"):
        self.pro_badge.setVisible(self._is_premium(name))
    for i in range(self.voice_combo.count()):
        if self.voice_combo.itemData(i, Qt.ItemDataRole.UserRole) == name:
            self.voice_combo.blockSignals(True)
            self.voice_combo.setCurrentIndex(i)
            self.voice_combo.blockSignals(False)
            break
    self.statusBar().showMessage(f"Cargando voz: {name}...")
    self._voice_worker = VoiceSelectWorker(self.engine.adapter, name)
    self._voice_worker.done.connect(self._on_voice_loaded)
    self._voice_worker.start()
    QTimer.singleShot(250, self._deferred_rebuilds)"""
if old_sv in t:
    t = t.replace(old_sv, new_sv, 1)
    print("1. _select_voice en segundo plano.")

# ---- 2. Licencia tras el primer paint ----
old_se = """    if not getattr(self, "_license_checked", False):
        self._license_checked = True
        if not self._check_license():
            self.close()"""
new_se = """    if not getattr(self, "_license_checked", False):
        self._license_checked = True
        QTimer.singleShot(300, self._deferred_license)"""
if old_se in t:
    t = t.replace(old_se, new_se, 1)
    print("2. Licencia diferida tras pintar.")

# ---- 3. Worker + helpers + cache de avatares ----
if "class VoiceSelectWorker" not in t:
    t += '''

class VoiceSelectWorker(QThread):
    done = Signal(str)

    def __init__(self, adapter, name):
        super().__init__()
        self.adapter = adapter
        self.name = name

    def run(self):
        import pythoncom
        pythoncom.CoInitialize()
        try:
            self.adapter.set_voice(self.name)
        except Exception:
            pass
        finally:
            pythoncom.CoUninitialize()
        self.done.emit(self.name)


def _on_voice_loaded(self, name):
    if name == getattr(self, "_selected_voice", ""):
        self.statusBar().showMessage(f"Voz lista: {name}")


def _deferred_rebuilds(self):
    self._rebuild_cards()
    self._rebuild_all_page()
    self._rebuild_fav_page()


def _deferred_license(self):
    if not self._check_license():
        self.close()


_orig_avatar = MainWindow._avatar_pixmap


def _avatar_pixmap_cached(self, name, ring):
    cache = self.__dict__.setdefault("_avatar_cache", {})
    key = (name, ring)
    if key in cache:
        return cache[key]
    pix = _orig_avatar(self, name, ring)
    cache[key] = pix
    return pix


MainWindow._avatar_pixmap = _avatar_pixmap_cached
MainWindow._on_voice_loaded = _on_voice_loaded
MainWindow._deferred_rebuilds = _deferred_rebuilds
MainWindow._deferred_license = _deferred_license
'''
    print("3. Worker + cache de avatares + helpers.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
