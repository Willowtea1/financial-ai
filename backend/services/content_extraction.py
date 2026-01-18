"""
Content extraction service using Docling for advanced document understanding.
Extracts text content from PDFs, DOCX, PPTX, XLSX, images, and more.
"""
import io
import tempfile
import os
from typing import Optional
from docling.document_converter import DocumentConverter
import google.generativeai as genai
from config import get_settings


# Initialize Docling converter (reuse across requests)
_converter = None

def get_converter():
    """Get or create DocumentConverter instance."""
    global _converter
    if _converter is None:
        _converter = DocumentConverter()
    return _converter


async def extract_content(file_content: bytes, content_type: str, filename: str) -> str:
    """
    Extract text content from various file types using Docling.
    
    Docling supports:
    - PDF (with advanced layout understanding, tables, formulas)
    - DOCX, PPTX, XLSX
    - Images (PNG, TIFF, JPEG with OCR)
    - HTML, Markdown
    - And more
    
    Args:
        file_content: Raw file bytes
        content_type: MIME type of the file
        filename: Name of the file
        
    Returns:
        Extracted text content in Markdown format
    """
    try:
        converter = get_converter()
        
        # Docling works with file paths, so we need to write to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
        
        try:
            # Convert document using Docling
            result = converter.convert(tmp_file_path)
            
            # Export to Markdown format (clean, structured text)
            markdown_content = result.document.export_to_markdown()
            
            if not markdown_content or not markdown_content.strip():
                return f"[No content extracted from {filename}]"
            
            return markdown_content
            
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_file_path)
            except:
                pass
                
    except Exception as e:
        return f"[Error extracting content from {filename}: {str(e)}]"


async def extract_content_from_url(file_url: str) -> str:
    """
    Extract content directly from a URL using Docling.
    
    Args:
        file_url: URL of the document
        
    Returns:
        Extracted text content in Markdown format
    """
    try:
        converter = get_converter()
        result = converter.convert(file_url)
        markdown_content = result.document.export_to_markdown()
        
        if not markdown_content or not markdown_content.strip():
            return "[No content extracted from URL]"
        
        return markdown_content
        
    except Exception as e:
        return f"[Error extracting content from URL: {str(e)}]"


async def summarize_document(extracted_content: str, filename: str) -> str:
    """
    Summarize extracted document content using Gemini AI.
    Creates a concise summary focused on key financial information.
    
    Args:
        extracted_content: The full extracted text content
        filename: Name of the document
        
    Returns:
        Summarized content
    """
    try:
        settings = get_settings()
        genai.configure(api_key=settings.google_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create summarization prompt
        prompt = f"""
You are a financial document analyzer. Summarize the following document concisely, focusing on:
- Key financial figures (income, expenses, assets, liabilities, investments)
- Important dates and deadlines
- Account information and balances
- Financial goals or plans mentioned
- Any action items or recommendations

Document: {filename}

Content:
{extracted_content[:15000]}  # Limit to ~15k chars to avoid token limits

Provide a clear, structured summary in 200-300 words that captures the essential financial information.
"""
        
        response = model.generate_content(prompt)
        summary = response.text.strip()
        
        if not summary:
            return "[Unable to generate summary]"
        
        return summary
        
    except Exception as e:
        # If summarization fails, return a truncated version of the content
        print(f"Summarization failed: {str(e)}")
        # Return first 1000 characters as fallback
        return extracted_content[:1000] + "..." if len(extracted_content) > 1000 else extracted_content


