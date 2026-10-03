import os
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader
from config import SYLLABUS_DIR


def load_txt_file(file_path: Path) -> str:
    """Reads content from a text file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""


def load_pdf_file(file_path: Path) -> str:
    """Extracts text content from a PDF file using pypdf."""
    try:
        reader = PdfReader(str(file_path))
        text_parts = [page.extract_text() for page in reader.pages if page.extract_text()]
        return "\n".join(text_parts)
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return ""


def chunk_text(text: str, source: str, chunk_size: int = 400, overlap: int = 50) -> List[Dict[str, Any]]:
    """Splits raw text into small chunks with source metadata."""
    if not text.strip():
        return []
    
    chunks = []
    # Split by double newlines to respect paragraphs first, then group
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    current_chunk = ""
    
    for p in paragraphs:
        if len(current_chunk) + len(p) <= chunk_size:
            current_chunk += ("\n\n" if current_chunk else "") + p
        else:
            if current_chunk:
                chunks.append({"text": current_chunk, "source": source})
            current_chunk = p
    
    if current_chunk:
        chunks.append({"text": current_chunk, "source": source})
        
    return chunks


def load_syllabus_documents(syllabus_dir: Path = SYLLABUS_DIR) -> List[Dict[str, Any]]:
    """Scans syllabus folder for txt/pdf files and returns all text chunks."""
    all_chunks = []
    if not syllabus_dir.exists():
        return all_chunks

    for entry in syllabus_dir.iterdir():
        if entry.is_file():
            source_name = entry.name
            raw_text = ""
            if entry.suffix.lower() == ".txt":
                raw_text = load_txt_file(entry)
            elif entry.suffix.lower() == ".pdf":
                raw_text = load_pdf_file(entry)
            
            if raw_text:
                file_chunks = chunk_text(raw_text, source=source_name)
                all_chunks.extend(file_chunks)

    return all_chunks
