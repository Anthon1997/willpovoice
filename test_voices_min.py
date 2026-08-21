import sys
try:
    import comtypes.client
    sapi = comtypes.client.CreateObject("SAPI.SpVoice")
    voices = sapi.GetVoices()
    print(f"Total voces: {len(voices)}")
    for i, v in enumerate(voices):
        try:
            print(f"  [{i}] {v.GetDescription()}")
        except:
            print(f"  [{i}] (sin descripcion)")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback; traceback.print_exc()
input("Press Enter to exit...")
