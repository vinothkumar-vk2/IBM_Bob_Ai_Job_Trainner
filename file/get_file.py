import os
from pathlib import Path
from typing import Optional

class File:
    """Document loader and reader for Resumes and Job Descriptions."""
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def read_file(self, path: Optional[str] = None) -> str:
        """Reads content from txt, pdf, docx or markdown files."""
        target_path = Path(path or self.file_path)
        if not target_path.exists():
            raise FileNotFoundError(f"File not found: {target_path}")

        suffix = target_path.suffix.lower()

        if suffix in [".txt", ".md", ".json", ".csv"]:
            with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()

        elif suffix == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(str(target_path))
                text = ""
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
                return text.strip()
            except Exception as e:
                print(f"[File] Error parsing PDF with pypdf: {e}")
                # Fallback binary read
                with open(target_path, "rb") as f:
                    raw = f.read()
                    return raw.decode("latin-1", errors="ignore")

        elif suffix in [".docx", ".doc"]:
            try:
                import docx
                doc = docx.Document(str(target_path))
                return "\n".join([p.text for p in doc.paragraphs if p.text])
            except Exception:
                with open(target_path, "rb") as f:
                    return f.read().decode("latin-1", errors="ignore")

        else:
            with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()