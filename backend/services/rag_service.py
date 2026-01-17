import os
import re
from pathlib import Path
from typing import Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

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
        logger.info(f"Attempting to load playbook from: {playbook_path}")
        
        if not playbook_path.exists():
            logger.warning(f"Playbook file not found at {playbook_path}")
            return ""
            
        with open(playbook_path, "r", encoding="utf-8") as f:
            playbook_cache = f.read()
        logger.info(f"Playbook loaded successfully: {len(playbook_cache)} characters")
        return playbook_cache
    except Exception as error:
        logger.error(f"Error loading playbook: {error}")
        return ""

def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 300):
    """Split text into chunks by markdown sections."""
    logger.info(f"Starting chunk_text with text length: {len(text)}")
    
    # Simple approach: split by ## headers
    sections = text.split('\n## ')
    chunks = []
    
    for i, section in enumerate(sections):
        if i > 0:
            section = '## ' + section  # Add back the header
        section = section.strip()
        if section:
            chunks.append(section)
    
    logger.info(f"Chunking complete: created {len(chunks)} chunks")
    return chunks

def initialize_vectorizer():
    """Initialize TF-IDF vectorizer and create embeddings for playbook chunks."""
    global vectorizer, playbook_chunks, chunk_vectors
    
    if vectorizer is not None:
        logger.info("Vectorizer already initialized")
        return  # Already initialized
    
    logger.info("Initializing vectorizer...")
    playbook = load_playbook()
    if not playbook:
        logger.warning("No playbook content loaded")
        return
    
    # Chunk the playbook
    playbook_chunks = chunk_text(playbook, chunk_size=1500, overlap=300)
    logger.info(f"Created {len(playbook_chunks)} chunks from playbook")
    
    if not playbook_chunks:
        logger.warning("No chunks created from playbook")
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
        logger.info(f"Vectorizer initialized successfully with {chunk_vectors.shape} vectors")
    except Exception as e:
        logger.error(f"Error creating vectors: {e}", exc_info=True)
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
    
    logger.info("Starting get_relevant_context")
    
    # Initialize vectorizer if not already done
    initialize_vectorizer()
    
    if not playbook_chunks or vectorizer is None:
        logger.warning("No playbook chunks or vectorizer available, returning default guidance")
        return "Provide comprehensive financial planning advice based on Malaysian context, including EPF contributions, tax planning, and local investment options."
    
    # Create query from user answers
    query_text = create_query_vector(user_answers)
    logger.info(f"Query text: {query_text}")
    
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
        
        logger.info(f"Context retrieved: {len(context)} characters from {len(top_chunks)} chunks")
        return context if context else "Standard financial planning guidance."
        
    except Exception as e:
        logger.error(f"Error in RAG retrieval: {e}", exc_info=True)
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
