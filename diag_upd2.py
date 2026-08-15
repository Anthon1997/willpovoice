from pathlib import Path
import json, re, urllib.request

t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=== Piezas del flujo de actualizacion ===")
for k in ["QTimer.singleShot(1500, self._check_updates)",
          "def _check_updates", "MainWindow._check_updates",
          "def _on_update_found", "MainWindow._on_update_found",
          "class UpdateDialog", "def _on_update_none"]:
    print("OK   " if k in t else "FALTA", k)

i = t.find("def _on_update_found")
if i != -1:
    print("\n=== Codigo de _on_update_found ===")
    print(t[i:i + 1200])

print("\n=== Simulacion como app instalada 1.2.2 ===")
def pv(tag):
    n = re.findall(r"\d+", tag)
    return tuple(int(x) for x in n[:3])
url = "https://api.github.com/repos/Anthon1997/willpovoice/releases/latest"
req = urllib.request.Request(url, headers={"User-Agent": "WillpoVoice",
    "Accept": "application/vnd.github+json"})
data = json.loads(urllib.request.urlopen(req, timeout=8).read().decode())
tag = data.get("tag_name", "")
print("tag remoto:", tag)
print("remoto > 1.2.2:", pv(tag) > pv("1.2.2"))
print("assets:", [a["name"] for a in data.get("assets", [])])
