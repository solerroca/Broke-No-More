"""Knowledge base management with vector storage and retrieval."""

import os
import streamlit as st
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional, Tuple
from config.settings import settings
from src.utils import chunk_text, get_file_hash


class KnowledgeBase:
    """Manages the knowledge base using ChromaDB for vector storage."""
    
    def __init__(self):
        """Initialize the knowledge base."""
        self.collection_name = "finance_docs"
        self.embedding_model = self._load_embedding_model()
        self.client = self._initialize_chroma_client()
        self.collection = self._get_or_create_collection()
    
    @st.cache_resource
    def _load_embedding_model(_self):
        """Load the sentence transformer model for embeddings."""
        try:
            return SentenceTransformer(settings.EMBEDDING_MODEL)
        except Exception as e:
            st.error(f"Failed to load embedding model: {str(e)}")
            return None
    
    def _initialize_chroma_client(self) -> chromadb.Client:
        """Initialize ChromaDB client."""
        os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
        
        client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_DIR,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        return client
    
    def _get_or_create_collection(self):
        """Get or create the ChromaDB collection."""
        try:
            return self.client.get_collection(name=self.collection_name)
        except:
            return self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Financial documents and advice"}
            )
    
    def add_document(self, content: str, filename: str, file_type: str = "text") -> bool:
        """Add a document to the knowledge base."""
        try:
            if not content.strip():
                st.warning("Document content is empty")
                return False
            
            if self.embedding_model is None:
                st.error("Embedding model not available")
                return False
            
            # Create chunks from the content
            chunks = chunk_text(content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
            
            # Generate unique IDs and metadata
            doc_hash = get_file_hash(content.encode())
            
            # Check if document already exists
            if self.document_exists(doc_hash):
                st.warning(f"Document '{filename}' already exists in the knowledge base")
                return False
            
            ids = []
            metadatas = []
            documents = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_hash}_chunk_{i}"
                ids.append(chunk_id)
                documents.append(chunk)
                metadatas.append({
                    "filename": filename,
                    "file_type": file_type,
                    "doc_hash": doc_hash,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(documents).tolist()
            
            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            st.success(f"Successfully added '{filename}' to knowledge base ({len(chunks)} chunks)")
            return True
            
        except Exception as e:
            st.error(f"Error adding document to knowledge base: {str(e)}")
            return False
    
    def search_documents(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search for relevant documents based on the query."""
        try:
            if self.embedding_model is None:
                return []
            
            if top_k is None:
                top_k = settings.TOP_K_RESULTS
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Convert distance to similarity (ChromaDB uses cosine distance)
                    similarity = 1 - distance
                    
                    if similarity >= settings.SIMILARITY_THRESHOLD:
                        formatted_results.append({
                            'content': doc,
                            'filename': metadata['filename'],
                            'file_type': metadata['file_type'],
                            'similarity': similarity,
                            'chunk_index': metadata.get('chunk_index', 0)
                        })
            
            return formatted_results
            
        except Exception as e:
            st.error(f"Error searching documents: {str(e)}")
            return []
    
    def document_exists(self, doc_hash: str) -> bool:
        """Check if a document already exists in the knowledge base."""
        try:
            results = self.collection.get(
                where={"doc_hash": doc_hash},
                limit=1
            )
            return len(results['ids']) > 0
        except:
            return False
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents in the knowledge base."""
        try:
            results = self.collection.get(include=["metadatas"])
            
            # Group by document (doc_hash) to avoid duplicates from chunks
            docs_dict = {}
            for metadata in results['metadatas']:
                doc_hash = metadata['doc_hash']
                if doc_hash not in docs_dict:
                    docs_dict[doc_hash] = {
                        'filename': metadata['filename'],
                        'file_type': metadata['file_type'],
                        'doc_hash': doc_hash,
                        'total_chunks': metadata.get('total_chunks', 1)
                    }
            
            return list(docs_dict.values())
            
        except Exception as e:
            st.error(f"Error retrieving documents: {str(e)}")
            return []
    
    def delete_document(self, doc_hash: str) -> bool:
        """Delete a document and all its chunks from the knowledge base."""
        try:
            # Get all chunk IDs for this document
            results = self.collection.get(
                where={"doc_hash": doc_hash},
                include=["metadatas"]
            )
            
            if not results['ids']:
                st.warning("Document not found")
                return False
            
            # Delete all chunks
            self.collection.delete(where={"doc_hash": doc_hash})
            
            filename = results['metadatas'][0]['filename'] if results['metadatas'] else "Unknown"
            st.success(f"Successfully deleted '{filename}' from knowledge base")
            return True
            
        except Exception as e:
            st.error(f"Error deleting document: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        try:
            all_docs = self.get_all_documents()
            total_chunks = self.collection.count()
            
            return {
                'total_documents': len(all_docs),
                'total_chunks': total_chunks,
                'file_types': list(set(doc['file_type'] for doc in all_docs))
            }
        except Exception as e:
            st.error(f"Error getting stats: {str(e)}")
            return {'total_documents': 0, 'total_chunks': 0, 'file_types': []}
    
    def clear_all(self) -> bool:
        """Clear all documents from the knowledge base."""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self._get_or_create_collection()
            st.success("Knowledge base cleared successfully")
            return True
        except Exception as e:
            st.error(f"Error clearing knowledge base: {str(e)}")
            return False


# Global knowledge base instance
@st.cache_resource
def get_knowledge_base() -> KnowledgeBase:
    """Get a cached knowledge base instance."""
    return KnowledgeBase() 