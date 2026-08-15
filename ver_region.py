import sys
from pathlib import Path

path, start, end = sys.argv[1], sys.argv[2], sys.argv[3]
t = Path(path).read_text(encoding="utf-8")
i = t.find(start)
j = t.find(end)
if i == -1 or j == -1:
    print("MARCADORES NO ENCONTRADOS")
else:
    print(t[i:j + len(end)])
