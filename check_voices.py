import sys
sys.path.insert(0, ".")
from core.brain import get_available_voices
voces = get_available_voices()
print(f"\nTotal voces detectadas: {len(voces)}")
if len(voces) < 50:
    print("⚠ PO CAS VOCES - adapter posiblemente no registrado")
    print("\nPrimeras 10 voces:")
    for v in voces[:10]:
        print(f"  - {v.get('name', 'N/A')}")
elif len(voces) > 200:
    print("✓ Adapter funcionando correctamente (300+ voces)")
else:
    print("⚠ Rango medio - verificar adapter")
