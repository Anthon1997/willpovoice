from pathlib import Path

critical = [
    "run.py",
    "core/license_manager.py",
    "core/text_normalizer.py",
    "ui/modern_window.py",
    "scripts/keygen_gui.py",
    "scripts/v3_sign.py"
]

limpiados = 0
for fp in critical:
    p = Path(fp)
    if not p.exists():
        continue
    content = p.read_bytes()
    if content.startswith(b'\xef\xbb\xbf'):
        p.write_bytes(content[3:])
        limpiados += 1
        print(f"BOM eliminado: {fp}")

print(f"Archivos críticos limpiados: {limpiados}")
