"""
OrbOS Knowledge Database
=========================
SQLite-based persistent storage for OrbCamera data.

Stores:
- Chat sessions and messages
- Documents for RAG knowledge base
- Media file references

Based on GuitarWizard's KnowledgeDatabase pattern.
"""

import os
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict


# ===== DATA CLASSES =====

@dataclass
class ChatMessage:
    """A single message in a chat session."""
    id: str
    session_id: str
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ChatSession:
    """A chat session with OrbOS."""
    id: str
    started_at: str
    ended_at: Optional[str] = None
    title: str = "New Conversation"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Document:
    """A document for RAG knowledge base."""
    id: str
    title: str
    content: str
    doc_type: str  # 'manual', 'troubleshoot', 'capability', 'history'
    source: str = ""
    created_at: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class KnowledgeDatabase:
    """
    SQLite database for OrbOS knowledge and chat history.
    
    Provides persistent storage for:
    - Chat history (sessions + messages)
    - Documents for RAG context
    - Media references
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to project data directory
            base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            db_path = os.path.join(base, "data", "orb_knowledge.db")
        
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Chat Sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                title TEXT DEFAULT 'New Conversation',
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        # Chat Messages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
            )
        """)
        
        # Documents (for RAG)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                doc_type TEXT NOT NULL,
                source TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        # Document Chunks (for embeddings - future)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                embedding_id TEXT,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON chat_messages(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_started ON chat_sessions(started_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(doc_type)")
        
        conn.commit()
        conn.close()
        
        print(f"OrbOS Knowledge database initialized: {self.db_path}")
    
    # ===== CHAT SESSION METHODS =====
    
    def create_chat_session(self, title: str = "New Conversation") -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(
            id=str(uuid.uuid4()),
            started_at=datetime.now().isoformat(),
            title=title
        )
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_sessions (id, started_at, title, metadata)
            VALUES (?, ?, ?, ?)
        """, (session.id, session.started_at, session.title, json.dumps(session.metadata)))
        conn.commit()
        conn.close()
        
        return session
    
    def end_chat_session(self, session_id: str):
        """Mark a chat session as ended."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE chat_sessions SET ended_at = ? WHERE id = ?
        """, (datetime.now().isoformat(), session_id))
        conn.commit()
        conn.close()
    
    def update_session_title(self, session_id: str, title: str):
        """Update session title (often auto-generated from first message)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE chat_sessions SET title = ? WHERE id = ?
        """, (title, session_id))
        conn.commit()
        conn.close()
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None) -> ChatMessage:
        """Add a message to a chat session."""
        message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_messages (id, session_id, role, content, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (message.id, message.session_id, message.role, message.content, message.timestamp, json.dumps(message.metadata)))
        conn.commit()
        conn.close()
        
        return message
    
    def get_session_messages(self, session_id: str) -> List[ChatMessage]:
        """Get all messages for a chat session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM chat_messages WHERE session_id = ? ORDER BY timestamp ASC
        """, (session_id,))
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            messages.append(ChatMessage(
                id=row['id'],
                session_id=row['session_id'],
                role=row['role'],
                content=row['content'],
                timestamp=row['timestamp'],
                metadata=json.loads(row['metadata'])
            ))
        return messages
    
    def get_recent_sessions(self, limit: int = 20) -> List[ChatSession]:
        """Get recent chat sessions."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM chat_sessions 
            ORDER BY started_at DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in rows:
            sessions.append(ChatSession(
                id=row['id'],
                started_at=row['started_at'],
                ended_at=row['ended_at'],
                title=row['title'],
                metadata=json.loads(row['metadata'])
            ))
        return sessions
    
    def get_all_messages(self, limit: int = 100) -> List[ChatMessage]:
        """Get recent messages across all sessions (for RAG context)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM chat_messages
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            messages.append(ChatMessage(
                id=row['id'],
                session_id=row['session_id'],
                role=row['role'],
                content=row['content'],
                timestamp=row['timestamp'],
                metadata=json.loads(row['metadata'])
            ))
        return list(reversed(messages))  # Oldest first
    
    # ===== DOCUMENT METHODS (RAG) =====
    
    def add_document(self, title: str, content: str, doc_type: str, source: str = "", metadata: Dict = None) -> Document:
        """Add a document to the knowledge base."""
        doc = Document(
            id=str(uuid.uuid4()),
            title=title,
            content=content,
            doc_type=doc_type,
            source=source,
            created_at=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO documents (id, title, content, doc_type, source, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (doc.id, doc.title, doc.content, doc.doc_type, doc.source, doc.created_at, json.dumps(doc.metadata)))
        conn.commit()
        conn.close()
        
        return doc
    
    def get_documents_by_type(self, doc_type: str) -> List[Document]:
        """Get all documents of a specific type."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE doc_type = ?", (doc_type,))
        rows = cursor.fetchall()
        conn.close()
        
        docs = []
        for row in rows:
            docs.append(Document(
                id=row['id'],
                title=row['title'],
                content=row['content'],
                doc_type=row['doc_type'],
                source=row['source'],
                created_at=row['created_at'],
                metadata=json.loads(row['metadata'])
            ))
        return docs
    
    def search_documents(self, query: str, doc_type: str = None, limit: int = 5) -> List[Document]:
        """Simple text search on documents (non-vector fallback)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        search_term = f"%{query}%"
        if doc_type:
            cursor.execute("""
                SELECT * FROM documents 
                WHERE (title LIKE ? OR content LIKE ?) AND doc_type = ?
                LIMIT ?
            """, (search_term, search_term, doc_type, limit))
        else:
            cursor.execute("""
                SELECT * FROM documents 
                WHERE title LIKE ? OR content LIKE ?
                LIMIT ?
            """, (search_term, search_term, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        docs = []
        for row in rows:
            docs.append(Document(
                id=row['id'],
                title=row['title'],
                content=row['content'],
                doc_type=row['doc_type'],
                source=row['source'],
                created_at=row['created_at'],
                metadata=json.loads(row['metadata'])
            ))
        return docs
    
    # ===== STATISTICS =====
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM chat_sessions")
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM chat_messages")
        total_messages = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents")
        total_documents = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'total_documents': total_documents
        }


# ===== SINGLETON =====

_db_instance = None

def get_database() -> KnowledgeDatabase:
    """Get or create the singleton database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = KnowledgeDatabase()
    return _db_instance
