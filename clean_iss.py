from pathlib import Path
p = Path("installer/NaturalVoiceTTS.iss")
lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
keep = []
removed = []
for ln in lines:
    low = ln.lower()
    if "redist" in low or ('readme' in low and 'source:' in low):
        removed.append(ln.strip())
        continue
    keep.append(ln)
p.write_text("\r\n".join(keep), encoding="utf-8")
print("líneas eliminadas:")
for r in removed:
    print("  -", r)
