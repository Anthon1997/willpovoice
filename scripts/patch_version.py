from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

count = text.count('self.setWindowTitle("WillpoVoice")')
text = text.replace(
    'self.setWindowTitle("WillpoVoice")',
    'self.setWindowTitle("WillpoVoice v1.2.1")',
)

path.write_text(text, encoding="utf-8")
print(f"Titulos actualizados: {count}")
