from pathlib import Path

t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=" * 70)
print("1. TODO LO RELACIONADO CON PREVIEW / MUESTRA DE VOZ")
print("=" * 70)
for ln_no, ln in enumerate(t.splitlines(), 1):
    low = ln.lower()
    if "preview" in low or "muestra" in low:
        print(f"{ln_no}: {ln}")

print("\n----- funciones de preview (cuerpo completo) -----")
for name in ("def _preview_voice", "def _on_preview", "def _play_preview",
             "def _stop_preview", "def _toggle_preview", "def preview"):
    i = t.find(name)
    if i != -1:
        j = t.find("\ndef ", i + 10)
        print(f"\n----- {name} -----")
        print(t[i:j if j != -1 else i + 1500])

print("\n" + "=" * 70)
print("2. CLICK EN TARJETA DE VOZ (seleccion)")
print("=" * 70)
for name in ("def _on_voice_card", "def _select_voice_card",
             "def _voice_card_clicked", "def _on_card_clicked"):
    i = t.find(name)
    if i != -1:
        j = t.find("\ndef ", i + 10)
        print(f"\n----- {name} -----")
        print(t[i:j if j != -1 else i + 1200])

print("\n----- conexiones de tarjetas/preview -----")
for ln in t.splitlines():
    if ("card" in ln.lower() or "preview" in ln.lower()) and ("connect" in ln or "Signal" in ln):
        print(ln.strip())

print("\n" + "=" * 70)
print("3. _load_voices (sincronia combo <-> tarjetas)")
print("=" * 70)
i = t.find("def _load_voices")
if i != -1:
    j = t.find("\ndef ", i + 10)
    print(t[i:j if j != -1 else i + 2000])

print("\nFIN")
