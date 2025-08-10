# gitgeist/memory/vector_store.py
import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

from gitgeist.utils.logger import get_logger

# Suppress tokenizers parallelism warnings
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')

logger = get_logger(__name__)


class GitgeistMemory:
    """Simple vector store for commit history and code context"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.db_path = data_dir / "memory.db"
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database for memory storage"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS commits (
                    id INTEGER PRIMARY KEY,
                    hash TEXT UNIQUE,
                    message TEXT,
                    files_changed TEXT,
                    semantic_changes TEXT,
                    embedding BLOB,
                    timestamp REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_context (
                    id INTEGER PRIMARY KEY,
                    filepath TEXT,
                    content_hash TEXT,
                    functions TEXT,
                    classes TEXT,
                    embedding BLOB,
                    last_updated REAL
                )
            """)

    def store_commit(self, commit_hash: str, message: str, files_changed: List[str], 
                    semantic_changes: Dict) -> None:
        """Store commit information with vector embedding"""
        try:
            # Convert sets to lists for JSON serialization
            def convert_sets_to_lists(obj):
                if isinstance(obj, dict):
                    return {k: convert_sets_to_lists(v) for k, v in obj.items()}
                elif isinstance(obj, set):
                    return list(obj)
                elif isinstance(obj, list):
                    return [convert_sets_to_lists(item) for item in obj]
                else:
                    return obj
            
            serializable_changes = convert_sets_to_lists(semantic_changes)
            
            # Create text for embedding
            text = f"{message} | Files: {', '.join(files_changed[:5])}"
            if serializable_changes:
                funcs = serializable_changes.get('functions_added', [])
                classes = serializable_changes.get('classes_added', [])
                if funcs:
                    text += f" | Functions: {', '.join(funcs[:3])}"
                if classes:
                    text += f" | Classes: {', '.join(classes[:3])}"

            # Generate embedding
            embedding = self.model.encode(text)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO commits 
                    (hash, message, files_changed, semantic_changes, embedding, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    commit_hash,
                    message,
                    json.dumps(files_changed),
                    json.dumps(serializable_changes),
                    embedding.tobytes(),
                    __import__('time').time()
                ))
                
            logger.debug(f"Stored commit {commit_hash[:8]} in memory")
            
        except Exception as e:
            logger.error(f"Failed to store commit {commit_hash}: {e}")

    def find_similar_commits(self, query: str, limit: int = 5) -> List[Dict]:
        """Find similar commits based on semantic similarity"""
        try:
            query_embedding = self.model.encode(query)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT hash, message, files_changed, semantic_changes, embedding
                    FROM commits ORDER BY timestamp DESC LIMIT 50
                """)
                
                results = []
                for row in cursor.fetchall():
                    stored_embedding = np.frombuffer(row[4], dtype=np.float32)
                    similarity = np.dot(query_embedding, stored_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
                    )
                    
                    results.append({
                        'hash': row[0],
                        'message': row[1],
                        'files_changed': json.loads(row[2]),
                        'semantic_changes': json.loads(row[3]),
                        'similarity': float(similarity)
                    })
                
                # Sort by similarity and return top results
                results.sort(key=lambda x: x['similarity'], reverse=True)
                return results[:limit]
                
        except Exception as e:
            logger.error(f"Failed to find similar commits: {e}")
            return []

    def get_file_context(self, filepath: str) -> Optional[Dict]:
        """Get stored context for a file"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT functions, classes, last_updated
                    FROM file_context WHERE filepath = ?
                """, (filepath,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'functions': json.loads(row[0]),
                        'classes': json.loads(row[1]),
                        'last_updated': row[2]
                    }
                    
        except Exception as e:
            logger.error(f"Failed to get file context for {filepath}: {e}")
            
        return None

    def store_file_context(self, filepath: str, functions: List[str], 
                          classes: List[str]) -> None:
        """Store file context information"""
        try:
            # Create embedding from file structure
            text = f"File: {filepath} | Functions: {', '.join(functions[:10])} | Classes: {', '.join(classes[:5])}"
            embedding = self.model.encode(text)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO file_context
                    (filepath, functions, classes, embedding, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    filepath,
                    json.dumps(functions),
                    json.dumps(classes),
                    embedding.tobytes(),
                    __import__('time').time()
                ))
                
        except Exception as e:
            logger.error(f"Failed to store file context for {filepath}: {e}")

    def get_memory_stats(self) -> Dict:
        """Get memory database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                commits_count = conn.execute("SELECT COUNT(*) FROM commits").fetchone()[0]
                files_count = conn.execute("SELECT COUNT(*) FROM file_context").fetchone()[0]
                
                return {
                    'commits_stored': commits_count,
                    'files_tracked': files_count,
                    'db_size_mb': self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0
                }
                
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {'commits_stored': 0, 'files_tracked': 0, 'db_size_mb': 0}