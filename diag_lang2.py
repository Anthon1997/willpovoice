from pathlib import Path
t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=== Donde se crea el combo de idioma ===")
for i, ln in enumerate(t.splitlines(), 1):
    if "Español" in ln or "Inglés" in ln or "addItem" in ln and "Todos" in ln:
        print(f"{i}: {ln.strip()[:110]}")

print("\n=== _is_premium y _make_card ===")
for name in ["_is_premium", "_make_card"]:
    i = t.find(f"def {name}")
    if i != -1:
        j = t.find("\ndef ", i + 10)
        print(f"\n----- def {name} -----")
        print(t[i:j if j != -1 else i+1500])

print("\n=== Senales/conexiones del combo de idioma ===")
for i, ln in enumerate(t.splitlines(), 1):
    if "lang_combo" in ln or "idioma_combo" in ln or "combo_idioma" in ln or "filter_lang" in ln:
        print(f"{i}: {ln.strip()[:110]}")
