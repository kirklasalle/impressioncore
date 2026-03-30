#!/usr/bin/env python3
"""
ImpressionCore Personal Assistant Module

This module provides the core personal assistant functionality for ImpressionCore,
implementing brain-inspired multimodal AI assistance optimized for GTX 1050 Ti hardware.

File: assistant/__init__.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-31
Modified: 2025-05-31
Version: 1.0.0

Authors:
- ImpressionCore Development Team
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [assistant, personal-ai, brain-inspired, gtx-1050-ti, memory-optimized, 2025]
Dependencies: [torch, transformers, numpy, asyncio]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements the personal assistant core functionality for ImpressionCore,
providing natural language understanding, knowledge retrieval, contextual response
generation, and multi-modal interaction capabilities.

Phase: 8B Week 1 - Personal Assistant Core Foundation
Memory Budget: 125MB total allocation for assistant components
Performance Target: <3 second response time for complex queries

Architecture Overview:
- Query Processing Pipeline with intent classification and entity extraction
- Natural Language Understanding with context management
- Knowledge Retrieval Engine with UKS integration
- Response Generation with multi-modal output support
- Memory-optimized implementation for GTX 1050 Ti constraints

Components:
- core/: Core assistant functionality (query processing, retrieval, response generation)
- nlp/: Natural language processing components (NLU, context management)
- knowledge/: Knowledge management and UKS integration
- interfaces/: Multi-modal interface handlers (voice, text, visual)

Example Usage:
```python
from assistant import PersonalAssistant

# Initialize assistant with GTX 1050 Ti optimization
assistant = PersonalAssistant(
    memory_limit_mb=125,
    response_timeout=3.0,
    enable_gpu_acceleration=True
)

# Process natural language query
response = await assistant.process_query(
    "What's the weather like today and do I have any meetings?"
)

# Handle multi-modal response
await assistant.handle_response(response, output_mode="voice")
```

Memory Management:
- Query Processor: 15MB allocation limit
- Retrieval Engine: 25MB allocation limit
- NLU Engine: 20MB allocation limit
- Context Manager: 10MB allocation limit
- Response Generator: 30MB allocation limit
- UKS Integration: 15MB allocation limit
- System Overhead: 10MB buffer
Total: 125MB (GTX 1050 Ti compatible)

Performance Targets:
- Intent Recognition: >90% accuracy for common intents
- Response Time: <3 seconds for complex queries
- Memory Usage: <125MB total allocation
- Knowledge Access: <500ms average retrieval time
- Context Retention: 10+ conversation turns

Security Integration:
- Full integration with Phase 8A security infrastructure
- Privacy-compliant query processing and response generation
- Secure knowledge access with authentication controls
- Encrypted context storage and transmission
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Union, TYPE_CHECKING
from pathlib import Path
import sys

# Add project root to path for imports (to allow src.* imports)
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Import types for type hints only (prevents circular imports)
if TYPE_CHECKING:
    from src.services.assistant.core.query_processor import QueryProcessor
    from src.services.assistant.core.retrieval_engine import RetrievalEngine
    from src.services.assistant.nlp.nlu_engine import NLUEngine
    from src.services.assistant.core.context_manager import ContextManager, ConversationTurn
    from src.services.assistant.core.response_generator import ResponseGenerator, GeneratedResponse
    from src.services.assistant.knowledge.uks_integration import (
        UKSIntegration, KnowledgeQuery, KnowledgeItem, 
        KnowledgeSource, KnowledgeType, VerificationStatus
    )

# Core assistant components (lazy loading for memory efficiency)
_query_processor = None
_retrieval_engine = None
_nlu_engine = None
_context_manager = None
_response_generator = None
_uks_integration = None

# Memory management constants
MEMORY_LIMITS = {
    "query_processor": 15,      # MB
    "retrieval_engine": 25,     # MB
    "nlu_engine": 20,          # MB
    "context_manager": 10,      # MB
    "response_generator": 30,   # MB
    "uks_integration": 15,     # MB
    "system_overhead": 10      # MB
}

TOTAL_MEMORY_BUDGET = sum(MEMORY_LIMITS.values())  # 125MB


def get_memory_budget() -> Dict[str, int]:
    """
    Get memory allocation budget for assistant components.
    
    Returns:
        Dictionary mapping component names to memory limits in MB
    """
    return MEMORY_LIMITS.copy()


def get_total_memory_budget() -> int:
    """
    Get total memory budget for assistant system.
    
    Returns:
        Total memory budget in MB
    """
    return TOTAL_MEMORY_BUDGET


async def initialize_assistant_components(enable_gpu: bool = True) -> Dict[str, Any]:
    """
    Initialize all assistant components with memory optimization.
    
    Args:
        enable_gpu: Whether to enable GPU acceleration (GTX 1050 Ti)
        
    Returns:
        Dictionary of initialized components
        
    Raises:
        RuntimeError: If initialization fails or memory constraints violated
    """
    global _query_processor, _retrieval_engine, _nlu_engine
    global _context_manager, _response_generator, _uks_integration
    
    try:        # Lazy import to minimize memory footprint during initialization
        from src.services.assistant.core.query_processor import QueryProcessor
        from src.services.assistant.core.retrieval_engine import RetrievalEngine
        from src.services.assistant.nlp.nlu_engine import NLUEngine
        from src.services.assistant.core.context_manager import ContextManager
        from src.services.assistant.core.response_generator import ResponseGenerator
        from src.services.assistant.knowledge.uks_integration import UKSIntegration
        
        # Initialize components with memory limits
        components = {}
        
        # Query Processor
        if _query_processor is None:
            _query_processor = QueryProcessor(
                memory_limit_mb=MEMORY_LIMITS["query_processor"],
                enable_gpu=enable_gpu
            )
            await _query_processor.initialize()
        components["query_processor"] = _query_processor
        
        # Retrieval Engine
        if _retrieval_engine is None:
            _retrieval_engine = RetrievalEngine(
                memory_limit_mb=MEMORY_LIMITS["retrieval_engine"],
                enable_gpu=enable_gpu
            )
            await _retrieval_engine.initialize()
        components["retrieval_engine"] = _retrieval_engine
        
        # NLU Engine
        if _nlu_engine is None:
            _nlu_engine = NLUEngine(
                memory_limit_mb=MEMORY_LIMITS["nlu_engine"],
                enable_gpu=enable_gpu
            )
            await _nlu_engine.initialize()
        components["nlu_engine"] = _nlu_engine
        
        # Context Manager
        if _context_manager is None:
            _context_manager = ContextManager(
                memory_limit_mb=MEMORY_LIMITS["context_manager"],
                max_turns=10
            )
            await _context_manager.initialize()
        components["context_manager"] = _context_manager
        
        # Response Generator
        if _response_generator is None:
            _response_generator = ResponseGenerator(
                memory_limit_mb=MEMORY_LIMITS["response_generator"],
                enable_gpu=enable_gpu
            )
            await _response_generator.initialize()
        components["response_generator"] = _response_generator
        
        # UKS Integration
        if _uks_integration is None:
            _uks_integration = UKSIntegration(
                memory_limit_mb=MEMORY_LIMITS["uks_integration"]
            )
            await _uks_integration.initialize()
        components["uks_integration"] = _uks_integration
        
        logging.info(f"Assistant components initialized successfully. Memory budget: {TOTAL_MEMORY_BUDGET}MB")
        return components
        
    except Exception as e:
        logging.error(f"Failed to initialize assistant components: {e}")
        raise RuntimeError(f"Assistant initialization failed: {e}")


async def cleanup_assistant_components():
    """
    Clean up assistant components and free memory.
    """
    global _query_processor, _retrieval_engine, _nlu_engine
    global _context_manager, _response_generator, _uks_integration
    
    components = [
        (_query_processor, "query_processor"),
        (_retrieval_engine, "retrieval_engine"), 
        (_nlu_engine, "nlu_engine"),
        (_context_manager, "context_manager"),
        (_response_generator, "response_generator"),
        (_uks_integration, "uks_integration")
    ]
    
    for component, name in components:
        if component is not None:
            try:
                if hasattr(component, 'cleanup'):
                    await component.cleanup()
                logging.info(f"Cleaned up {name}")
            except Exception as e:
                logging.warning(f"Error cleaning up {name}: {e}")
    
    # Reset global references
    _query_processor = None
    _retrieval_engine = None
    _nlu_engine = None
    _context_manager = None
    _response_generator = None
    _uks_integration = None


class AssistantCore:
    """
    Main assistant core class integrating all personal assistant components.
    
    This class provides the unified interface for the ImpressionCore personal assistant,
    coordinating query processing, natural language understanding, knowledge retrieval,    context management, and response generation.
    """
    
    def __init__(self,
                 query_processor: Optional["QueryProcessor"] = None,
                 retrieval_engine: Optional["RetrievalEngine"] = None,
                 nlu_engine: Optional["NLUEngine"] = None,
                 context_manager: Optional["ContextManager"] = None,
                 response_generator: Optional["ResponseGenerator"] = None,
                 uks_integration: Optional["UKSIntegration"] = None,
                 enable_voice: bool = False,
                 enable_vision: bool = False):
        """
        Initialize the assistant core with all components.
        
        Args:
            query_processor: Query processing component
            retrieval_engine: Information retrieval component
            nlu_engine: Natural language understanding component
            context_manager: Conversation context management
            response_generator: Response generation component
            uks_integration: Knowledge integration component (NEW)
            enable_voice: Enable voice interface
            enable_vision: Enable vision interface
        """
        self.query_processor = query_processor
        self.retrieval_engine = retrieval_engine
        self.nlu_engine = nlu_engine
        self.context_manager = context_manager
        self.response_generator = response_generator
        self.uks_integration = uks_integration  # NEW
        self.enable_voice = enable_voice
        self.enable_vision = enable_vision
        
        # State tracking
        self.is_initialized = False
        self.conversation_id = None
          # Performance tracking
        self.query_count = 0
        self.total_response_time = 0.0
        
        logger.info("AssistantCore instance created")
    
    async def initialize(self):
        """Initialize all assistant components."""
        if self.is_initialized:
            return
        
        try:
            # Initialize components if not provided (with lazy imports)
            if self.query_processor is None:
                from src.services.assistant.core.query_processor import QueryProcessor
                self.query_processor = QueryProcessor()
                await self.query_processor.initialize()
            
            if self.retrieval_engine is None:
                from src.services.assistant.core.retrieval_engine import RetrievalEngine
                self.retrieval_engine = RetrievalEngine()
                await self.retrieval_engine.initialize()
            
            if self.nlu_engine is None:
                from src.services.assistant.nlp.nlu_engine import NLUEngine
                self.nlu_engine = NLUEngine()
                await self.nlu_engine.initialize()
            
            if self.context_manager is None:
                from src.services.assistant.core.context_manager import ContextManager
                self.context_manager = ContextManager()
                await self.context_manager.initialize()
            
            if self.response_generator is None:
                from src.services.assistant.core.response_generator import ResponseGenerator
                self.response_generator = ResponseGenerator()
                await self.response_generator.initialize()
            
            if self.uks_integration is None:
                from src.services.assistant.knowledge.uks_integration import UKSIntegration
                self.uks_integration = UKSIntegration()
            
            # Start new conversation
            self.conversation_id = f"conv_{int(time.time())}"
            
            self.is_initialized = True
            logger.info("AssistantCore initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AssistantCore: {e}")
            raise
    
    async def process_query(self,
                          user_input: str,
                          context_data: Optional[Dict[str, Any]] = None) -> "GeneratedResponse":
        """
        Process a user query through the complete assistant pipeline.
        
        Args:
            user_input: User's input text
            context_data: Additional context information
            
        Returns:
            Generated response with full processing results
        """
        if not self.is_initialized:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            # Step 1: Query Processing
            processed_query = await self.query_processor.process_query(user_input)
            
            # Step 2: Natural Language Understanding
            nlu_result = await self.nlu_engine.process(user_input)            # Step 3: Context Management
            from src.services.assistant.core.context_manager import ConversationTurn
            from datetime import datetime
            conversation_turn = ConversationTurn(
                turn_id=f"{self.conversation_id}_turn_{self.query_count + 1}",
                user_input=user_input,
                assistant_response="",  # Will be filled after response generation
                nlu_result=nlu_result,
                timestamp=datetime.now()
            )
            await self.context_manager.add_conversation_turn(conversation_turn)
            current_context = await self.context_manager.get_current_context()
              # Step 4: Knowledge Retrieval (NEW - UKS Integration)
            from src.services.assistant.knowledge.uks_integration import KnowledgeQuery
            knowledge_query = KnowledgeQuery(
                query_text=user_input,
                intent=nlu_result.intent.category,
                entities=[e.text for e in nlu_result.entities],
                context=context_data or {},
                max_results=5,
                min_confidence=0.5            )
            knowledge_response = await self.uks_integration.query_knowledge(knowledge_query)
              # Step 5: Response Generation - Create ResponseContext
            from .core.response_generator import ResponseContext
            response_context = ResponseContext(
                user_input=user_input,
                nlu_result=nlu_result,
                conversation_history=[],  # TODO: Extract from current_context
                session_context=current_context.get('session', {}),
                metadata={
                    'processed_query': processed_query,
                    'knowledge_items': knowledge_response.items
                }
            )
            
            response = await self.response_generator.generate_response(response_context)
            
            # Update performance tracking
            processing_time = time.time() - start_time
            self.query_count += 1
            self.total_response_time += processing_time
            
            # Add processing metadata to response
            response.metadata.update({
                'processing_time': processing_time,
                'query_count': self.query_count,
                'knowledge_items_found': len(knowledge_response.items),
                'knowledge_confidence': knowledge_response.confidence_score,
                'cache_hit': knowledge_response.cache_hit
            })
            
            logger.info(f"Query processed in {processing_time:.3f}s with {len(knowledge_response.items)} knowledge items")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")            # Return error response
            from src.services.assistant.core.response_generator import GeneratedResponse, ResponseType, ResponseStyle
            return GeneratedResponse(
                content=f"I apologize, but I encountered an error while processing your request: {str(e)}",
                response_type=ResponseType.ERROR,
                response_style=ResponseStyle.CASUAL,
                confidence=0.0,
                metadata={'error': str(e), 'processing_time': time.time() - start_time}
            )
    
    async def add_knowledge(self,
                          content: str, 
                          source: "KnowledgeSource" = None,
                          knowledge_type: "KnowledgeType" = None) -> bool:
        """
        Add knowledge to the assistant's knowledge base.
        
        Args:
            content: Knowledge content
            source: Knowledge source (defaults to USER_KNOWLEDGE)
            knowledge_type: Type of knowledge (defaults to FACTUAL)
            
        Returns:
            True if successfully added
        """
        if not self.is_initialized:
            await self.initialize()
          # Import at runtime to avoid circular imports
        from src.services.assistant.knowledge.uks_integration import (
            KnowledgeItem, KnowledgeSource, KnowledgeType, VerificationStatus
        )
        
        # Set defaults if not provided
        if source is None:
            source = KnowledgeSource.USER_KNOWLEDGE
        if knowledge_type is None:
            knowledge_type = KnowledgeType.FACTUAL
        
        knowledge_item = KnowledgeItem(
            id=f"user_knowledge_{int(time.time())}_{hash(content) % 10000}",
            content=content,
            source=source,
            knowledge_type=knowledge_type,
            confidence=0.8,
            verification_status=VerificationStatus.UNVERIFIED
        )
        
        return await self.uks_integration.add_knowledge(knowledge_item)
    
    async def get_conversation_history(self, limit: int = 10) -> List["ConversationTurn"]:
        """Get recent conversation history."""
        if not self.is_initialized:
            await self.initialize()
        
        return await self.context_manager.get_conversation_history(limit=limit)
    
    async def clear_conversation(self):
        """Clear current conversation and start fresh."""
        if not self.is_initialized:
            await self.initialize()
        
        await self.context_manager.clear_conversation()
        self.conversation_id = f"conv_{int(time.time())}"
        self.query_count = 0
        logger.info("Conversation cleared")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get assistant performance statistics."""
        stats = {
            'query_count': self.query_count,
            'average_response_time': (
                self.total_response_time / self.query_count 
                if self.query_count > 0 else 0.0
            ),
            'conversation_id': self.conversation_id,
            'is_initialized': self.is_initialized,
            'voice_enabled': self.enable_voice,
            'vision_enabled': self.enable_vision
        }
        
        # Add component statistics if available
        if self.uks_integration:
            stats['knowledge_stats'] = self.uks_integration.get_statistics()
        
        if self.context_manager:
            context_stats = await self.context_manager.get_statistics()
            stats['context_stats'] = context_stats
        
        return stats
    
    async def cleanup(self):
        """Clean up assistant resources."""
        try:
            components = [
                (self.query_processor, "query_processor"),
                (self.retrieval_engine, "retrieval_engine"),
                (self.nlu_engine, "nlu_engine"),
                (self.context_manager, "context_manager"),
                (self.response_generator, "response_generator"),
                (self.uks_integration, "uks_integration")
            ]
            
            for component, name in components:
                if component is not None and hasattr(component, 'cleanup'):
                    await component.cleanup()
                    logger.debug(f"Cleaned up {name}")
            
            self.is_initialized = False
            logger.info("AssistantCore cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


class PersonalAssistant(AssistantCore):
    """
    User-friendly wrapper for the AssistantCore with simplified interface.
    """
    
    def __init__(self, **kwargs):
        """Initialize personal assistant with default settings."""
        super().__init__(**kwargs)
        self.user_preferences = {}
    
    async def ask(self, question: str) -> str:
        """
        Simple question-answer interface.
        
        Args:
            question: User's question
            
        Returns:
            Assistant's response text        """
        response = await self.process_query(question)
        return response.content
    
    async def learn(self, fact: str) -> bool:
        """
        Teach the assistant a new fact.
        
        Args:
            fact: Fact to learn
              Returns:
            True if successfully learned
        """
        from src.services.assistant.knowledge.uks_integration import KnowledgeSource
        return await self.add_knowledge(fact, KnowledgeSource.USER_KNOWLEDGE)
    
    async def remember(self, key: str, value: Any):
        """Remember user preference or information."""
        self.user_preferences[key] = value
        
        # Add to knowledge base as contextual information
        from src.services.assistant.knowledge.uks_integration import KnowledgeSource, KnowledgeType
        content = f"User preference: {key} = {value}"
        await self.add_knowledge(content, KnowledgeSource.USER_KNOWLEDGE, KnowledgeType.CONTEXTUAL)
    
    async def forget(self, topic: str):
        """Clear conversation history related to a topic."""
        # This would be more sophisticated in production
        await self.clear_conversation()
        logger.info(f"Cleared conversation history for topic: {topic}")


# Factory functions for convenient instance creation
async def create_assistant_core(
    memory_limit_mb: int = 125,
    enable_gpu: bool = True,
    enable_voice: bool = False,
    enable_vision: bool = False
) -> AssistantCore:
    """
    Factory function to create and initialize an AssistantCore instance.
    
    Args:
        memory_limit_mb: Total memory limit for assistant components
        enable_gpu: Whether to enable GPU acceleration (GTX 1050 Ti)
        enable_voice: Enable voice interface
        enable_vision: Enable vision interface
        
    Returns:
        Initialized AssistantCore instance
    """
    assistant = AssistantCore(
        enable_voice=enable_voice,
        enable_vision=enable_vision
    )
    await assistant.initialize()
    return assistant


async def create_personal_assistant(
    memory_limit_mb: int = 125,
    response_timeout: float = 3.0,
    enable_gpu: bool = True
) -> PersonalAssistant:
    """
    Factory function to create and initialize a PersonalAssistant instance.
    
    Args:
        memory_limit_mb: Total memory limit for assistant components
        response_timeout: Maximum response time in seconds
        enable_gpu: Whether to enable GPU acceleration (GTX 1050 Ti)
        
    Returns:
        Initialized PersonalAssistant instance
    """
    assistant = PersonalAssistant(
        memory_limit_mb=memory_limit_mb,
        response_timeout=response_timeout,        enable_gpu_acceleration=enable_gpu
    )
    await assistant.initialize()
    return assistant


# Public API exports
__all__ = [
    # Core classes
    "AssistantCore",
    "PersonalAssistant",
    
    # Utility functions
    "get_memory_budget",
    "get_total_memory_budget", 
    "initialize_assistant_components",
    "cleanup_assistant_components",
    
    # Constants
    "MEMORY_LIMITS",
    "TOTAL_MEMORY_BUDGET",
    
    # Factory function
    "create_assistant_core",
    "create_personal_assistant"
]


# Module initialization
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("ImpressionCore Personal Assistant Module loaded - Phase 8B Week 1")
