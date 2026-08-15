from pathlib import Path

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 1. Ampliar mapeo de fotos con las 6 nuevas
old_dict = '''    "remy": "ms_remy.png",
    "seraphina": "ms_seraphina.png",
}'''
new_dict = '''    "remy": "ms_remy.png",
    "seraphina": "ms_seraphina.png",
    "william": "ms_william.png",
    "vivienne": "ms_vivienne.png",
    "thalita": "ms_thalita.png",
    "elvira": "ms_elvira.png",
    "alonso": "ms_alonso.png",
    "dalia": "ms_dalia.png",
}'''
if old_dict in t:
    t = t.replace(old_dict, new_dict, 1)
    print("1. Mapeo de fotos ampliado (william, vivienne, thalita, elvira, alonso, dalia).")

# 2. Buscar foto en TODAS las voces, no solo Premium
old_lookup = '''                premium = gid == "multi"
                photo = None
                if premium:
                    low = v.lower()
                    for key, fname in PREMIUM_PHOTOS.items():
                        if key in low:
                            photo = self._resource_path(
                                Path("assets") / "icons" / fname
                            )
                            break'''
new_lookup = '''                premium = gid == "multi"
                photo = None
                low = v.lower()
                for key, fname in PREMIUM_PHOTOS.items():
                    if key in low:
                        photo = self._resource_path(
                            Path("assets") / "icons" / fname
                        )
                        break'''
if old_lookup in t:
    t = t.replace(old_lookup, new_lookup, 1)
    print("2. Fotos aplicadas a todas las secciones (incluye espanol).")

p.write_text(t, encoding="utf-8")

# 3. Leer adapter_config.reg para ver como registrar voces nuevas
reg = Path("installer/adapter_config.reg")
if reg.exists():
    content = reg.read_text(encoding="utf-8", errors="ignore")
    print("---- adapter_config.reg (primeros 3500 caracteres) ----")
    print(content[:3500])
else:
    print("AVISO: installer/adapter_config.reg no existe.")
