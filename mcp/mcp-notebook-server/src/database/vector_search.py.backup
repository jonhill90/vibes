"""
INMPARA Notebook Server - Vector Search
Handles semantic search using Qdrant vector database.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct

logger = logging.getLogger(__name__)


class VectorSearchEngine:
    """Qdrant-based vector search for semantic similarity."""
    
    def __init__(self, host: str = "localhost", port: int = 6334, 
                 collection_name: str = "inmpara_vault"):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.client = None
        self.embedding_model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Qdrant client and embedding model."""
        try:
            self.client = QdrantClient(host=self.host, port=self.port)
            self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            self._ensure_collection_exists()
            logger.info(f"Vector search engine initialized - Collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize vector search: {e}")
            raise
    
    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=384,  # all-MiniLM-L6-v2 dimension
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created new collection: {self.collection_name}")
            else:
                logger.info(f"Collection already exists: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text."""
        try:
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def add_note(self, note_data: Dict[str, Any]) -> bool:
        """Add a note to the vector index."""
        try:
            # Combine title and content for embedding
            text_content = f"{note_data.get('title', '')} {note_data.get('content', '')}"
            embedding = self.embed_text(text_content)
            
            # Create point with metadata
            point = PointStruct(
                id=note_data['id'],
                vector=embedding,
                payload={
                    "file_path": note_data.get('file_path'),
                    "title": note_data.get('title'),
                    "content_type": note_data.get('content_type'),
                    "domain": note_data.get('domain'),
                    "tags": note_data.get('tags', []),
                    "created_date": note_data.get('created_date'),
                    "confidence": note_data.get('confidence_score', 1.0),
                    "semantic_markup": note_data.get('semantic_markup', []),
                    "relations": note_data.get('relations', [])
                }
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"Added note to vector index: {note_data.get('title')}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding note to vector index: {e}")
            return False
    
    def search_semantic(self, query: str, filters: Dict[str, Any] = None, 
                       limit: int = 15, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Perform semantic similarity search."""
        try:
            # Generate query embedding
            query_embedding = self.embed_text(query)
            
            # Build filter conditions
            filter_conditions = []
            
            if filters:
                if 'content_types' in filters:
                    filter_conditions.append(
                        models.FieldCondition(
                            key="content_type",
                            match=models.MatchAny(any=filters['content_types'])
                        )
                    )
                
                if 'domains' in filters:
                    filter_conditions.append(
                        models.FieldCondition(
                            key="domain",
                            match=models.MatchAny(any=filters['domains'])
                        )
                    )
                
                if 'min_confidence' in filters:
                    filter_conditions.append(
                        models.FieldCondition(
                            key="confidence",
                            range=models.Range(gte=filters['min_confidence'])
                        )
                    )
                
                if 'tags' in filters:
                    filter_conditions.append(
                        models.FieldCondition(
                            key="tags",
                            match=models.MatchAny(any=filters['tags'])
                        )
                    )
            
            # Combine filters
            search_filter = None
            if filter_conditions:
                search_filter = models.Filter(must=filter_conditions)
            
            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit,
                score_threshold=similarity_threshold
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    'id': result.id,
                    'score': result.score,
                    'payload': result.payload
                })
            
            logger.info(f"Semantic search returned {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def find_related(self, note_id: str, limit: int = 10, 
                    similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find notes related to a specific note."""
        try:
            # Get the note's vector
            search_results = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[note_id],
                with_vectors=True
            )
            
            if not search_results:
                logger.warning(f"Note not found in vector index: {note_id}")
                return []
            
            note_vector = search_results[0].vector
            
            # Search for similar notes (excluding the original)
            similar_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=note_vector,
                limit=limit + 1,  # +1 to account for the original note
                score_threshold=similarity_threshold
            )
            
            # Filter out the original note and format results
            results = []
            for result in similar_results:
                if result.id != note_id:
                    results.append({
                        'id': result.id,
                        'score': result.score,
                        'payload': result.payload
                    })
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error finding related notes: {e}")
            return []
    
    def suggest_connections(self, text_content: str, existing_note_domains: List[str] = None,
                           limit: int = 5, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Suggest connections for new content based on existing notes."""
        try:
            # Generate embedding for the content
            content_embedding = self.embed_text(text_content)
            
            # Build filters to focus on relevant domains
            filter_conditions = []
            if existing_note_domains:
                filter_conditions.append(
                    models.FieldCondition(
                        key="domain",
                        match=models.MatchAny(any=existing_note_domains)
                    )
                )
            
            search_filter = models.Filter(must=filter_conditions) if filter_conditions else None
            
            # Search for similar content
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=content_embedding,
                query_filter=search_filter,
                limit=limit,
                score_threshold=similarity_threshold
            )
            
            # Format suggestions
            suggestions = []
            for result in search_results:
                suggestions.append({
                    'id': result.id,
                    'title': result.payload.get('title'),
                    'content_type': result.payload.get('content_type'),
                    'domain': result.payload.get('domain'),
                    'similarity_score': result.score,
                    'file_path': result.payload.get('file_path'),
                    'suggestion_type': 'semantic_similarity'
                })
            
            logger.info(f"Generated {len(suggestions)} connection suggestions")
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating connection suggestions: {e}")
            return []
    
    def update_note(self, note_data: Dict[str, Any]) -> bool:
        """Update an existing note in the vector index."""
        try:
            # Delete existing point and add updated one
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=[note_data['id']])
            )
            
            return self.add_note(note_data)
            
        except Exception as e:
            logger.error(f"Error updating note in vector index: {e}")
            return False
    
    def delete_note(self, note_id: str) -> bool:
        """Remove a note from the vector index."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=[note_id])
            )
            
            logger.info(f"Deleted note from vector index: {note_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting note from vector index: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                'name': info.config.name,
                'vector_size': info.config.params.vectors.size,
                'distance': info.config.params.vectors.distance,
                'points_count': info.points_count,
                'status': info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}
    
    def bulk_add_notes(self, notes_data: List[Dict[str, Any]]) -> int:
        """Add multiple notes to the vector index efficiently."""
        try:
            points = []
            
            for note_data in notes_data:
                # Combine title and content for embedding
                text_content = f"{note_data.get('title', '')} {note_data.get('content', '')}"
                embedding = self.embed_text(text_content)
                
                point = PointStruct(
                    id=note_data['id'],
                    vector=embedding,
                    payload={
                        "file_path": note_data.get('file_path'),
                        "title": note_data.get('title'),
                        "content_type": note_data.get('content_type'),
                        "domain": note_data.get('domain'),
                        "tags": note_data.get('tags', []),
                        "created_date": note_data.get('created_date'),
                        "confidence": note_data.get('confidence_score', 1.0),
                        "semantic_markup": note_data.get('semantic_markup', []),
                        "relations": note_data.get('relations', [])
                    }
                )
                points.append(point)
            
            # Batch upsert
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Bulk added {len(points)} notes to vector index")
            return len(points)
            
        except Exception as e:
            logger.error(f"Error in bulk add operation: {e}")
            return 0
    
    def close(self):
        """Close the vector search engine."""
        if self.client:
            self.client.close()
            logger.info("Vector search engine closed")
