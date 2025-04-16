from typing import List, Dict, Any, Optional, Tuple
import numpy as np # Add numpy for array handling

# Embedding Models: sentence-transformers requires `pip install sentence-transformers`
# Vector DBs: Choose one like FAISS (`pip install faiss-cpu` or `faiss-gpu`), ChromaDB (`pip install chromadb`)

try:
    from sentence_transformers import SentenceTransformer
    HAS_SBERT = True
except ImportError:
    HAS_SBERT = False

# Example: Using ChromaDB
try:
    import chromadb
    from chromadb.utils import embedding_functions
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False

from koios.logger import KoiosLogger
logger = KoiosLogger.get_logger("KOIOS.SemanticSearchService")

class SemanticSearchService:
    """Handles text embedding, indexing, and semantic search."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.embedding_model = None
        self.vector_db_client = None
        self.collection = None

        model_name = self.config.get('embedding_model_name', 'all-MiniLM-L6-v2')
        if HAS_SBERT:
            try:
                # Use sentence-transformers embedding function if ChromaDB is used
                if HAS_CHROMA:
                     # ChromaDB's helper function handles model loading
                     self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
                     self.embedding_model = self.embedding_function # Keep a ref if needed elsewhere
                     logger.info(f"Initialized ChromaDB SentenceTransformer embedding function: {model_name}")
                else:
                     # Load model directly if not using Chroma's helper (e.g., for FAISS)
                     self.embedding_model = SentenceTransformer(model_name)
                     logger.info(f"Initialized SentenceTransformer model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load embedding model '{model_name}': {e}", exc_info=True)
                self.embedding_model = None
        else:
            logger.warning("sentence-transformers library not found. Embeddings disabled.")

        # Initialize Vector DB (Example: ChromaDB persistent client)
        if HAS_CHROMA:
            try:
                db_path = self.config.get("vector_db_path", "./vector_db_storage")
                collection_name = self.config.get("collection_name", "egos_documents")
                self.vector_db_client = chromadb.PersistentClient(path=db_path)
                # Get or create collection, using the sbert function for Chroma
                self.collection = self.vector_db_client.get_or_create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function if self.embedding_function else None
                )
                logger.info(f"Initialized ChromaDB client at '{db_path}' and collection '{collection_name}'.")
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB: {e}", exc_info=True)
                self.vector_db_client = None
                self.collection = None
        else:
            logger.warning("chromadb library not found. Vector indexing/search disabled.")
            # TODO: Add logic for FAISS or other vector stores if needed

    def embed_texts(self, texts: List[str]) -> Optional[List[List[float]]]:
        """Generates vector embeddings for a list of text chunks."""
        if not self.embedding_model or not hasattr(self.embedding_model, 'encode'):
            logger.error("Embedding model not available or invalid.")
            return None
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts...")
            embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
            # Convert numpy arrays to lists of floats for broader compatibility
            return embeddings.tolist() if isinstance(embeddings, np.ndarray) else embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}", exc_info=True)
            return None

    def index_processed_chunks(self, processed_chunks: List[Dict[str, Any]]):
        """Embeds, and indexes document chunks that have been processed (e.g., by PdfProcessingService)."""
        if not self.collection or not self.embedding_function:
            logger.error("Cannot index: Vector DB or embedding function not available.")
            return
        if not processed_chunks:
            logger.info("No processed chunks provided for indexing.")
            return

        texts_to_embed = [chunk['page_content'] for chunk in processed_chunks]
        metadatas = [chunk['metadata'] for chunk in processed_chunks]
        # Generate unique IDs for each chunk (e.g., filepath + chunk index)
        ids = [
            f"{chunk['metadata'].get('source_file', 'unknown')}_chunk{chunk['metadata'].get('chunk_index', i)}"
            for i, chunk in enumerate(processed_chunks)
        ]

        logger.info(f"Generating embeddings for {len(texts_to_embed)} chunks...")
        embeddings = self.embed_texts(texts_to_embed)

        if embeddings is None:
            logger.error("Failed to generate embeddings. Indexing aborted.")
            return

        if not (len(ids) == len(embeddings) == len(texts_to_embed) == len(metadatas)):
             logger.error("Mismatch in lengths of generated data for indexing. Indexing aborted.")
             return

        try:
            logger.info(f"Indexing {len(ids)} processed chunks...")
            # ChromaDB uses add method
            self.collection.add(
                embeddings=embeddings,
                documents=texts_to_embed, # Store original text chunk
                metadatas=metadatas, # Store source info, chunk index, etc.
                ids=ids # Unique ID for each chunk
            )
            logger.info(f"Successfully indexed {len(ids)} chunks.")
        except Exception as e:
            logger.error(f"Failed to index documents: {e}", exc_info=True)

    def search(self, query: str, top_k: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> Optional[List[Tuple[Dict[str, Any], float]]]:
        """Performs semantic search for a query (ChromaDB example)."""
        if not self.collection or not self.embedding_function:
            logger.error("Vector DB collection or embedding function not available for search.")
            return None

        try:
            logger.info(f"Performing semantic search for query: '{query}' (top_k={top_k})")
            # 1. Embed the query text (Handled by ChromaDB's query method with embedding_function)
            # 2. Search the index
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=filter_metadata, # Optional metadata filtering
                include=["metadatas", "distances"] # Request distances (lower is better) and metadata
            )

            # 3. Format results
            formatted_results: List[Tuple[Dict[str, Any], float]] = []
            if results and results.get('ids') and results.get('ids')[0]:
                ids = results['ids'][0]
                metadatas = results['metadatas'][0] if results.get('metadatas') else [{}] * len(ids)
                distances = results['distances'][0] if results.get('distances') else [0.0] * len(ids)

                for metadata, distance in zip(metadatas, distances):
                    # Convert distance to similarity score (e.g., 1 - distance for cosine)
                    similarity = 1.0 - distance
                    formatted_results.append((metadata, similarity))

            logger.info(f"Search completed. Found {len(formatted_results)} results.")
            return formatted_results

        except Exception as e:
            logger.error(f"Semantic search failed for query '{query}': {e}", exc_info=True)
            return None

    # TODO: Add text chunking logic HERE if not done upstream in PdfProcessingService
    # TODO: Add methods for index management (e.g., delete, update, get count)
    # TODO: Add support/abstraction for other vector stores (e.g., FAISS)
