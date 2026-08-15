from pathlib import Path

t = Path("ui/modern_window.py").read_text(encoding="utf-8")
lines = t.split("\n")

print("=== lineas con lang_combo / voice_combo (altura/creacion) ===")
for i, ln in enumerate(lines, 1):
    if "lang_combo" in ln or (
        "voice_combo" in ln and (
            "Fixed" in ln or "setStyleSheet" in ln or "= QComboBox" in ln
            or "setSizePolicy" in ln or "setIconSize" in ln)):
        print(f"{i:5} | {ln}")

print("=== creaciones duplicadas ===")
print("lang_combo = QComboBox():", t.count("self.lang_combo = QComboBox()"))
print("voice_combo = QComboBox():", t.count("self.voice_combo = QComboBox()"))

print("=== region sel completa ===")
start = t.find("sel = QHBoxLayout()")
end = t.find("cl.addLayout(sel)")
if start != -1 and end != -1:
    print(t[start:end + 18])
