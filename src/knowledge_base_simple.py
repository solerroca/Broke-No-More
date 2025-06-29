"""Simplified knowledge base management with basic text search."""

import os
import json
import streamlit as st
from typing import List, Dict, Any, Optional
from config.settings import settings
from src.utils import chunk_text, get_file_hash


class SimpleKnowledgeBase:
    """Manages the knowledge base using simple text search and JSON storage."""
    
    def __init__(self):
        """Initialize the knowledge base."""
        self.data_file = os.path.join(settings.KNOWLEDGE_BASE_DIR, "knowledge_base.json")
        self.documents = self._load_documents()
    
    def _load_documents(self) -> List[Dict[str, Any]]:
        """Load documents from JSON file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            st.error(f"Error loading documents: {str(e)}")
            return []
    
    def _save_documents(self) -> bool:
        """Save documents to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"Error saving documents: {str(e)}")
            return False
    
    def add_document(self, content: str, filename: str, file_type: str = "text") -> bool:
        """Add a document to the knowledge base."""
        try:
            if not content.strip():
                st.warning("Document content is empty")
                return False
            
            # Create chunks from the content
            chunks = chunk_text(content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
            
            # Generate unique ID
            doc_hash = get_file_hash(content.encode())
            
            # Check if document already exists
            if self.document_exists(doc_hash):
                st.warning(f"Document '{filename}' already exists in the knowledge base")
                return False
            
            # Add document with chunks
            document = {
                'filename': filename,
                'file_type': file_type,
                'doc_hash': doc_hash,
                'content': content,
                'chunks': chunks,
                'total_chunks': len(chunks)
            }
            
            self.documents.append(document)
            
            if self._save_documents():
                st.success(f"Successfully added '{filename}' to knowledge base ({len(chunks)} chunks)")
                return True
            else:
                # Remove from memory if save failed
                self.documents.pop()
                return False
                
        except Exception as e:
            st.error(f"Error adding document to knowledge base: {str(e)}")
            return False
    
    def search_documents(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search for relevant documents based on the query using simple text matching."""
        try:
            if top_k is None:
                top_k = settings.TOP_K_RESULTS
            
            query_lower = query.lower()
            query_words = set(query_lower.split())
            
            # Score each chunk based on word overlap
            scored_chunks = []
            
            for doc in self.documents:
                for i, chunk in enumerate(doc['chunks']):
                    chunk_lower = chunk.lower()
                    chunk_words = set(chunk_lower.split())
                    
                    # Calculate simple relevance score
                    # Count exact query appearances
                    exact_matches = chunk_lower.count(query_lower)
                    
                    # Count word overlaps
                    word_overlap = len(query_words.intersection(chunk_words))
                    
                    # Calculate score (prioritize exact matches)
                    score = exact_matches * 3 + word_overlap
                    
                    if score > 0:
                        scored_chunks.append({
                            'content': chunk,
                            'filename': doc['filename'],
                            'file_type': doc['file_type'],
                            'similarity': min(score / (len(query_words) + 3), 1.0),  # Normalize to 0-1
                            'chunk_index': i,
                            'score': score
                        })
            
            # Sort by score and return top results
            scored_chunks.sort(key=lambda x: x['score'], reverse=True)
            
            # Filter by similarity threshold and return top_k
            results = []
            for chunk in scored_chunks[:top_k]:
                if chunk['similarity'] >= settings.SIMILARITY_THRESHOLD / 2:  # Lower threshold for text search
                    results.append(chunk)
            
            return results
            
        except Exception as e:
            st.error(f"Error searching documents: {str(e)}")
            return []
    
    def document_exists(self, doc_hash: str) -> bool:
        """Check if a document already exists in the knowledge base."""
        return any(doc['doc_hash'] == doc_hash for doc in self.documents)
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents in the knowledge base."""
        try:
            return [{
                'filename': doc['filename'],
                'file_type': doc['file_type'],
                'doc_hash': doc['doc_hash'],
                'total_chunks': doc.get('total_chunks', 1)
            } for doc in self.documents]
        except Exception as e:
            st.error(f"Error retrieving documents: {str(e)}")
            return []
    
    def delete_document(self, doc_hash: str) -> bool:
        """Delete a document from the knowledge base."""
        try:
            original_length = len(self.documents)
            self.documents = [doc for doc in self.documents if doc['doc_hash'] != doc_hash]
            
            if len(self.documents) < original_length:
                if self._save_documents():
                    st.success("Document deleted successfully")
                    return True
                else:
                    # Restore documents if save failed
                    self.documents = self._load_documents()
                    return False
            else:
                st.warning("Document not found")
                return False
                
        except Exception as e:
            st.error(f"Error deleting document: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        try:
            total_chunks = sum(doc.get('total_chunks', 1) for doc in self.documents)
            file_types = list(set(doc['file_type'] for doc in self.documents)) if self.documents else []
            
            return {
                'total_documents': len(self.documents),
                'total_chunks': total_chunks,
                'file_types': file_types
            }
        except Exception as e:
            st.error(f"Error getting stats: {str(e)}")
            return {'total_documents': 0, 'total_chunks': 0, 'file_types': []}
    
    def clear_all(self) -> bool:
        """Clear all documents from the knowledge base."""
        try:
            self.documents = []
            if self._save_documents():
                st.success("Knowledge base cleared successfully")
                return True
            return False
        except Exception as e:
            st.error(f"Error clearing knowledge base: {str(e)}")
            return False


# Global knowledge base instance
@st.cache_resource
def get_simple_knowledge_base() -> SimpleKnowledgeBase:
    """Get a cached simple knowledge base instance."""
    return SimpleKnowledgeBase() 