"""
Face Database Module

Manages persistent storage of face encodings and identity metadata.
Uses SQLite for reliability and easy backup/restore.

Created: January 14, 2026
Author: ImpressionCore Team
"""

import json
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

# Database location
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "faces"
DB_PATH = DATA_DIR / "faces.db"


@dataclass
class FaceIdentity:
    """Represents an enrolled face identity."""

    id: str                          # UUID
    name: str                        # Display name (e.g., "Kirk")
    role: str = "user"               # user, admin, guest
    created_at: str = ""             # ISO timestamp
    updated_at: str = ""             # ISO timestamp
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding_count: int = 0         # Number of stored embeddings

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at


@dataclass
class FaceEmbedding:
    """A single face embedding (128-dim vector)."""

    id: str                # UUID
    identity_id: str       # Foreign key to FaceIdentity
    embedding: np.ndarray  # 128-dimensional face encoding
    captured_at: str = ""  # ISO timestamp
    quality_score: float = 1.0  # Image quality at capture time

    def __post_init__(self):
        if not self.captured_at:
            self.captured_at = datetime.now().isoformat()


class FaceDatabase:
    """
    SQLite-backed storage for face identities and encodings.

    Schema:
    - identities: id, name, role, created_at, updated_at, metadata
    - embeddings: id, identity_id, embedding, captured_at, quality_score
    """

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or DB_PATH
        self._ensure_directory()
        self._init_database()

    def _ensure_directory(self):
        """Create data directory if it doesn't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _init_database(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Identities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS identities (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}'
                )
            """)

            # Embeddings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id TEXT PRIMARY KEY,
                    identity_id TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    captured_at TEXT NOT NULL,
                    quality_score REAL DEFAULT 1.0,
                    FOREIGN KEY (identity_id) REFERENCES identities(id)
                        ON DELETE CASCADE
                )
            """)

            # Index for fast lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_embeddings_identity
                ON embeddings(identity_id)
            """)

            conn.commit()

    # ========================
    # Identity CRUD Operations
    # ========================

    def create_identity(self, name: str, role: str = "user",
                       metadata: dict | None = None) -> FaceIdentity:
        """Create a new face identity."""
        identity = FaceIdentity(
            id=str(uuid.uuid4()),
            name=name,
            role=role,
            metadata=metadata or {}
        )

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO identities (id, name, role, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                identity.id,
                identity.name,
                identity.role,
                identity.created_at,
                identity.updated_at,
                json.dumps(identity.metadata)
            ))
            conn.commit()

        return identity

    def get_identity(self, identity_id: str) -> FaceIdentity | None:
        """Get identity by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, role, created_at, updated_at, metadata,
                       (SELECT COUNT(*) FROM embeddings WHERE identity_id = ?)
                FROM identities WHERE id = ?
            """, (identity_id, identity_id))

            row = cursor.fetchone()
            if row:
                return FaceIdentity(
                    id=row[0],
                    name=row[1],
                    role=row[2],
                    created_at=row[3],
                    updated_at=row[4],
                    metadata=json.loads(row[5]) if row[5] else {},
                    embedding_count=row[6]
                )
        return None

    def get_identity_by_name(self, name: str) -> FaceIdentity | None:
        """Get identity by name (case-insensitive)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, role, created_at, updated_at, metadata
                FROM identities WHERE LOWER(name) = LOWER(?)
            """, (name,))

            row = cursor.fetchone()
            if row:
                return FaceIdentity(
                    id=row[0],
                    name=row[1],
                    role=row[2],
                    created_at=row[3],
                    updated_at=row[4],
                    metadata=json.loads(row[5]) if row[5] else {}
                )
        return None

    def list_identities(self) -> list[FaceIdentity]:
        """List all enrolled identities."""
        identities = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT i.id, i.name, i.role, i.created_at, i.updated_at, i.metadata,
                       (SELECT COUNT(*) FROM embeddings e WHERE e.identity_id = i.id)
                FROM identities i
                ORDER BY i.name
            """)

            for row in cursor.fetchall():
                identities.append(FaceIdentity(
                    id=row[0],
                    name=row[1],
                    role=row[2],
                    created_at=row[3],
                    updated_at=row[4],
                    metadata=json.loads(row[5]) if row[5] else {},
                    embedding_count=row[6]
                ))

        return identities

    def update_identity(self, identity_id: str, name: str | None = None,
                       role: str | None = None,
                       metadata: dict | None = None) -> bool:
        """Update identity fields."""
        updates = []
        values = []

        if name is not None:
            updates.append("name = ?")
            values.append(name)
        if role is not None:
            updates.append("role = ?")
            values.append(role)
        if metadata is not None:
            updates.append("metadata = ?")
            values.append(json.dumps(metadata))

        if not updates:
            return False

        updates.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(identity_id)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE identities SET {', '.join(updates)}
                WHERE id = ?
            """, values)
            conn.commit()
            return cursor.rowcount > 0

    def delete_identity(self, identity_id: str) -> bool:
        """Delete identity and all associated embeddings."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Embeddings deleted via CASCADE
            cursor.execute("DELETE FROM identities WHERE id = ?", (identity_id,))
            conn.commit()
            return cursor.rowcount > 0

    # ========================
    # Embedding Operations
    # ========================

    def add_embedding(self, identity_id: str, embedding: np.ndarray,
                     quality_score: float = 1.0) -> FaceEmbedding | None:
        """Add a face embedding to an identity."""
        if self.get_identity(identity_id) is None:
            return None

        face_embedding = FaceEmbedding(
            id=str(uuid.uuid4()),
            identity_id=identity_id,
            embedding=embedding,
            quality_score=quality_score
        )

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO embeddings (id, identity_id, embedding, captured_at, quality_score)
                VALUES (?, ?, ?, ?, ?)
            """, (
                face_embedding.id,
                face_embedding.identity_id,
                embedding.tobytes(),
                face_embedding.captured_at,
                face_embedding.quality_score
            ))

            # Update identity timestamp
            cursor.execute("""
                UPDATE identities SET updated_at = ? WHERE id = ?
            """, (datetime.now().isoformat(), identity_id))

            conn.commit()

        return face_embedding

    def get_embeddings(self, identity_id: str) -> list[FaceEmbedding]:
        """Get all embeddings for an identity."""
        embeddings = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, identity_id, embedding, captured_at, quality_score
                FROM embeddings WHERE identity_id = ?
                ORDER BY captured_at DESC
            """, (identity_id,))

            for row in cursor.fetchall():
                embeddings.append(FaceEmbedding(
                    id=row[0],
                    identity_id=row[1],
                    embedding=np.frombuffer(row[2], dtype=np.float64),
                    captured_at=row[3],
                    quality_score=row[4]
                ))

        return embeddings

    def get_all_embeddings(self) -> list[tuple[FaceIdentity, list[np.ndarray]]]:
        """
        Get all identities with their embeddings for recognition.

        Returns list of (identity, embeddings) tuples for efficient matching.
        """
        result = []
        identities = self.list_identities()

        for identity in identities:
            embeddings = self.get_embeddings(identity.id)
            if embeddings:
                np_embeddings = [e.embedding for e in embeddings]
                result.append((identity, np_embeddings))

        return result

    def delete_embedding(self, embedding_id: str) -> bool:
        """Delete a specific embedding."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM embeddings WHERE id = ?", (embedding_id,))
            conn.commit()
            return cursor.rowcount > 0

    # ========================
    # Utility Methods
    # ========================

    def get_stats(self) -> dict[str, int]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM identities")
            identity_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM embeddings")
            embedding_count = cursor.fetchone()[0]

        return {
            "identity_count": identity_count,
            "embedding_count": embedding_count,
            "db_path": str(self.db_path)
        }

    def backup(self, backup_path: Path) -> bool:
        """Create a backup of the database."""
        import shutil
        try:
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception:
            return False


# Global database instance
_db_instance: FaceDatabase | None = None


def get_face_database() -> FaceDatabase:
    """Get global face database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = FaceDatabase()
    return _db_instance
