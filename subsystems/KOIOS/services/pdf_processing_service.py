from pathlib import Path
from typing import List, Dict, Any, Optional

# Preferred library: PyMuPDF (requires `pip install pymupdf`)
# Alternative: pdfminer.six (requires `pip install pdfminer.six`)
try:
    import fitz # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    # TODO: Add fallback or explicit dependency error

# Text chunking library (e.g., langchain or simple implementation)
# from langchain.text_splitter import RecursiveCharacterTextSplitter

from koios.logger import KoiosLogger
logger = KoiosLogger.get_logger("KOIOS.PdfProcessingService")

class PdfProcessingService:
    """Handles extraction and chunking of text and metadata from PDF documents."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        # Default chunking parameters (can be overridden via config)
        self.chunk_size = self.config.get("chunking", {}).get("chunk_size", 1000)
        self.chunk_overlap = self.config.get("chunking", {}).get("chunk_overlap", 150)

        if not HAS_PYMUPDF:
             logger.warning("PyMuPDF (fitz) not found. PDF text/metadata extraction will be limited.")
        # TODO: Initialize OCR if needed (e.g., pytesseract)
        # TODO: Initialize text splitter (e.g., Langchain's RecursiveCharacterTextSplitter)
        # self.text_splitter = RecursiveCharacterTextSplitter(
        #     chunk_size=self.chunk_size,
        #     chunk_overlap=self.chunk_overlap,
        #     length_function=len,
        # )

    def extract_text(self, pdf_path: Path) -> Optional[str]:
        """Extracts plain text content from a PDF file."""
        if not HAS_PYMUPDF:
            logger.error("Cannot extract text: PyMuPDF (fitz) is not installed.")
            return None
        if not pdf_path.exists() or pdf_path.suffix.lower() != '.pdf':
            logger.error(f"Invalid or non-PDF path provided: {pdf_path}")
            return None

        text_content = ""
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += page.get_text("text") # Basic text extraction
                text_content += "\n\n" # Add page break separator
            doc.close()
            logger.info(f"Successfully extracted text from {pdf_path.name} ({len(text_content)} chars)")
            return text_content
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}", exc_info=True)
            # TODO: Consider attempting OCR fallback here if text extraction fails
            return None

    def extract_metadata(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        """Extracts metadata (author, title, pages, etc.) from a PDF file."""
        if not HAS_PYMUPDF:
            logger.error("Cannot extract metadata: PyMuPDF (fitz) is not installed.")
            return None
        if not pdf_path.exists() or pdf_path.suffix.lower() != '.pdf':
            logger.error(f"Invalid or non-PDF path provided: {pdf_path}")
            return None

        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata or {}
            metadata['page_count'] = len(doc) # Add page count
            # Clean up potentially null bytes in metadata values
            cleaned_metadata = {}
            for k, v in metadata.items():
                if isinstance(v, str):
                    cleaned_metadata[k] = v.replace("\x00", "")
                else:
                    cleaned_metadata[k] = v
            doc.close()
            logger.info(f"Successfully extracted metadata from {pdf_path.name}")
            return cleaned_metadata
        except Exception as e:
            logger.error(f"Failed to extract metadata from {pdf_path}: {e}", exc_info=True)
            return None

    def chunk_text(self, text: str) -> List[str]:
        """Splits a large text into smaller chunks based on configured size/overlap."""
        if not text:
            return []

        # TODO: Replace placeholder with actual text splitter implementation
        # if self.text_splitter:
        #    return self.text_splitter.split_text(text)
        # else:
        #    logger.warning("Text splitter not initialized. Using simple placeholder chunking.")

        # Simple Placeholder Chunking:
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            # Move start forward, considering overlap (simple version)
            start += self.chunk_size - self.chunk_overlap
            if start >= len(text) and end < len(text): # Ensure last part isn't missed
                chunks.append(text[start:])
                break
            elif start >= end: # Avoid infinite loop if overlap >= size
                 start = end
        logger.debug(f"Split text into {len(chunks)} chunks (size={self.chunk_size}, overlap={self.chunk_overlap})")
        return chunks

    def process_pdf(self, pdf_path: Path) -> Optional[List[Dict[str, Any]]]:
        """Processes a PDF: extracts metadata, text, and chunks the text.

        Returns:
            A list of dictionaries, where each dict represents a chunk
            containing the chunk text and associated metadata, or None on failure.
        """
        logger.info(f"Processing PDF: {pdf_path.name}")
        metadata = self.extract_metadata(pdf_path)
        full_text = self.extract_text(pdf_path)

        if metadata is None or full_text is None:
            logger.error(f"Failed to extract metadata or text from {pdf_path.name}. Aborting processing.")
            return None

        text_chunks = self.chunk_text(full_text)

        processed_chunks = []
        for i, chunk in enumerate(text_chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata["source_file"] = str(pdf_path) # Store original path
            chunk_metadata["chunk_index"] = i
            # TODO: Add more sophisticated metadata (e.g., page numbers if available)
            processed_chunks.append({
                "page_content": chunk,
                "metadata": chunk_metadata
            })

        logger.info(f"Successfully processed {pdf_path.name} into {len(processed_chunks)} chunks.")
        return processed_chunks

    # TODO: Add methods for handling OCR for image-based PDFs
