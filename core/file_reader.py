from __future__ import annotations

import re
from pathlib import Path


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix in (".txt", ".md", ".log", ".csv"):
        return path.read_text(encoding="utf-8", errors="ignore")

    if suffix == ".docx":
        from docx import Document

        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)

    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)

    if suffix == ".rtf":
        raw = path.read_text(encoding="latin-1", errors="ignore")
        text = re.sub(r"\\[a-zA-Z]+-?\d*\s?", "", raw)
        text = re.sub(r"[{}]", "", text)
        return text

    if suffix in (".html", ".htm"):
        raw = path.read_text(encoding="utf-8", errors="ignore")
        text = re.sub(r"<[^>]+>", " ", raw)
        return re.sub(r"\s+", " ", text).strip()

    if suffix == ".doc":
        try:
            import comtypes.client

            word = comtypes.client.CreateObject("Word.Application")
            doc = word.Documents.Open(str(path))
            text = doc.Range().Text
            doc.Close(False)
            word.Quit()
            return text
        except Exception as exc:
            raise RuntimeError(
                "Para abrir .doc necesitas Microsoft Word instalado."
            ) from exc

    raise RuntimeError(f"Formato no soportado: {suffix}")
