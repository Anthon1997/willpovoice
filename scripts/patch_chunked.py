from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

start = text.find("class ExportWorker(QThread):")
end = text.find("class SpeakingDialog(QDialog):")

if start == -1 or end == -1:
    print("ERROR: anclas ExportWorker no encontradas")
else:
    new_worker = '''class ExportWorker(QThread):
    export_ok = Signal(str)
    export_error = Signal(str)
    export_progress = Signal(int)

    def __init__(self, exporter, text, path, voice, rate, volume):
        super().__init__()
        self.exporter = exporter
        self.text = text
        self.path = path
        self.voice = voice
        self.rate = rate
        self.volume = volume

    @staticmethod
    def _split_chunks(text, limit=600):
        import re

        sentences = re.split(r"(?<=[.!?...])\\s+", text)
        chunks = []
        current = ""

        for sentence in sentences:
            if len(sentence) > limit:
                if current:
                    chunks.append(current)
                    current = ""

                for i in range(0, len(sentence), limit):
                    chunks.append(sentence[i:i + limit])

                continue

            if len(current) + len(sentence) + 1 > limit and current:
                chunks.append(current)
                current = sentence
            else:
                current = f"{current} {sentence}".strip()

        if current:
            chunks.append(current)

        return chunks or [text]

    def run(self):
        try:
            import pythoncom

            pythoncom.CoInitialize()
        except Exception:
            pass

        import tempfile
        import wave

        try:
            chunks = self._split_chunks(self.text)
            total = len(chunks)
            first = True

            with wave.open(self.path, "wb") as out:
                for index, chunk in enumerate(chunks):
                    tmp = tempfile.mktemp(suffix=".wav")

                    self.exporter.save_text_to_wav(
                        text=chunk,
                        output_path=tmp,
                        voice_query=self.voice,
                        rate=self.rate,
                        volume=self.volume,
                    )

                    with wave.open(tmp, "rb") as wav_in:
                        if first:
                            out.setnchannels(wav_in.getnchannels())
                            out.setsampwidth(wav_in.getsampwidth())
                            out.setframerate(wav_in.getframerate())
                            first = False

                        out.writeframes(wav_in.readframes(wav_in.getnframes()))

                    Path(tmp).unlink(missing_ok=True)
                    self.export_progress.emit(
                        int((index + 1) * 100 / total)
                    )

            self.export_ok.emit(self.path)
        except Exception as exc:
            self.export_error.emit(str(exc))


'''
    text = text[:start] + new_worker + text[end:]

text = text.replace(
    "        self.export_worker.export_ok.connect(self.on_export_ok)",
    "        self.export_worker.export_ok.connect(self.on_export_ok)\n"
    "        self.export_worker.export_progress.connect("
    "self._on_export_progress)",
)

text = text.replace(
    """
        self._export_tick_timer = QTimer(self)
        self._export_tick_timer.timeout.connect(self._tick_export_progress)
        self._export_tick_timer.start(80)""",
    "",
)

progress_method = '''    def _on_export_progress(self, value: int) -> None:
        bar = getattr(self, "_export_bar", None)

        if bar is not None:
            bar.setValue(value)

        pct = getattr(self, "_export_pct", None)

        if pct is not None:
            pct.setText(f"{value}%")

'''

if "def _on_export_progress" not in text:
    i = text.find("    def _tick_export_progress")
    if i != -1:
        text = text[:i] + progress_method + text[i:]

path.write_text(text, encoding="utf-8")
print("Exportacion por bloques con progreso real lista.")
