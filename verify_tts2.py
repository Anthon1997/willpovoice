from pathlib import Path
src = Path("ui/modern_window.py").read_text(encoding="utf-8")
i = src.find("def _tts_text")
print("=== _tts_text ===")
print(src[i:i+900] if i>=0 else "NO ENCONTRADO")

for pat in ("def _export", "def _do_export", "export_audio", "normalize"):
    j = src.find(pat)
    print("\n=== ", pat, " ===", j)
    if j>=0: print(src[j:j+400])
