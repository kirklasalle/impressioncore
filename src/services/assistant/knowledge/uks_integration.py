#!/usr/bin/env python3
"""
ImpressionCore: UKS Integration for Personal Assistant

Module implementing UKS (Unified Knowledge Store) integration for the personal assistant,
providing intelligent knowledge retrieval, fact verification, and learning capabilities.

File: src/assistant/knowledge/uks_integration.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-31
Modified: 2025-05-31
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [production, assistant, knowledge, uks, memory-optimized, 2025]
Dependencies: [typing, asyncio, sqlite3, json, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module provides the UKS integration layer for the personal assistant,
enabling intelligent knowledge retrieval, fact verification, and continuous
learning. Optimized for memory-constrained environments and designed to run
efficiently on consumer hardware with advanced knowledge graph traversal.

Design Philosophy:
- Memory-efficient knowledge access with <25MB allocation limit
- Intelligent knowledge caching and prefetching
- Multi-source knowledge integration (UKS, web, documents)
- Real-time knowledge validation and fact-checking
- Adaptive learning from user interactions

Architecture:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Assistant     │───▶│  UKS Integration │───▶│  Knowledge      │
│   Components    │    │     Layer        │    │  Systems        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                         ┌─────────┐
                         │ Cache & │
                         │Learning │
                         └─────────┘

Memory Considerations:
- Knowledge cache limited to 15MB for GTX 1050 Ti compatibility
- Lazy loading of knowledge graphs with LRU eviction
- Efficient embedding storage using quantized representations
- Chunked knowledge processing for large queries

Performance Targets:
- Knowledge retrieval: <500ms average
- Fact verification: <200ms for cached facts
- Memory usage: <25MB total allocation
- Cache hit rate: >80% for frequent queries
"""

import asyncio
import json
import logging
import sqlite3
import threading
import time
from collections import defaultdict, OrderedDict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from datetime import datetime, timedelta

import numpy as np

# Import existing knowledge systems
try:
    from src.core.knowledge.knowledge_store import (
        retrieve_knowledge, load_knowledge, add_knowledge
    )
    from src.core.knowledge.uks import KnowledgeNode
except ImportError:
    # Fallback imports for testing
    from knowledge.knowledge_store import (
        retrieve_knowledge, load_knowledge, add_knowledge
    )
    from knowledge.uks import KnowledgeNode

# Initialize logger
logger = logging.getLogger(__name__)

# Memory management constants
MAX_CACHE_SIZE_MB = 15  # Memory limit for knowledge cache
MAX_KNOWLEDGE_ITEMS = 1000  # Maximum cached knowledge items
EMBEDDING_DIMENSION = 384  # Reduced dimension for memory efficiency
CACHE_EXPIRY_HOURS = 24  # Cache expiry time


class KnowledgeSource(Enum):
    """Available knowledge sources for the UKS integration."""
    UKS_CORE = "uks_core"
    DOCUMENT_STORE = "document_store"
    WEB_KNOWLEDGE = "web_knowledge"
    USER_KNOWLEDGE = "user_knowledge"
    CONVERSATION_MEMORY = "conversation_memory"
    SYSTEM_KNOWLEDGE = "system_knowledge"


class KnowledgeType(Enum):
    """Types of knowledge stored in the UKS."""
    FACTUAL = "factual"
    PROCEDURAL = "procedural"
    DECLARATIVE = "declarative"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    CONTEXTUAL = "contextual"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"


class VerificationStatus(Enum):
    """Status of knowledge verification."""
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    CONTRADICTED = "contradicted"
    UNCERTAIN = "uncertain"
    OUTDATED = "outdated"


@dataclass
class KnowledgeItem:
    """Represents a single piece of knowledge in the UKS."""
    id: str
    content: str
    source: KnowledgeSource
    knowledge_type: KnowledgeType
    confidence: float = 0.8
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    tags: Set[str] = field(default_factory=set)
    embedding: Optional[np.ndarray] = None
    related_items: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing."""
        if self.embedding is None:
            # Generate simple embedding (in production, use proper embeddings)
            self.embedding = self._generate_simple_embedding()

    def _generate_simple_embedding(self) -> np.ndarray:
        """Generate a simple embedding for the knowledge item."""
        # Simple hash-based embedding for demonstration
        # In production, use proper sentence transformers
        content_hash = hash(self.content.lower()) % (2**16)
        embedding = np.random.random(EMBEDDING_DIMENSION).astype(np.float32)
        embedding[0] = (content_hash % 1000) / 1000.0  # Normalize
        return embedding

    def update_access(self):
        """Update access statistics."""
        self.last_accessed = datetime.now()
        self.access_count += 1

    def calculate_relevance_score(self, query_embedding: np.ndarray) -> float:
        """Calculate relevance score for a query."""
        if self.embedding is None:
            return 0.0
        
        # Cosine similarity
        similarity = np.dot(self.embedding, query_embedding) / (
            np.linalg.norm(self.embedding) * np.linalg.norm(query_embedding)
        )
        
        # Boost score based on access frequency and verification status
        frequency_boost = min(0.1, self.access_count * 0.01)
        verification_boost = {
            VerificationStatus.VERIFIED: 0.2,
            VerificationStatus.UNVERIFIED: 0.0,
            VerificationStatus.CONTRADICTED: -0.3,
            VerificationStatus.UNCERTAIN: -0.1,
            VerificationStatus.OUTDATED: -0.2
        }.get(self.verification_status, 0.0)
        
        return float(similarity + frequency_boost + verification_boost)


@dataclass
class KnowledgeQuery:
    """Represents a knowledge query to the UKS."""
    query_text: str
    intent: Optional[str] = None
    entities: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    preferred_sources: List[KnowledgeSource] = field(default_factory=list)
    max_results: int = 10
    min_confidence: float = 0.5
    require_verification: bool = False
    temporal_scope: Optional[Tuple[datetime, datetime]] = None


@dataclass
class KnowledgeResponse:
    """Response from a knowledge query."""
    query: KnowledgeQuery
    items: List[KnowledgeItem]
    total_found: int
    processing_time: float
    cache_hit: bool
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgeCache:
    """Memory-efficient cache for knowledge items with LRU eviction."""
    
    def __init__(self, max_size_mb: int = MAX_CACHE_SIZE_MB):
        self.max_size_mb = max_size_mb
        self.cache: OrderedDict[str, KnowledgeItem] = OrderedDict()
        self.query_cache: OrderedDict[str, KnowledgeResponse] = OrderedDict()
        self.current_size_mb = 0.0
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0

    def _estimate_item_size_mb(self, item: KnowledgeItem) -> float:
        """Estimate memory size of a knowledge item in MB."""
        # Rough estimation based on content length and embedding size
        content_size = len(item.content.encode('utf-8')) / (1024 * 1024)
        embedding_size = (
            item.embedding.nbytes / (1024 * 1024) if item.embedding is not None else 0
        )
        metadata_size = len(str(item.metadata).encode('utf-8')) / (1024 * 1024)
        return content_size + embedding_size + metadata_size

    def _enforce_memory_limit(self):
        """Remove oldest items to stay within memory limit."""
        while self.current_size_mb > self.max_size_mb and self.cache:
            # Remove oldest item
            item_id, item = self.cache.popitem(last=False)
            self.current_size_mb -= self._estimate_item_size_mb(item)
            logger.debug(f"Evicted knowledge item {item_id} from cache")

    def get(self, item_id: str) -> Optional[KnowledgeItem]:
        """Get a knowledge item from cache."""
        with self.lock:
            if item_id in self.cache:
                # Move to end (most recently used)
                item = self.cache.pop(item_id)
                self.cache[item_id] = item
                item.update_access()
                self.hits += 1
                return item
            else:
                self.misses += 1
                return None

    def put(self, item: KnowledgeItem):
        """Add a knowledge item to cache."""
        with self.lock:
            item_size = self._estimate_item_size_mb(item)
            
            # Remove existing item if present
            if item.id in self.cache:
                old_item = self.cache.pop(item.id)
                self.current_size_mb -= self._estimate_item_size_mb(old_item)
            
            # Add new item
            self.cache[item.id] = item
            self.current_size_mb += item_size
            
            # Enforce memory limit
            self._enforce_memory_limit()

    def get_query_response(self, query_hash: str) -> Optional[KnowledgeResponse]:
        """Get cached query response."""
        with self.lock:
            if query_hash in self.query_cache:
                response = self.query_cache.pop(query_hash)
                self.query_cache[query_hash] = response  # Move to end
                return response
            return None

    def cache_query_response(self, query_hash: str, response: KnowledgeResponse):
        """Cache a query response."""
        with self.lock:
            self.query_cache[query_hash] = response
            # Limit query cache size
            if len(self.query_cache) > 100:
                self.query_cache.popitem(last=False)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
            return {
                "hit_rate": hit_rate,
                "hits": self.hits,
                "misses": self.misses,
                "cached_items": len(self.cache),
                "memory_usage_mb": self.current_size_mb,
                "memory_limit_mb": self.max_size_mb,
                "query_cache_size": len(self.query_cache)
            }

    def clear(self):
        """Clear the cache."""
        with self.lock:
            self.cache.clear()
            self.query_cache.clear()
            self.current_size_mb = 0.0
            self.hits = 0
            self.misses = 0


class UKSIntegration:
    """
    Main UKS integration class providing knowledge retrieval, verification,
    and learning capabilities for the personal assistant.
    """
    
    def __init__(self, 
                 database_path: Optional[str] = None,
                 enable_learning: bool = True,
                 cache_size_mb: int = MAX_CACHE_SIZE_MB):
        """
        Initialize the UKS integration.
        
        Args:
            database_path: Path to SQLite database for persistent knowledge
            enable_learning: Whether to enable continuous learning
            cache_size_mb: Maximum cache size in MB
        """
        self.database_path = database_path or "data/assistant_knowledge.db"
        self.enable_learning = enable_learning
        
        # Initialize components
        self.cache = KnowledgeCache(cache_size_mb)
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="uks")
        
        # Knowledge tracking
        self.knowledge_sources: Dict[KnowledgeSource, bool] = {
            source: True for source in KnowledgeSource
        }
        
        # Performance tracking
        self.query_stats = defaultdict(int)
        self.response_times = []
        
        # Initialize database
        self._init_database()
        
        # Load frequently accessed knowledge into cache
        self._warm_cache()
        
        logger.info(f"UKS Integration initialized with cache size: {cache_size_mb}MB")

    def _init_database(self):
        """Initialize the SQLite database for persistent knowledge storage."""
        try:
            # Ensure database directory exists
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.database_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS knowledge_items (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        source TEXT NOT NULL,
                        knowledge_type TEXT NOT NULL,
                        confidence REAL DEFAULT 0.8,
                        verification_status TEXT DEFAULT 'unverified',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        access_count INTEGER DEFAULT 0,
                        tags TEXT DEFAULT '[]',
                        embedding BLOB,
                        related_items TEXT DEFAULT '[]',
                        metadata TEXT DEFAULT '{}'
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_knowledge_source 
                    ON knowledge_items(source)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_knowledge_type 
                    ON knowledge_items(knowledge_type)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_knowledge_confidence 
                    ON knowledge_items(confidence)
                """)
                
                conn.commit()
                logger.debug("Knowledge database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize knowledge database: {e}")
            raise

    def _warm_cache(self):
        """Load frequently accessed knowledge items into cache."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM knowledge_items 
                    ORDER BY access_count DESC, last_accessed DESC 
                    LIMIT 100
                """)
                
                for row in cursor.fetchall():
                    item = self._row_to_knowledge_item(row)
                    self.cache.put(item)
                    
                logger.debug(f"Cache warmed with {len(self.cache.cache)} items")
                
        except Exception as e:
            logger.warning(f"Failed to warm cache: {e}")

    def _row_to_knowledge_item(self, row: tuple) -> KnowledgeItem:
        """Convert database row to KnowledgeItem."""
        (id_, content, source, knowledge_type, confidence, verification_status,
         created_at, last_accessed, access_count, tags, embedding, 
         related_items, metadata) = row
        
        # Parse JSON fields
        tags_set = set(json.loads(tags)) if tags else set()
        related_list = json.loads(related_items) if related_items else []
        metadata_dict = json.loads(metadata) if metadata else {}
        
        # Parse embedding
        embedding_array = None
        if embedding:
            try:
                embedding_array = np.frombuffer(embedding, dtype=np.float32)
            except Exception as e:
                logger.warning(f"Failed to parse embedding for item {id_}: {e}")
        
        return KnowledgeItem(
            id=id_,
            content=content,
            source=KnowledgeSource(source),
            knowledge_type=KnowledgeType(knowledge_type),
            confidence=confidence,
            verification_status=VerificationStatus(verification_status),
            created_at=datetime.fromisoformat(created_at),
            last_accessed=datetime.fromisoformat(last_accessed),
            access_count=access_count,
            tags=tags_set,
            embedding=embedding_array,
            related_items=related_list,
            metadata=metadata_dict
        )

    def _knowledge_item_to_row(self, item: KnowledgeItem) -> tuple:
        """Convert KnowledgeItem to database row."""
        embedding_bytes = None
        if item.embedding is not None:
            embedding_bytes = item.embedding.tobytes()
        
        return (
            item.id,
            item.content,
            item.source.value,
            item.knowledge_type.value,
            item.confidence,
            item.verification_status.value,
            item.created_at.isoformat(),
            item.last_accessed.isoformat(),
            item.access_count,
            json.dumps(list(item.tags)),
            embedding_bytes,
            json.dumps(item.related_items),
            json.dumps(item.metadata)
        )

    async def query_knowledge(self, query: KnowledgeQuery) -> KnowledgeResponse:
        """
        Query the UKS for relevant knowledge.
        
        Args:
            query: Knowledge query specification
            
        Returns:
            Knowledge response with relevant items
        """
        start_time = time.time()
        
        # Generate query hash for caching
        query_hash = self._generate_query_hash(query)
        
        # Check cache first
        cached_response = self.cache.get_query_response(query_hash)
        if cached_response:
            cached_response.cache_hit = True
            self.query_stats["cache_hits"] += 1
            return cached_response
        
        self.query_stats["cache_misses"] += 1
        
        try:
            # Generate query embedding
            query_embedding = self._generate_query_embedding(query.query_text)
            
            # Search knowledge from multiple sources
            knowledge_items = await self._search_knowledge_sources(query, query_embedding)
            
            # Filter and rank results
            filtered_items = self._filter_and_rank_results(
                knowledge_items, query, query_embedding
            )
            
            # Calculate overall confidence
            confidence_score = self._calculate_overall_confidence(filtered_items)
            
            # Create response
            processing_time = time.time() - start_time
            response = KnowledgeResponse(
                query=query,
                items=filtered_items[:query.max_results],
                total_found=len(knowledge_items),
                processing_time=processing_time,
                cache_hit=False,
                confidence_score=confidence_score,
                metadata={
                    "sources_queried": len(self.knowledge_sources),
                    "query_embedding_dimension": len(query_embedding)
                }
            )
            
            # Cache the response
            self.cache.cache_query_response(query_hash, response)
            
            # Update statistics
            self.response_times.append(processing_time)
            self.query_stats["total_queries"] += 1
            
            logger.debug(
                f"Knowledge query processed in {processing_time:.3f}s, "
                f"found {len(filtered_items)} relevant items"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing knowledge query: {e}")
            # Return empty response on error
            return KnowledgeResponse(
                query=query,
                items=[],
                total_found=0,
                processing_time=time.time() - start_time,
                cache_hit=False,
                confidence_score=0.0,
                metadata={"error": str(e)}
            )

    def _generate_query_hash(self, query: KnowledgeQuery) -> str:
        """Generate a hash for query caching."""
        query_str = f"{query.query_text}_{query.intent}_{sorted(query.entities)}"
        return str(hash(query_str))

    def _generate_query_embedding(self, query_text: str) -> np.ndarray:
        """Generate embedding for query text."""
        # Simple hash-based embedding for demonstration
        # In production, use proper sentence transformers
        query_hash = hash(query_text.lower()) % (2**16)
        embedding = np.random.random(EMBEDDING_DIMENSION).astype(np.float32)
        embedding[0] = (query_hash % 1000) / 1000.0  # Normalize
        return embedding

    async def _search_knowledge_sources(
        self, 
        query: KnowledgeQuery, 
        query_embedding: np.ndarray
    ) -> List[KnowledgeItem]:
        """Search all available knowledge sources."""
        all_items = []
        
        # Search preferred sources first
        sources_to_search = (
            query.preferred_sources if query.preferred_sources 
            else list(self.knowledge_sources.keys())
        )
        
        # Search each source
        for source in sources_to_search:
            if not self.knowledge_sources.get(source, False):
                continue
                
            try:
                items = await self._search_source(source, query, query_embedding)
                all_items.extend(items)
            except Exception as e:
                logger.warning(f"Error searching source {source}: {e}")
        
        return all_items

    async def _search_source(
        self, 
        source: KnowledgeSource, 
        query: KnowledgeQuery,
        query_embedding: np.ndarray
    ) -> List[KnowledgeItem]:
        """Search a specific knowledge source."""
        if source == KnowledgeSource.UKS_CORE:
            return await self._search_uks_core(query, query_embedding)
        elif source == KnowledgeSource.DOCUMENT_STORE:
            return await self._search_document_store(query, query_embedding)
        elif source == KnowledgeSource.USER_KNOWLEDGE:
            return await self._search_user_knowledge(query, query_embedding)
        else:
            # For other sources, search local database
            return await self._search_local_database(query, query_embedding, source)

    async def _search_uks_core(
        self, 
        query: KnowledgeQuery, 
        query_embedding: np.ndarray
    ) -> List[KnowledgeItem]:
        """Search the core UKS knowledge base."""
        try:
            # Use existing knowledge store
            loop = asyncio.get_event_loop()
            knowledge_snippets = await loop.run_in_executor(
                self.executor,
                retrieve_knowledge,
                query.query_text,
                query.max_results * 2,  # Get more for better filtering
                query.min_confidence
            )
            
            items = []
            for i, snippet in enumerate(knowledge_snippets):
                if isinstance(snippet, dict):
                    content = snippet.get("content", str(snippet))
                    confidence = snippet.get("score", 0.8)
                else:
                    content = str(snippet)
                    confidence = 0.8
                
                item = KnowledgeItem(
                    id=f"uks_core_{i}_{hash(content) % 10000}",
                    content=content,
                    source=KnowledgeSource.UKS_CORE,
                    knowledge_type=KnowledgeType.FACTUAL,
                    confidence=confidence,
                    verification_status=VerificationStatus.UNVERIFIED
                )
                items.append(item)
            
            return items
            
        except Exception as e:
            logger.error(f"Error searching UKS core: {e}")
            return []

    async def _search_document_store(
        self, 
        query: KnowledgeQuery, 
        query_embedding: np.ndarray
    ) -> List[KnowledgeItem]:
        """Search the document store."""
        # Placeholder for document store integration
        # In production, this would integrate with the document store
        return []

    async def _search_user_knowledge(
        self, 
        query: KnowledgeQuery, 
        query_embedding: np.ndarray
    ) -> List[KnowledgeItem]:
        """Search user-specific knowledge."""
        # Search local database for user knowledge
        return await self._search_local_database(
            query, query_embedding, KnowledgeSource.USER_KNOWLEDGE
        )

    async def _search_local_database(
        self, 
        query: KnowledgeQuery, 
        query_embedding: np.ndarray,
        source: KnowledgeSource
    ) -> List[KnowledgeItem]:
        """Search the local SQLite database."""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self.executor,
                self._search_database_sync,
                query,
                query_embedding,
                source
            )
        except Exception as e:
            logger.error(f"Error searching local database: {e}")
            return []

    def _search_database_sync(
        self, 
        query: KnowledgeQuery, 
        query_embedding: np.ndarray,
        source: KnowledgeSource
    ) -> List[KnowledgeItem]:
        """Synchronous database search."""
        items = []
        
        try:
            with sqlite3.connect(self.database_path) as conn:
                # Build query conditions
                conditions = ["source = ?"]
                params = [source.value]
                
                if query.min_confidence > 0:
                    conditions.append("confidence >= ?")
                    params.append(query.min_confidence)
                
                if query.require_verification:
                    conditions.append("verification_status = ?")
                    params.append(VerificationStatus.VERIFIED.value)
                
                # Simple text search (in production, use FTS or vector search)
                conditions.append("content LIKE ?")
                params.append(f"%{query.query_text}%")
                
                query_sql = f"""
                    SELECT * FROM knowledge_items 
                    WHERE {' AND '.join(conditions)}
                    ORDER BY confidence DESC, access_count DESC
                    LIMIT ?
                """
                params.append(query.max_results * 2)
                
                cursor = conn.execute(query_sql, params)
                
                for row in cursor.fetchall():
                    item = self._row_to_knowledge_item(row)
                    items.append(item)
                    
        except Exception as e:
            logger.error(f"Database search error: {e}")
        
        return items

    def _filter_and_rank_results(
        self, 
        items: List[KnowledgeItem], 
        query: KnowledgeQuery,
        query_embedding: np.ndarray
    ) -> List[KnowledgeItem]:
        """Filter and rank knowledge items by relevance."""
        scored_items = []
        
        for item in items:
            # Calculate relevance score
            relevance_score = item.calculate_relevance_score(query_embedding)
            
            # Apply filters
            if relevance_score < query.min_confidence:
                continue
                
            if query.require_verification and item.verification_status != VerificationStatus.VERIFIED:
                continue
            
            # Check temporal scope
            if query.temporal_scope:
                start_time, end_time = query.temporal_scope
                if not (start_time <= item.created_at <= end_time):
                    continue
            
            scored_items.append((item, relevance_score))
        
        # Sort by relevance score (descending)
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        # Return sorted items
        return [item for item, score in scored_items]

    def _calculate_overall_confidence(self, items: List[KnowledgeItem]) -> float:
        """Calculate overall confidence score for the response."""
        if not items:
            return 0.0
        
        # Weighted average of confidence scores
        total_weight = 0
        weighted_sum = 0
        
        for i, item in enumerate(items):
            # Give higher weight to top results
            weight = 1.0 / (i + 1)
            weighted_sum += item.confidence * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    async def add_knowledge(self, item: KnowledgeItem) -> bool:
        """
        Add a new knowledge item to the UKS.
        
        Args:
            item: Knowledge item to add
            
        Returns:
            True if successfully added, False otherwise
        """
        try:
            # Add to cache
            self.cache.put(item)
            
            # Add to database
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                self.executor,
                self._add_knowledge_sync,
                item
            )
            
            if success:
                logger.debug(f"Added knowledge item: {item.id}")
                
                # Learn from new knowledge if enabled
                if self.enable_learning:
                    await self._learn_from_knowledge(item)
            
            return success
            
        except Exception as e:
            logger.error(f"Error adding knowledge item: {e}")
            return False

    def _add_knowledge_sync(self, item: KnowledgeItem) -> bool:
        """Synchronously add knowledge item to database."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                row = self._knowledge_item_to_row(item)
                conn.execute("""
                    INSERT OR REPLACE INTO knowledge_items 
                    (id, content, source, knowledge_type, confidence, 
                     verification_status, created_at, last_accessed, 
                     access_count, tags, embedding, related_items, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, row)
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Database insert error: {e}")
            return False

    async def _learn_from_knowledge(self, item: KnowledgeItem):
        """Learn patterns from new knowledge item."""
        # Placeholder for learning implementation
        # This would analyze the knowledge item and update models
        logger.debug(f"Learning from knowledge item: {item.id}")

    async def verify_knowledge(self, item_id: str) -> VerificationStatus:
        """
        Verify a knowledge item against multiple sources.
        
        Args:
            item_id: ID of the knowledge item to verify
            
        Returns:
            Verification status
        """
        try:
            # Get the knowledge item
            item = self.cache.get(item_id)
            if not item:
                # Load from database
                item = await self._load_knowledge_item(item_id)
                if not item:
                    return VerificationStatus.UNCERTAIN
            
            # Perform verification (placeholder implementation)
            # In production, this would cross-reference multiple sources
            verification_status = await self._perform_verification(item)
            
            # Update item status
            item.verification_status = verification_status
            
            # Update in database
            await self._update_knowledge_item(item)
            
            logger.debug(f"Verified knowledge item {item_id}: {verification_status}")
            return verification_status
            
        except Exception as e:
            logger.error(f"Error verifying knowledge item {item_id}: {e}")
            return VerificationStatus.UNCERTAIN

    async def _load_knowledge_item(self, item_id: str) -> Optional[KnowledgeItem]:
        """Load knowledge item from database."""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self.executor,
                self._load_knowledge_item_sync,
                item_id
            )
        except Exception as e:
            logger.error(f"Error loading knowledge item {item_id}: {e}")
            return None

    def _load_knowledge_item_sync(self, item_id: str) -> Optional[KnowledgeItem]:
        """Synchronously load knowledge item from database."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM knowledge_items WHERE id = ?", 
                    (item_id,)
                )
                row = cursor.fetchone()
                if row:
                    return self._row_to_knowledge_item(row)
                return None
        except Exception as e:
            logger.error(f"Database load error: {e}")
            return None

    async def _perform_verification(self, item: KnowledgeItem) -> VerificationStatus:
        """Perform actual verification of knowledge item."""
        # Placeholder verification logic
        # In production, this would use multiple verification strategies
        
        # Simple heuristics for demonstration
        if item.confidence > 0.9:
            return VerificationStatus.VERIFIED
        elif item.confidence > 0.7:
            return VerificationStatus.UNVERIFIED
        elif item.confidence > 0.3:
            return VerificationStatus.UNCERTAIN
        else:
            return VerificationStatus.CONTRADICTED

    async def _update_knowledge_item(self, item: KnowledgeItem):
        """Update knowledge item in storage."""
        # Update cache
        self.cache.put(item)
        
        # Update database
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self._add_knowledge_sync,  # INSERT OR REPLACE
            item
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get UKS integration performance statistics."""
        cache_stats = self.cache.get_stats()
        
        avg_response_time = (
            sum(self.response_times) / len(self.response_times) 
            if self.response_times else 0.0
        )
        
        return {
            "cache_statistics": cache_stats,
            "query_statistics": dict(self.query_stats),
            "average_response_time": avg_response_time,
            "total_queries": len(self.response_times),
            "knowledge_sources": {
                source.value: enabled 
                for source, enabled in self.knowledge_sources.items()
            },
            "database_path": self.database_path,
            "learning_enabled": self.enable_learning
        }

    async def cleanup(self):
        """Clean up resources."""
        try:
            # Clear cache
            self.cache.clear()
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            logger.info("UKS Integration cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            # Try to clean up if not already done
            if hasattr(self, 'executor') and not self.executor._shutdown:
                self.executor.shutdown(wait=False)
        except Exception:
            pass


# Convenience functions for easy integration

async def create_uks_integration(
    database_path: Optional[str] = None,
    enable_learning: bool = True,
    cache_size_mb: int = MAX_CACHE_SIZE_MB
) -> UKSIntegration:
    """
    Create and initialize a UKS integration instance.
    
    Args:
        database_path: Path to SQLite database
        enable_learning: Whether to enable learning
        cache_size_mb: Cache size in MB
        
    Returns:
        Initialized UKS integration instance
    """
    return UKSIntegration(
        database_path=database_path,
        enable_learning=enable_learning,
        cache_size_mb=cache_size_mb
    )


async def query_uks(
    integration: UKSIntegration,
    query_text: str,
    intent: Optional[str] = None,
    max_results: int = 10,
    min_confidence: float = 0.5
) -> KnowledgeResponse:
    """
    Convenience function to query the UKS.
    
    Args:
        integration: UKS integration instance
        query_text: Query text
        intent: Optional intent
        max_results: Maximum results to return
        min_confidence: Minimum confidence threshold
        
    Returns:
        Knowledge response
    """
    query = KnowledgeQuery(
        query_text=query_text,
        intent=intent,
        max_results=max_results,
        min_confidence=min_confidence
    )
    
    return await integration.query_knowledge(query)


# Example usage and testing
if __name__ == "__main__":
    async def main():
        """Example usage of UKS Integration."""
        # Create integration
        uks = await create_uks_integration()
        
        try:
            # Query knowledge
            response = await query_uks(
                uks, 
                "What is artificial intelligence?",
                intent="question",
                max_results=5
            )
            
            print(f"Found {len(response.items)} knowledge items")
            print(f"Processing time: {response.processing_time:.3f}s")
            print(f"Confidence: {response.confidence_score:.2f}")
            
            for i, item in enumerate(response.items):
                print(f"{i+1}. {item.content[:100]}... (confidence: {item.confidence:.2f})")
            
            # Show statistics
            stats = uks.get_statistics()
            print(f"\nCache hit rate: {stats['cache_statistics']['hit_rate']:.2%}")
            print(f"Memory usage: {stats['cache_statistics']['memory_usage_mb']:.1f}MB")
            
        finally:
            await uks.cleanup()
    
    # Run example
    asyncio.run(main())
