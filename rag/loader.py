import os
import json
from typing import List, Dict
import fitz  # PyMuPDF
from rag.chunker import split_into_paragraphs, semantic_chunk, chunk_text


def load_pdf_mupdf(DOCUMENT_PATH: str) -> List[Dict]:
    doc = fitz.open(DOCUMENT_PATH)
    all_chunks = []

    for pno in range(len(doc)):
        page = doc.load_page(pno)
        text = page.get_text("text")
        if not text:
            continue

        paragraphs = split_into_paragraphs(text)
        page_chunks = semantic_chunk(paragraphs)

        for c in page_chunks:
            c["page"] = pno + 1
            all_chunks.append(c)

    for i, c in enumerate(all_chunks):
        c["chunk_id"] = i

    return all_chunks


def load_jsonl_documents(DOCUMENT_PATH: str) -> List[Dict]:
    """
    Load JSONL dengan struktur yang konsisten:
    - text: konten chunk
    - page: None (untuk JSONL)
    - chunk_id: global unik
    - metadata: dict dengan name, difficulty, technologies, dll
    """
    if not os.path.exists(DOCUMENT_PATH):
        print(f"⚠️  Warning: JSONL file not found at {DOCUMENT_PATH}")
        return []
    
    docs = []
    global_chunk_id = 0  

    try:
        with open(DOCUMENT_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                    
                    # Chunk text dari combined_text
                    chunks = chunk_text(item["combined_text"])

                    # Build dokumen dengan struktur konsisten
                    for c in chunks:
                        docs.append({
                            "text": c["text"],
                            "page": None,  # JSONL tidak punya page number
                            "chunk_id": global_chunk_id,
                            "metadata": {
                                "name": item.get("name", "Unknown"),
                                "summary": item.get("summary", ""),
                                "description": item.get("description", ""),
                                "difficulty": item.get("course_difficulty", "N/A"),
                                "technologies": item.get("technologies", []),
                            }
                        })
                        global_chunk_id += 1
                except json.JSONDecodeError as e:
                    print(f"⚠️  Skipping invalid JSON line: {e}")
                    continue
    except Exception as e:
        print(f"⚠️  Error reading JSONL file: {e}")
        return []

    return docs

def load_documents(DOCUMENT_PATH: str) -> List[Dict]:
    """
    Load dokumen dari berbagai format.
    Return format standar:
    {
        "text": str,
        "page": int | None,
        "chunk_id": int,
        "metadata": dict (optional, hanya untuk JSONL)
    }
    """
    ext = os.path.splitext(DOCUMENT_PATH)[1].lower()

    if ext == ".pdf":
        return load_pdf_mupdf(DOCUMENT_PATH)

    elif ext == ".jsonl":
        return load_jsonl_documents(DOCUMENT_PATH)

    else:
        raise ValueError(f"Format file {ext} not supported")