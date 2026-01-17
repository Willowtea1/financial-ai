import os
import re
from pathlib import Path
from typing import Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

playbook_cache = None
vectorizer = None
playbook_chunks = None
chunk_vectors = None

def load_playbook():
    """Load and cache the financial playbook markdown file."""
    global playbook_cache
    if playbook_cache:
        return playbook_cache

    try:
        current_dir = Path(__file__).parent
        playbook_path = current_dir.parent / "data" / "financial-playbook.md"
        with open(playbook_path, "r", encoding="utf-8") as f:
            playbook_cache = f.read()
        return playbook_cache
    except Exception as error:
        print(f"Error loading playbook: {error}")
        return ""

def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 300):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        # Try to break at sentence boundaries
        if end < len(text):
            # Look for sentence endings near the chunk boundary
            for punct in ['. ', '\n\n', '##']:
                last_punct = text.rfind(punct, start, end)
                if last_punct > start:
                    end = last_punct + len(punct)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break

    return chunks

def initialize_vectorizer():
    """Initialize TF-IDF vectorizer and create embeddings for playbook chunks."""
    global vectorizer, playbook_chunks, chunk_vectors
    
    if vectorizer is not None:
        return  # Already initialized
    
    playbook = load_playbook()
    if not playbook:
        return
    
    # Chunk the playbook
    playbook_chunks = chunk_text(playbook, chunk_size=1500, overlap=300)
    
    if not playbook_chunks:
        return
    
    # Initialize TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=500,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95
    )
    
    # Create embeddings for all chunks
    try:
        chunk_vectors = vectorizer.fit_transform(playbook_chunks)
    except Exception as e:
        print(f"Error creating vectors: {e}")
        vectorizer = None

def calculate_keyword_relevance(chunk: str, user_answers: Dict) -> float:
    """Calculate relevance score based on keyword matching."""
    chunk_lower = chunk.lower()
    score = 0.0

    # Check for relevant keywords based on user answers
    if user_answers.get("aboutYou"):
        about_you_lower = user_answers["aboutYou"].lower()
        if about_you_lower in chunk_lower:
            score += 5.0
        if about_you_lower == "student" and "student" in chunk_lower:
            score += 3.0
        if about_you_lower == "retired" and "retirement" in chunk_lower:
            score += 3.0
        if about_you_lower == "business owner" and "business" in chunk_lower:
            score += 3.0

    if user_answers.get("income"):
        income = user_answers["income"]
        if "36,000" in income or "0-" in income or "0–" in income:
            if "low income" in chunk_lower or "budget" in chunk_lower:
                score += 3.0
        if "100,000+" in income:
            if "high income" in chunk_lower or "investment" in chunk_lower:
                score += 3.0

    if user_answers.get("debt"):
        debt_lower = user_answers["debt"].lower()
        if debt_lower in chunk_lower:
            score += 4.0
        if debt_lower != "none" and "debt" in chunk_lower:
            score += 2.0

    if user_answers.get("savings"):
        savings = user_answers["savings"]
        if savings == "0" and "emergency fund" in chunk_lower:
            score += 3.0
        if "50k+" in savings and "investment" in chunk_lower:
            score += 3.0

    if user_answers.get("riskTolerance"):
        risk_lower = user_answers["riskTolerance"].lower()
        if risk_lower in chunk_lower:
            score += 3.0
        if risk_lower == "low" and "conservative" in chunk_lower:
            score += 2.0
        if risk_lower == "high" and "aggressive" in chunk_lower:
            score += 2.0

    return score

def create_query_vector(user_answers: Dict) -> str:
    """Create a query string from user answers for semantic search."""
    query_parts = []
    
    if user_answers.get("aboutYou"):
        query_parts.append(user_answers["aboutYou"])
    if user_answers.get("income"):
        query_parts.append(f"income {user_answers['income']}")
    if user_answers.get("expenses"):
        query_parts.append(f"expenses {user_answers['expenses']}")
    if user_answers.get("debt"):
        query_parts.append(f"debt {user_answers['debt']}")
    if user_answers.get("savings"):
        query_parts.append(f"savings {user_answers['savings']}")
    if user_answers.get("riskTolerance"):
        query_parts.append(f"risk tolerance {user_answers['riskTolerance']}")
    
    return " ".join(query_parts)

async def get_relevant_context(user_answers: Dict):
    """Get relevant context from playbook using RAG (TF-IDF + cosine similarity + keyword matching)."""
    global vectorizer, playbook_chunks, chunk_vectors
    
    # Initialize vectorizer if not already done
    initialize_vectorizer()
    
    if not playbook_chunks or vectorizer is None:
        return "Standard financial planning guidance."
    
    # Create query from user answers
    query_text = create_query_vector(user_answers)
    
    try:
        # Vectorize the query
        query_vector = vectorizer.transform([query_text])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, chunk_vectors).flatten()
        
        # Combine semantic similarity with keyword relevance
        combined_scores = []
        for i, chunk in enumerate(playbook_chunks):
            semantic_score = float(similarities[i])
            keyword_score = calculate_keyword_relevance(chunk, user_answers)
            # Normalize keyword score (max is around 20)
            normalized_keyword = keyword_score / 20.0
            # Weighted combination: 70% semantic, 30% keyword
            combined_score = 0.7 * semantic_score + 0.3 * normalized_keyword
            combined_scores.append((combined_score, chunk))
        
        # Sort by combined score and take top 5
        combined_scores.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [chunk for score, chunk in combined_scores[:5] if score > 0.1]
        
        # Fallback to top 3 if no good matches
        if not top_chunks:
            top_chunks = [chunk for _, chunk in combined_scores[:3]]
        
        # Combine top chunks
        context = "\n\n---\n\n".join(top_chunks)
        
        return context if context else "Standard financial planning guidance."
        
    except Exception as e:
        print(f"Error in RAG retrieval: {e}")
        # Fallback to keyword-based retrieval
        scored_chunks = [
            (calculate_keyword_relevance(chunk, user_answers), chunk)
            for chunk in playbook_chunks
        ]
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [chunk for score, chunk in scored_chunks[:5] if score > 0]
        
        if not top_chunks:
            top_chunks = playbook_chunks[:3]
        
        return "\n\n---\n\n".join(top_chunks)
