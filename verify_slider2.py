from pathlib import Path
import re
src = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=== ocurrencias ::groove ===", len(re.findall(r"::groove", src)))
print("=== ocurrencias QSlider:: ===", len(re.findall(r"QSlider::", src)))

for pat in ("_mock_slider", "QSlider::handle", "QSlider::groove", "QSlider::add-page", "QSlider::sub-page"):
    for m in list(re.finditer(re.escape(pat), src))[:3]:
        ln = src[:m.start()].count("\n") + 1
        print("\n=== ", pat, " linea", ln, " ===")
        print(src[m.start()-300:m.start()+600])
        print("-"*70)

i = src.find("self.progress_slider = QSlider")
print("\n=== zona progress_slider ===")
print(src[i-100:i+900])
