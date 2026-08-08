from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

start = text.find("class ExportWorker(QThread):")
end = text.find("class SpeakingDialog(QDialog):")

if start == -1 or end == -1:
    print("ERROR: anclas no encontradas")
else:
    new_worker = '''class ExportWorker(QThread):
    export_ok = Signal(str)
    export_error = Signal(str)
    export_progress = Signal(int)
    MAX_WORKERS = 4

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

    def _synth_chunk(self, chunk, tmp_path):
        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()

        try:
            sapi = win32com.client.Dispatch("SAPI.SpVoice")

            if self.exporter.adapter is not None:
                if self.voice:
                    self.exporter.adapter.set_voice(self.voice)

                try:
                    sapi.Voice = self.exporter.adapter.sapi.Voice
                except Exception:
                    pass

            sapi.Rate = max(-10, min(10, int(self.rate)))
            sapi.Volume = max(0, min(100, int(self.volume)))

            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            stream.Open(tmp_path, 3, False)
            sapi.AudioOutputStream = stream
            sapi.Speak(chunk)
            stream.Close()
            sapi.AudioOutputStream = None
        finally:
            pythoncom.CoUninitialize()

    def run(self):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import tempfile
        import wave

        try:
            chunks = self._split_chunks(self.text)
            total = len(chunks)
            tmp_paths = []
            futures_idx = {}

            workers = min(self.MAX_WORKERS, total)

            with ThreadPoolExecutor(max_workers=workers) as pool:
                for index, chunk in enumerate(chunks):
                    tmp = tempfile.mktemp(suffix=f"_{index}.wav")
                    tmp_paths.append((index, tmp))
                    fut = pool.submit(self._synth_chunk, chunk, tmp)
                    futures_idx[fut] = (index, tmp)

                done = 0

                for fut in as_completed(futures_idx):
                    fut.result()
                    done += 1
                    self.export_progress.emit(int(done * 100 / total))

            ordered = sorted(tmp_paths, key=lambda x: x[0])
            first = True

            with wave.open(self.path, "wb") as out:
                for _, tmp in ordered:
                    with wave.open(tmp, "rb") as wav_in:
                        if first:
                            out.setnchannels(wav_in.getnchannels())
                            out.setsampwidth(wav_in.getsampwidth())
                            out.setframerate(wav_in.getframerate())
                            first = False

                        out.writeframes(wav_in.readframes(wav_in.getnframes()))

                    Path(tmp).unlink(missing_ok=True)

            self.export_ok.emit(self.path)
        except Exception as exc:
            self.export_error.emit(str(exc))


'''
    text = text[:start] + new_worker + text[end:]

path.write_text(text, encoding="utf-8")
print("Sintesis paralela con 4 hilos lista.")
