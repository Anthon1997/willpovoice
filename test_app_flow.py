import sys
sys.path.insert(0, '.')

try:
    from voice_manager import VoiceManager
    vm = VoiceManager()
    voices = vm.adapter.list_voices()
    print(f"VoiceManager.list_voices() = {len(voices)} voces")
    if voices:
        print(f"Primera voz: {voices[0].get('name', voices[0].get('description', '?'))}")
except Exception as e:
    print(f"ERROR en VoiceManager: {type(e).__name__}: {e}")
    import traceback; traceback.print_exc()

input("Enter...")
