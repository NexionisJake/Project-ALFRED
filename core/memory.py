"""
Vector-based memory system for ALFRED using ChromaDB.
Provides semantic search capabilities for conversation history and knowledge base.
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠ ChromaDB not installed. Vector memory disabled.")

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("⚠ sentence-transformers not installed. Semantic search disabled.")

from colorama import Fore


class VectorMemory:
    """
    ChromaDB-based vector memory for semantic search over conversations
    and knowledge base entries.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize vector memory.
        
        Args:
            data_dir: Directory to store ChromaDB data (defaults to project data folder)
        """
        self.enabled = CHROMADB_AVAILABLE and EMBEDDINGS_AVAILABLE
        
        if not self.enabled:
            print(Fore.YELLOW + "⚠ Vector memory not available (missing dependencies)")
            return
        
        # Setup data directory
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "vector_db")
        
        os.makedirs(data_dir, exist_ok=True)
        self.data_dir = data_dir
        
        # Initialize embedding model (lightweight model for speed)
        print(Fore.YELLOW + "Loading embedding model...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        print(Fore.GREEN + "✓ Embedding model loaded")
        
        # Initialize ChromaDB with persistent storage
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=data_dir,
            anonymized_telemetry=False
        ))
        
        # Create collections
        self.conversation_collection = self.client.get_or_create_collection(
            name="conversations",
            metadata={"description": "Conversation history with semantic search"}
        )
        
        self.knowledge_collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"description": "Personal knowledge base entries"}
        )
        
        print(Fore.GREEN + f"✓ Vector memory initialized ({self.conversation_collection.count()} conversations, {self.knowledge_collection.count()} knowledge entries)")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        return self.embedder.encode(text).tolist()
    
    def add_conversation(self, role: str, content: str, metadata: Dict = None) -> str:
        """
        Add a conversation message to vector memory.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional additional metadata
        
        Returns:
            ID of added document
        """
        if not self.enabled:
            return None
        
        doc_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        meta = {
            "role": role,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }
        
        embedding = self._generate_embedding(content)
        
        self.conversation_collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[meta]
        )
        
        return doc_id
    
    def search_conversations(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search conversation history semantically.
        
        Args:
            query: Search query
            n_results: Number of results to return
        
        Returns:
            List of matching conversations with metadata
        """
        if not self.enabled:
            return []
        
        query_embedding = self._generate_embedding(query)
        
        results = self.conversation_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        conversations = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                conversations.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None
                })
        
        return conversations
    
    def add_knowledge(self, content: str, category: str = "general") -> str:
        """
        Add a knowledge base entry.
        
        Args:
            content: Knowledge content (e.g., "My WiFi password is 'secret'")
            category: Category for organization
        
        Returns:
            ID of added entry
        """
        if not self.enabled:
            return None
        
        doc_id = f"kb_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        meta = {
            "category": category,
            "added_at": datetime.now().isoformat()
        }
        
        embedding = self._generate_embedding(content)
        
        self.knowledge_collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[meta]
        )
        
        return doc_id
    
    def search_knowledge(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        Search knowledge base semantically.
        
        Args:
            query: Search query (e.g., "wifi password")
            n_results: Number of results to return
        
        Returns:
            List of matching knowledge entries
        """
        if not self.enabled:
            return []
        
        query_embedding = self._generate_embedding(query)
        
        results = self.knowledge_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        entries = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                entries.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None
                })
        
        return entries
    
    def import_brain_txt(self, brain_path: str) -> int:
        """
        Import existing brain.txt into vector knowledge base.
        
        Args:
            brain_path: Path to brain.txt file
        
        Returns:
            Number of entries imported
        """
        if not self.enabled:
            return 0
        
        if not os.path.exists(brain_path):
            print(Fore.RED + f"✗ brain.txt not found: {brain_path}")
            return 0
        
        with open(brain_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        count = 0
        for line in lines:
            self.add_knowledge(line)
            count += 1
        
        print(Fore.GREEN + f"✓ Imported {count} entries from brain.txt")
        return count
    
    def get_relevant_context(self, query: str, max_tokens: int = 500) -> str:
        """
        Get relevant context for a query from both conversations and knowledge.
        Useful for providing context to the LLM.
        
        Args:
            query: User's query
            max_tokens: Approximate max length of context
        
        Returns:
            Formatted context string
        """
        if not self.enabled:
            return ""
        
        context_parts = []
        
        # Search knowledge base first (higher priority)
        knowledge = self.search_knowledge(query, n_results=3)
        if knowledge:
            context_parts.append("**From your knowledge base:**")
            for entry in knowledge:
                if entry['distance'] and entry['distance'] < 1.0:  # Relevance threshold
                    context_parts.append(f"- {entry['content']}")
        
        # Search recent conversations
        conversations = self.search_conversations(query, n_results=3)
        if conversations:
            context_parts.append("\n**From past conversations:**")
            for conv in conversations:
                if conv['distance'] and conv['distance'] < 1.0:
                    role = conv['metadata'].get('role', 'unknown')
                    context_parts.append(f"- [{role}]: {conv['content'][:100]}...")
        
        context = "\n".join(context_parts)
        
        # Rough token limit (4 chars ≈ 1 token)
        if len(context) > max_tokens * 4:
            context = context[:max_tokens * 4] + "..."
        
        return context
    
    def clear_conversations(self):
        """Clear all conversation history."""
        if self.enabled:
            # Delete and recreate collection
            self.client.delete_collection("conversations")
            self.conversation_collection = self.client.create_collection(
                name="conversations",
                metadata={"description": "Conversation history with semantic search"}
            )
            print(Fore.CYAN + "✓ Conversation history cleared")
    
    def persist(self):
        """Persist data to disk."""
        if self.enabled:
            self.client.persist()


class SemanticKnowledgeSearch:
    """
    Drop-in replacement for simple string search in knowledge base.
    Combines vector search with keyword matching for best results.
    """
    
    def __init__(self, brain_path: str, vector_memory: VectorMemory = None):
        """
        Initialize semantic search.
        
        Args:
            brain_path: Path to brain.txt
            vector_memory: Optional shared VectorMemory instance
        """
        self.brain_path = brain_path
        self.vector_memory = vector_memory
        self.plain_content = None
        
        # Load plain text as fallback
        if os.path.exists(brain_path):
            with open(brain_path, 'r', encoding='utf-8') as f:
                self.plain_content = f.read()
    
    def search(self, query: str) -> List[str]:
        """
        Search knowledge base with semantic + keyword hybrid search.
        
        Args:
            query: Search query
        
        Returns:
            List of matching lines/entries
        """
        results = []
        
        # 1. Try vector search first
        if self.vector_memory and self.vector_memory.enabled:
            vector_results = self.vector_memory.search_knowledge(query, n_results=5)
            for entry in vector_results:
                if entry['distance'] and entry['distance'] < 1.0:
                    results.append(entry['content'])
        
        # 2. Fallback/supplement with keyword search
        if self.plain_content:
            query_lower = query.lower()
            lines = self.plain_content.split('\n')
            for line in lines:
                if line.strip() and query_lower in line.lower():
                    if line.strip() not in results:  # Avoid duplicates
                        results.append(line.strip())
        
        return results


# Quick test
if __name__ == "__main__":
    print("Testing Vector Memory...")
    
    if not CHROMADB_AVAILABLE or not EMBEDDINGS_AVAILABLE:
        print(Fore.RED + "⚠ Missing dependencies. Install with:")
        print(Fore.YELLOW + "  pip install chromadb sentence-transformers")
    else:
        # Initialize
        vm = VectorMemory()
        
        # Test adding knowledge
        vm.add_knowledge("My WiFi password is 'Realme 5 Pro'")
        vm.add_knowledge("My name is Abhijeet")
        vm.add_knowledge("I live in Bengaluru, India")
        
        # Test search
        print("\nSearching for 'wifi':")
        results = vm.search_knowledge("wifi")
        for r in results:
            print(f"  - {r['content']} (distance: {r['distance']:.3f})")
        
        print("\nSearching for 'where do I live':")
        results = vm.search_knowledge("where do I live")
        for r in results:
            print(f"  - {r['content']} (distance: {r['distance']:.3f})")
        
        print(Fore.GREEN + "\n✓ Vector memory test complete!")
