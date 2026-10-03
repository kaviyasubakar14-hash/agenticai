import re
from typing import List, Dict, Any
from rag.loader import load_syllabus_documents


def tokenize(text: str) -> set:
    """Converts text into lowercase word tokens."""
    words = re.findall(r'\w+', text.lower())
    # Exclude trivial stop words for better keyword scoring
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'with', 'by', 'what', 'how', 'explain'}
    return {w for w in words if w not in stop_words and len(w) > 1}


def score_chunk(query_tokens: set, chunk_text: str) -> float:
    """Calculates term overlap score between query tokens and chunk text."""
    chunk_tokens = tokenize(chunk_text)
    if not chunk_tokens or not query_tokens:
        return 0.0
    overlap = query_tokens.intersection(chunk_tokens)
    return len(overlap) / (len(query_tokens) ** 0.5)


def retrieve_syllabus_context(query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Retrieves the most relevant syllabus text chunks for a given query.
    Returns dict with found status, combined context, and sources list.
    """
    chunks = load_syllabus_documents()
    if not chunks or not query.strip():
        return {"found": False, "context": "", "sources": []}

    query_tokens = tokenize(query)
    if not query_tokens:
        return {"found": False, "context": "", "sources": []}

    scored_chunks = []
    for chunk in chunks:
        s = score_chunk(query_tokens, chunk["text"])
        if s > 0:
            scored_chunks.append((s, chunk))

    # Sort by highest score
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    top_results = scored_chunks[:top_k]

    if not top_results:
        return {"found": False, "context": "", "sources": []}

    context_parts = []
    sources = set()

    for score, chunk in top_results:
        context_parts.append(chunk["text"])
        sources.add(chunk["source"])

    combined_context = "\n---\n".join(context_parts)
    return {
        "found": True,
        "context": combined_context,
        "sources": list(sources)
    }
