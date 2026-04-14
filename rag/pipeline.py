import os
from rag.loader import load_documents
from rag.vectorstore import VectorStore
from rag.llm import ask_llm
from rag.classifier import classify_query
from rag.tracking import get_tracker
from rag.recommendation import get_recommendation_engine
from rag.history import get_history_manager
from rag.prompt_loader import load_prompt
from config import (
    DOCUMENT_PATH, 
    TOP_K, 
    RETRIEVE_MIN_SCORE, 
    MAX_CONTEXT_WORDS
)

INDEX_PATH = "faiss.index"
META_PATH = "faiss_meta.json"

# Lazy initialization - only load when needed
_vs = None
_vs_initialized = False


def _get_vectorstore():
    """Lazy load vector store on first use"""
    global _vs, _vs_initialized
    
    if _vs_initialized:
        return _vs
    
    try:
        if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
            _vs = VectorStore.load(INDEX_PATH, META_PATH)
        elif os.path.exists(DOCUMENT_PATH):
            docs = load_documents(DOCUMENT_PATH)
            _vs = VectorStore(docs)
            _vs.save(INDEX_PATH, META_PATH)
        else:
            print(f"⚠️  Warning: Data file not found at {DOCUMENT_PATH}. RAG will not work until data is provided.")
            _vs = None
    except Exception as e:
        print(f"⚠️  Warning: Failed to load vector store: {e}")
        _vs = None
    
    _vs_initialized = True
    return _vs



def _build_context(results):
    """Build context from search results with metadata"""
    parts = []
    total_words = 0
    
    for doc, score in results:
        text = doc["text"].strip()
        
        if "metadata" in doc and doc["metadata"]:
            meta = doc["metadata"]
            header = (
                f"[Kelas: {meta.get('name', 'Unknown')} | "
                f"Level: {meta.get('difficulty', 'N/A')} | "
                f"Teknologi: {', '.join(meta.get('technologies', [])[:3])} | "
                f"Score: {score:.3f}]\n"
            )
        else:
            header = f"[Page: {doc.get('page', 'N/A')} | Chunk: {doc.get('chunk_id', 'N/A')} | Score: {score:.3f}]\n"
        
        words = len(text.split())
        
        if total_words + words > MAX_CONTEXT_WORDS:
            allowed = max(0, MAX_CONTEXT_WORDS - total_words)
            if allowed <= 0:
                break
            truncated = " ".join(text.split()[:allowed])
            parts.append(header + truncated)
            total_words += allowed
            break
        
        parts.append(header + text)
        total_words += words
    
    return "\n\n".join(parts)


def rag_answer(query: str, session_id: str = None):
    """Answer learning queries using RAG"""
    vs = _get_vectorstore()
    
    if vs is None:
        return "Maaf, basis data pembelajaran belum tersedia. Silakan hubungi administrator untuk setup data."
    
    results = vs.search(query, k=TOP_K, min_score=RETRIEVE_MIN_SCORE)
    context = _build_context(results)
    
    # Add conversation history if session_id provided
    history_context = ""
    if session_id:
        history_manager = get_history_manager()
        history_context = history_manager.get_conversation_context(session_id, last_n=3)
    
    # Load system prompt from file
    system_prompt = load_prompt("learning")
    
    prompt = f"""
{history_context}

KONTEKS MATERI:
{context}

PERTANYAAN TERBARU:
{query}

JAWABAN:
"""
    
    return ask_llm(prompt, system_prompt=system_prompt)


def smart_answer(query: str, session_id: str = None) -> dict:
    """Main entry point that classifies query and routes to appropriate handler"""
    
    # Classify the query
    query_type = classify_query(query)
    
    # ✅ FIX: Pass session_id ke semua handler
    if query_type == "tracking":
        tracker = get_tracker()
        answer = tracker.answer_tracking_query(query, session_id=session_id)
    
    elif query_type == "recommendation":
        recommendation_engine = get_recommendation_engine()
        answer = recommendation_engine.answer_recommendation_query(query, session_id=session_id)
    
    else:  # learning
        answer = rag_answer(query, session_id=session_id)
    
    # Save to history if session_id provided
    if session_id:
        history_manager = get_history_manager()
        history_manager.save_message(
            session_id=session_id,
            query=query,
            answer=answer,
            query_type=query_type
        )
    
    return {
        "answer": answer,
        "type": query_type,
        "session_id": session_id
    }