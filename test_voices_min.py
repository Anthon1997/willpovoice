import comtypes.client
sapi = comtypes.client.CreateObject("SAPI.SpVoice")
voices = sapi.GetVoices()
print(f"Total voces: {len(voices)}")
input("Enter para salir...")
