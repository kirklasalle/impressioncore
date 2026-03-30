"""
Context Manager for Phase 8B Personal Assistant

This module provides comprehensive context management including conversation state,
long-term context retention, context switching, and memory-efficient context storage.
Optimized for GTX 1050 Ti hardware constraints.

Author: ImpressionCore Development Team
Created: 2025-01-18
Version: 1.0.0
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
Memory Budget: 10MB maximum allocation
"""

import asyncio
import json
import logging
import sqlite3
import time
from abc import ABC, abstractmethod
from collections import deque, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any, Dict, List, Optional, Set, Tuple, Union,
    Callable, Awaitable, NamedTuple, Deque
)
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)

# Rich console imports for enhanced user experience
try:
    from src.core.utils.rich_enhancements import (
        console, success_panel, error_panel, info_panel,
        create_progress_bar, highlight_text
    )
    from src.core.utils.rich_logging import setup_rich_logging
    from src.core.utils.rich_status_animation import StatusAnimation
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Import NLU types
try:
    from ..nlp.nlu_engine import NLUResult, Intent, Entity, Sentiment, IntentCategory
    NLU_AVAILABLE = True
except ImportError:
    NLU_AVAILABLE = False


class ContextType(Enum):
    """Types of context information."""
    
    CONVERSATION = auto()  # Dialog flow context
    TASK = auto()         # Task-related context
    USER_PROFILE = auto() # User preferences and history
    SESSION = auto()      # Current session context
    TEMPORAL = auto()     # Time-based context
    SPATIAL = auto()      # Location-based context
    EMOTIONAL = auto()    # Emotional state context
    SYSTEM = auto()       # System state context


class ContextScope(Enum):
    """Context scope and persistence levels."""
    
    IMMEDIATE = auto()    # Current turn only
    SHORT_TERM = auto()   # Last few turns
    MEDIUM_TERM = auto()  # Current session
    LONG_TERM = auto()    # Persistent across sessions
    PERMANENT = auto()    # User profile information


class ContextPriority(Enum):
    """Context priority levels for memory management."""
    
    CRITICAL = auto()     # Essential context, never remove
    HIGH = auto()         # Important, remove only if necessary
    MEDIUM = auto()       # Standard context
    LOW = auto()          # Can be removed to free memory


@dataclass
class ContextItem:
    """Individual context item with metadata."""
    
    content: Any
    context_type: ContextType
    scope: ContextScope
    priority: ContextPriority
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
    expiry: Optional[datetime] = None
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Set expiry based on scope if not provided."""
        if self.expiry is None:
            if self.scope == ContextScope.IMMEDIATE:
                self.expiry = self.timestamp + timedelta(minutes=5)
            elif self.scope == ContextScope.SHORT_TERM:
                self.expiry = self.timestamp + timedelta(hours=1)
            elif self.scope == ContextScope.MEDIUM_TERM:
                self.expiry = self.timestamp + timedelta(hours=12)
            elif self.scope == ContextScope.LONG_TERM:
                self.expiry = self.timestamp + timedelta(days=30)
            # PERMANENT scope has no expiry
    
    def is_expired(self) -> bool:
        """Check if context item has expired."""
        if self.scope == ContextScope.PERMANENT or self.expiry is None:
            return False
        return datetime.now() > self.expiry
    
    def access(self) -> None:
        """Update access statistics."""
        self.access_count += 1
        self.last_accessed = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'content': self.content,
            'context_type': self.context_type.name,
            'scope': self.scope.name,
            'priority': self.priority.name,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'metadata': self.metadata,
            'expiry': self.expiry.isoformat() if self.expiry else None,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextItem':
        """Create from dictionary."""
        return cls(
            content=data['content'],
            context_type=ContextType[data['context_type']],
            scope=ContextScope[data['scope']],
            priority=ContextPriority[data['priority']],
            timestamp=datetime.fromisoformat(data['timestamp']),
            source=data['source'],
            metadata=data['metadata'],
            expiry=datetime.fromisoformat(data['expiry']) if data['expiry'] else None,
            access_count=data['access_count'],
            last_accessed=datetime.fromisoformat(data['last_accessed'])
        )


@dataclass
class ConversationTurn:
    """Represents a single conversation turn."""
    
    turn_id: str
    user_input: str
    assistant_response: str
    nlu_result: Optional[Any] = None  # NLUResult if available
    timestamp: datetime = field(default_factory=datetime.now)
    context_updates: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'turn_id': self.turn_id,
            'user_input': self.user_input,
            'assistant_response': self.assistant_response,
            'nlu_result': self.nlu_result.to_dict() if hasattr(self.nlu_result, 'to_dict') else None,
            'timestamp': self.timestamp.isoformat(),
            'context_updates': self.context_updates,
            'metadata': self.metadata
        }


class MemoryManager:
    """Memory management for context storage."""
    
    def __init__(self, max_memory_mb: int = 10):
        """Initialize memory manager.
        
        Args:
            max_memory_mb: Maximum memory allocation in MB
        """
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.current_usage = 0
        self.allocations = {}
        
        self.logger = logging.getLogger(__name__)
    
    def estimate_size(self, obj: Any) -> int:
        """Estimate memory size of an object."""
        if isinstance(obj, str):
            return len(obj.encode('utf-8'))
        elif isinstance(obj, dict):
            return sum(self.estimate_size(k) + self.estimate_size(v) for k, v in obj.items())
        elif isinstance(obj, list):
            return sum(self.estimate_size(item) for item in obj)
        elif isinstance(obj, ContextItem):
            return self.estimate_size(obj.to_dict())
        else:
            # Rough estimate for other objects
            return len(str(obj).encode('utf-8'))
    
    def can_allocate(self, size_bytes: int) -> bool:
        """Check if memory can be allocated."""
        return self.current_usage + size_bytes <= self.max_memory_bytes
    
    def allocate(self, component: str, obj: Any) -> bool:
        """Allocate memory for an object."""
        size_bytes = self.estimate_size(obj)
        
        if not self.can_allocate(size_bytes):
            self.logger.warning(f"Memory allocation failed for {component}: "
                              f"would exceed limit ({size_bytes} bytes requested)")
            return False
        
        if component in self.allocations:
            self.current_usage -= self.allocations[component]
        
        self.allocations[component] = size_bytes
        self.current_usage += size_bytes
        return True
    
    def deallocate(self, component: str) -> None:
        """Deallocate memory for a component."""
        if component in self.allocations:
            self.current_usage -= self.allocations[component]
            del self.allocations[component]
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current memory usage statistics."""
        return {
            "current_usage_mb": self.current_usage / (1024 * 1024),
            "max_memory_mb": self.max_memory_bytes / (1024 * 1024),
            "usage_percentage": (self.current_usage / self.max_memory_bytes) * 100,
            "allocations": {k: v / (1024 * 1024) for k, v in self.allocations.items()}
        }


class ContextStorage:
    """Handles persistent storage of context data."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize context storage.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or Path("src/assistant/data/context.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize database connection and tables."""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            await self._create_tables()
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize context storage: {e}")
            return False
    
    async def _create_tables(self) -> None:
        """Create database tables."""
        cursor = self.conn.cursor()
        
        # Context items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_json TEXT NOT NULL,
                context_type TEXT NOT NULL,
                scope TEXT NOT NULL,
                priority TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL,
                metadata_json TEXT,
                expiry TEXT,
                access_count INTEGER DEFAULT 0,
                last_accessed TEXT NOT NULL
            )
        ''')
        
        # Conversation turns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_turns (
                turn_id TEXT PRIMARY KEY,
                user_input TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                nlu_result_json TEXT,
                timestamp TEXT NOT NULL,
                context_updates_json TEXT,
                metadata_json TEXT
            )
        ''')
        
        # Indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_context_type ON context_items(context_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scope ON context_items(scope)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON context_items(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_expiry ON context_items(expiry)')
        
        self.conn.commit()
    
    async def store_context_item(self, item: ContextItem) -> str:
        """Store a context item."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO context_items 
            (content_json, context_type, scope, priority, timestamp, source, 
             metadata_json, expiry, access_count, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            json.dumps(item.content),
            item.context_type.name,
            item.scope.name,
            item.priority.name,
            item.timestamp.isoformat(),
            item.source,
            json.dumps(item.metadata),
            item.expiry.isoformat() if item.expiry else None,
            item.access_count,
            item.last_accessed.isoformat()
        ))
        
        self.conn.commit()
        return str(cursor.lastrowid)
    
    async def load_context_items(self, 
                                context_type: Optional[ContextType] = None,
                                scope: Optional[ContextScope] = None,
                                limit: int = 100) -> List[ContextItem]:
        """Load context items from storage."""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM context_items WHERE 1=1"
        params = []
        
        if context_type:
            query += " AND context_type = ?"
            params.append(context_type.name)
        
        if scope:
            query += " AND scope = ?"
            params.append(scope.name)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        items = []
        for row in rows:
            item = ContextItem(
                content=json.loads(row[1]),
                context_type=ContextType[row[2]],
                scope=ContextScope[row[3]],
                priority=ContextPriority[row[4]],
                timestamp=datetime.fromisoformat(row[5]),
                source=row[6],
                metadata=json.loads(row[7]) if row[7] else {},
                expiry=datetime.fromisoformat(row[8]) if row[8] else None,
                access_count=row[9],
                last_accessed=datetime.fromisoformat(row[10])            )
            items.append(item)
        
        return items
    
    async def store_conversation_turn(self, turn: ConversationTurn) -> None:
        """Store a conversation turn."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO conversation_turns
            (turn_id, user_input, assistant_response, nlu_result_json,
             timestamp, context_updates_json, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            turn.turn_id,
            turn.user_input,
            turn.assistant_response,
            json.dumps(turn.nlu_result.to_dict()) if (turn.nlu_result and hasattr(turn.nlu_result, 'to_dict')) else None,
            turn.timestamp.isoformat(),
            json.dumps(turn.context_updates),
            json.dumps(turn.metadata)
        ))
        
        self.conn.commit()
    
    async def add_conversation_turn(self, turn: ConversationTurn) -> None:
        """
        Add a conversation turn to the context.
        
        This method updates both in-memory conversation history and persistent storage.
        
        Args:
            turn: The conversation turn to add
        """
        # Add to conversation history deque
        self.conversation_history.append(turn)
        
        # Store in persistent storage
        await self.storage.store_conversation_turn(turn)
        
        self.logger.debug(f"Added conversation turn: {turn.turn_id}")
    
    async def cleanup_expired(self) -> int:
        """Remove expired context items."""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            DELETE FROM context_items 
            WHERE expiry IS NOT NULL AND expiry < ?
            AND scope != ?
        ''', (now, ContextScope.PERMANENT.name))
        
        deleted_count = cursor.rowcount
        self.conn.commit()
        
        return deleted_count
    
    async def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None


class ContextManager:
    """Main context management system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Context Manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.memory_manager = MemoryManager(
            max_memory_mb=self.config.get('max_memory_mb', 10)
        )
        
        # In-memory context storage
        self.active_context: Dict[str, ContextItem] = {}
        self.conversation_history: Deque[ConversationTurn] = deque(
            maxlen=self.config.get('max_conversation_turns', 20)
        )
        
        # Context organization
        self.context_by_type: Dict[ContextType, List[str]] = defaultdict(list)
        self.context_by_scope: Dict[ContextScope, List[str]] = defaultdict(list)
        
        # Persistent storage
        self.storage = ContextStorage(
            self.config.get('db_path')
        )
        
        # Performance tracking
        self.stats = {
            'total_context_items': 0,
            'context_retrievals': 0,
            'context_updates': 0,
            'memory_cleanups': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Current session context
        self.session_id = f"session_{int(time.time())}"
        self.session_start = datetime.now()
        
        self.logger = logging.getLogger(__name__)
        
        if RICH_AVAILABLE:
            self.status_animation = StatusAnimation()
    
    async def initialize(self) -> bool:
        """Initialize context manager."""
        if RICH_AVAILABLE:
            console.print(info_panel("Initializing Context Manager..."))
            await self.status_animation.start("Loading context data")
        
        try:
            # Initialize storage
            if not await self.storage.initialize():
                raise RuntimeError("Failed to initialize context storage")
            
            # Load recent context items
            await self._load_recent_context()
            
            # Set up session context
            await self._initialize_session_context()
            
            if RICH_AVAILABLE:
                await self.status_animation.stop()
                console.print(success_panel("Context Manager initialized successfully"))
            
            self.logger.info("Context Manager initialization completed")
            return True
            
        except Exception as e:
            if RICH_AVAILABLE:
                await self.status_animation.stop()
                console.print(error_panel(f"Context Manager initialization failed: {str(e)}"))
            
            self.logger.error(f"Context Manager initialization failed: {e}")
            return False
    
    async def _load_recent_context(self) -> None:
        """Load recent context items from storage."""
        # Load different types of context
        for context_type in [ContextType.USER_PROFILE, ContextType.TASK, ContextType.CONVERSATION]:
            items = await self.storage.load_context_items(
                context_type=context_type,
                limit=self.config.get('max_context_per_type', 10)
            )
            
            for item in items:
                if not item.is_expired():
                    await self._add_to_active_context(item)
    
    async def _initialize_session_context(self) -> None:
        """Initialize session-specific context."""
        session_context = ContextItem(
            content={
                'session_id': self.session_id,
                'start_time': self.session_start.isoformat(),
                'user_preferences': self.config.get('user_preferences', {}),
                'system_capabilities': self.config.get('system_capabilities', [])
            },
            context_type=ContextType.SESSION,
            scope=ContextScope.MEDIUM_TERM,
            priority=ContextPriority.HIGH,
            source="context_manager"
        )
        
        await self.add_context_item(session_context)
    
    async def add_context_item(self, item: ContextItem) -> str:
        """Add a context item to the manager.
        
        Args:
            item: Context item to add
            
        Returns:
            Context item ID
        """
        # Generate unique ID
        item_id = f"{item.context_type.name}_{int(time.time())}_{len(self.active_context)}"
        
        # Check memory constraints
        if not self.memory_manager.allocate(item_id, item):
            # Try to free memory by removing low-priority items
            await self._cleanup_low_priority_context()
            
            if not self.memory_manager.allocate(item_id, item):
                self.logger.warning(f"Failed to add context item due to memory constraints")
                return ""
        
        # Add to active context
        await self._add_to_active_context(item, item_id)
        
        # Store persistently if appropriate
        if item.scope in [ContextScope.LONG_TERM, ContextScope.PERMANENT]:
            await self.storage.store_context_item(item)
        
        self.stats['total_context_items'] += 1
        self.stats['context_updates'] += 1
        
        return item_id
    
    async def _add_to_active_context(self, item: ContextItem, item_id: Optional[str] = None) -> None:
        """Add item to active context with indexing."""
        if item_id is None:
            item_id = f"{item.context_type.name}_{int(time.time())}_{len(self.active_context)}"
        
        self.active_context[item_id] = item
        self.context_by_type[item.context_type].append(item_id)
        self.context_by_scope[item.scope].append(item_id)
    
    async def get_context(self, 
                         context_type: Optional[ContextType] = None,
                         scope: Optional[ContextScope] = None,
                         query: Optional[str] = None,
                         limit: int = 10) -> List[ContextItem]:
        """Retrieve context items based on criteria.
        
        Args:
            context_type: Filter by context type
            scope: Filter by context scope
            query: Search query for content
            limit: Maximum number of items to return
            
        Returns:
            List of matching context items
        """
        self.stats['context_retrievals'] += 1
        
        # Start with all active context
        candidates = list(self.active_context.values())
        
        # Filter by type
        if context_type:
            candidates = [item for item in candidates if item.context_type == context_type]
        
        # Filter by scope
        if scope:
            candidates = [item for item in candidates if item.scope == scope]
        
        # Filter expired items
        candidates = [item for item in candidates if not item.is_expired()]
        
        # Apply text search if query provided
        if query:
            candidates = await self._search_context_content(candidates, query)
        
        # Sort by relevance (access count, recency, priority)
        candidates.sort(key=lambda item: (
            item.priority.value,
            -item.access_count,
            -item.timestamp.timestamp()
        ))
        
        # Update access statistics
        for item in candidates[:limit]:
            item.access()
        
        return candidates[:limit]
    
    async def _search_context_content(self, items: List[ContextItem], query: str) -> List[ContextItem]:
        """Search context items by content."""
        query_lower = query.lower()
        matching_items = []
        
        for item in items:
            # Convert content to string for search
            content_str = str(item.content).lower()
            
            # Simple text matching (could be enhanced with semantic search)
            if query_lower in content_str:
                matching_items.append(item)
            elif hasattr(item, 'metadata') and query_lower in str(item.metadata).lower():
                matching_items.append(item)
        
        return matching_items
    
    async def update_conversation_context(self, 
                                        user_input: str,
                                        assistant_response: str,
                                        nlu_result: Optional[Any] = None) -> str:
        """Update conversation context with new turn.
        
        Args:
            user_input: User's input
            assistant_response: Assistant's response
            nlu_result: NLU analysis result
            
        Returns:
            Turn ID
        """
        turn_id = f"turn_{int(time.time())}_{len(self.conversation_history)}"
        
        # Create conversation turn
        turn = ConversationTurn(
            turn_id=turn_id,
            user_input=user_input,
            assistant_response=assistant_response,
            nlu_result=nlu_result,
            metadata={'session_id': self.session_id}
        )
        
        # Add to conversation history
        self.conversation_history.append(turn)
        
        # Create context item for this turn
        conversation_context = ContextItem(
            content={
                'user_input': user_input,
                'assistant_response': assistant_response,
                'turn_id': turn_id,
                'intent': nlu_result.intent.category.name if (nlu_result and hasattr(nlu_result, 'intent')) else None,
                'entities': [e.text for e in nlu_result.entities] if (nlu_result and hasattr(nlu_result, 'entities')) else []
            },
            context_type=ContextType.CONVERSATION,
            scope=ContextScope.SHORT_TERM,
            priority=ContextPriority.MEDIUM,
            source=f"conversation_{self.session_id}"
        )
        
        await self.add_context_item(conversation_context)
        
        # Store in persistent storage
        await self.storage.store_conversation_turn(turn)
        
        # Extract and store entities as context
        if nlu_result and hasattr(nlu_result, 'entities'):
            await self._extract_entity_context(nlu_result.entities, turn_id)
        
        return turn_id
    
    async def _extract_entity_context(self, entities: List[Any], turn_id: str) -> None:
        """Extract entity information as context items."""
        for entity in entities:
            if hasattr(entity, 'text') and hasattr(entity, 'entity_type'):
                entity_context = ContextItem(
                    content={
                        'entity_text': entity.text,
                        'entity_type': entity.entity_type.name if hasattr(entity.entity_type, 'name') else str(entity.entity_type),
                        'confidence': getattr(entity, 'confidence', 0.0),
                        'source_turn': turn_id
                    },
                    context_type=ContextType.CONVERSATION,
                    scope=ContextScope.MEDIUM_TERM,
                    priority=ContextPriority.LOW,
                    source=f"entity_extraction_{turn_id}"
                )
                
                await self.add_context_item(entity_context)
    
    async def get_conversation_context(self, turns_back: int = 5) -> List[ConversationTurn]:
        """Get recent conversation context.
        
        Args:
            turns_back: Number of recent turns to retrieve
            
        Returns:
            List of recent conversation turns
        """
        # Return recent turns from deque
        recent_turns = list(self.conversation_history)[-turns_back:]
        return recent_turns
    
    async def switch_context(self, new_context_type: ContextType) -> None:
        """Switch to a different context focus.
        
        Args:
            new_context_type: New context type to focus on
        """
        self.logger.info(f"Switching context focus to {new_context_type.name}")
        
        # Mark current context items with lower priority
        for item_id, item in self.active_context.items():
            if item.context_type != new_context_type:
                if item.priority == ContextPriority.HIGH:
                    item.priority = ContextPriority.MEDIUM
                elif item.priority == ContextPriority.MEDIUM:
                    item.priority = ContextPriority.LOW
        
        # Load more items of the new context type
        additional_items = await self.storage.load_context_items(
            context_type=new_context_type,
            limit=5
        )
        
        for item in additional_items:
            if not item.is_expired():
                await self._add_to_active_context(item)
    
    async def cleanup_expired_context(self) -> int:
        """Remove expired context items from memory and storage.
        
        Returns:
            Number of items cleaned up
        """
        cleanup_count = 0
        
        # Clean up active context
        expired_ids = []
        for item_id, item in self.active_context.items():
            if item.is_expired():
                expired_ids.append(item_id)
        
        for item_id in expired_ids:
            self._remove_from_active_context(item_id)
            cleanup_count += 1
        
        # Clean up persistent storage
        storage_cleanup_count = await self.storage.cleanup_expired()
        cleanup_count += storage_cleanup_count
        
        self.stats['memory_cleanups'] += 1
        self.logger.info(f"Cleaned up {cleanup_count} expired context items")
        
        return cleanup_count
    
    async def _cleanup_low_priority_context(self) -> None:
        """Remove low-priority context items to free memory."""
        # Find low-priority items
        low_priority_ids = []
        for item_id, item in self.active_context.items():
            if item.priority == ContextPriority.LOW and item.scope != ContextScope.PERMANENT:
                low_priority_ids.append(item_id)
        
        # Sort by access count (remove least accessed first)
        low_priority_ids.sort(key=lambda id: self.active_context[id].access_count)
        
        # Remove up to half of low-priority items
        items_to_remove = min(len(low_priority_ids) // 2 + 1, 5)
        
        for item_id in low_priority_ids[:items_to_remove]:
            self._remove_from_active_context(item_id)
        
        self.logger.info(f"Removed {items_to_remove} low-priority context items to free memory")
    
    def _remove_from_active_context(self, item_id: str) -> None:
        """Remove item from active context and indexes."""
        if item_id in self.active_context:
            item = self.active_context[item_id]
            
            # Remove from indexes
            if item_id in self.context_by_type[item.context_type]:
                self.context_by_type[item.context_type].remove(item_id)
            
            if item_id in self.context_by_scope[item.scope]:
                self.context_by_scope[item.scope].remove(item_id)
            
            # Remove from active context
            del self.active_context[item_id]
            
            # Deallocate memory
            self.memory_manager.deallocate(item_id)
    
    async def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context state."""
        return {
            'session_id': self.session_id,
            'session_duration': str(datetime.now() - self.session_start),
            'active_context_items': len(self.active_context),
            'conversation_turns': len(self.conversation_history),
            'context_by_type': {
                context_type.name: len(item_ids) 
                for context_type, item_ids in self.context_by_type.items()
            },
            'context_by_scope': {
                scope.name: len(item_ids)
                for scope, item_ids in self.context_by_scope.items()            },
            'memory_usage': self.memory_manager.get_usage_stats(),
            'statistics': self.stats.copy()
        }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        stats = self.stats.copy()
        stats.update(self.memory_manager.get_usage_stats())
        stats['session_duration'] = str(datetime.now() - self.session_start)
        return stats
    
    async def add_conversation_turn(self, turn: ConversationTurn) -> None:
        """
        Add a conversation turn to the context.
        
        This method updates both in-memory conversation history and persistent storage.
        
        Args:
            turn: The conversation turn to add
        """
        # Add to conversation history deque
        self.conversation_history.append(turn)
        
        # Store in persistent storage
        await self.storage.store_conversation_turn(turn)
        
        self.logger.debug(f"Added conversation turn: {turn.turn_id}")
    
    async def get_current_context(self, context_types: Optional[List[ContextType]] = None) -> Dict[str, Any]:
        """Get current context information.
        
        Args:
            context_types: Optional list of context types to filter by
            
        Returns:
            Dictionary containing current context information
        """
        if context_types is None:
            context_types = [ContextType.CONVERSATION, ContextType.TASK, ContextType.SESSION]
        
        current_context = {}
        
        for context_type in context_types:
            context_items = await self.get_context(
                context_type=context_type,
                limit=5
            )
            current_context[context_type.name.lower()] = [
                item.content for item in context_items
            ]
        
        # Add conversation history
        current_context['conversation_history'] = [
            {
                'user_input': turn.user_input,
                'assistant_response': turn.assistant_response,
                'timestamp': turn.timestamp.isoformat()
            }
            for turn in list(self.conversation_history)[-3:]  # Last 3 turns
        ]
        
        # Add session information
        current_context['session'] = {
            'session_id': self.session_id,
            'duration': str(datetime.now() - self.session_start),
            'total_turns': len(self.conversation_history)
        }
        
        return current_context
    
    async def cleanup(self) -> None:
        """Clean up resources and close connections."""
        if RICH_AVAILABLE:
            console.print(info_panel("Cleaning up Context Manager resources..."))
        
        # Clean up expired context
        await self.cleanup_expired_context()
        
        # Close storage connection
        await self.storage.close()
        
        # Clear memory
        self.active_context.clear()
        self.conversation_history.clear()
        self.context_by_type.clear()
        self.context_by_scope.clear()
        
        self.logger.info("Context Manager cleanup completed")


# Example usage and testing
async def main():
    """Example usage of the Context Manager."""
    if RICH_AVAILABLE:
        console.print(highlight_text("Context Manager Demo", "bold blue"))
    
    # Initialize Context Manager
    context_manager = ContextManager({
        'max_memory_mb': 10,
        'max_conversation_turns': 20,
        'max_context_per_type': 15,
        'user_preferences': {
            'language': 'en',
            'timezone': 'UTC',
            'notification_preferences': ['email', 'desktop']
        }
    })
    
    if not await context_manager.initialize():
        print("Failed to initialize Context Manager")
        return
    
    # Simulate conversation with context updates
    conversations = [
        ("Hello, my name is Alice", "Hello Alice! Nice to meet you."),
        ("I need to schedule a meeting for tomorrow at 3 PM", "I'll help you schedule that meeting. Let me add it to your calendar."),
        ("What was my name again?", "Your name is Alice, as you mentioned earlier."),
        ("Cancel that meeting", "I'll cancel the meeting scheduled for tomorrow at 3 PM.")
    ]
    
    if RICH_AVAILABLE:
        console.print("\n[bold]Simulating conversation with context:[/bold]")
    
    for i, (user_input, assistant_response) in enumerate(conversations):
        # Simulate NLU result (simplified)
        class MockNLUResult:
            def __init__(self, intent_name, entities_text):
                self.intent = type('Intent', (), {'category': type('Category', (), {'name': intent_name})()})()
                self.entities = [type('Entity', (), {'text': text, 'entity_type': type('Type', (), {'name': 'PERSON'})()})() for text in entities_text]
        
        nlu_result = None
        if i == 0:  # First message with name
            nlu_result = MockNLUResult('GREETING', ['Alice'])
        elif i == 1:  # Meeting scheduling
            nlu_result = MockNLUResult('TASK_CREATE', ['tomorrow', '3 PM'])
        
        # Update conversation context
        turn_id = await context_manager.update_conversation_context(
            user_input, assistant_response, nlu_result
        )
        
        if RICH_AVAILABLE:
            console.print(f"\n[blue]Turn {i+1}:[/blue] {user_input}")
            console.print(f"[green]Response:[/green] {assistant_response}")
            console.print(f"[yellow]Turn ID:[/yellow] {turn_id}")
        else:
            print(f"\nTurn {i+1}: {user_input}")
            print(f"Response: {assistant_response}")
            print(f"Turn ID: {turn_id}")
    
    # Demonstrate context retrieval
    if RICH_AVAILABLE:
        console.print("\n[bold]Context Retrieval Examples:[/bold]")
    
    # Get conversation context
    conversation_context = await context_manager.get_context(
        context_type=ContextType.CONVERSATION,
        limit=5
    )
    
    if RICH_AVAILABLE:
        console.print(f"[cyan]Conversation context items:[/cyan] {len(conversation_context)}")
        for item in conversation_context:
            console.print(f"  - {item.content.get('user_input', 'N/A')[:50]}...")
    else:
        print(f"Conversation context items: {len(conversation_context)}")
    
    # Search for specific content
    name_context = await context_manager.get_context(query="Alice")
    if RICH_AVAILABLE:
        console.print(f"[magenta]Context mentioning 'Alice':[/magenta] {len(name_context)} items")
    else:
        print(f"Context mentioning 'Alice': {len(name_context)} items")
    
    # Get context summary
    summary = await context_manager.get_context_summary()
    if RICH_AVAILABLE:
        console.print(f"\n[bold]Context Summary:[/bold]")
        console.print(f"Session ID: {summary['session_id']}")
        console.print(f"Active context items: {summary['active_context_items']}")
        console.print(f"Conversation turns: {summary['conversation_turns']}")
        console.print(f"Memory usage: {summary['memory_usage']['current_usage_mb']:.1f}MB")
    
    # Cleanup
    await context_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
