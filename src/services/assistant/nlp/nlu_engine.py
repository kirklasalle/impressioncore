"""
Enhanced Natural Language Understanding Engine for Phase 8B Personal Assistant

This module provides comprehensive NLU capabilities including advanced intent recognition,
named entity recognition, sentiment analysis, and context-aware understanding.
Optimized for GTX 1050 Ti hardware constraints with memory-efficient processing.

Author: ImpressionCore Development Team
Created: 2025-01-18
Version: 1.0.0
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
Memory Budget: 20MB maximum allocation
"""

import asyncio
import logging
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any, Dict, List, Optional, Set, Tuple, Union, 
    Callable, Awaitable, NamedTuple
)
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)

# Core NLP and ML imports with memory optimization
try:
    import spacy
    from spacy.lang.en import English
    import torch
    import numpy as np
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        pipeline, set_seed
    )
    from sentence_transformers import SentenceTransformer
    import json
    import sqlite3
    from collections import defaultdict, Counter
    from datetime import datetime, timedelta
    
    ML_AVAILABLE = True
except ImportError as e:
    ML_AVAILABLE = False
    logging.warning(f"ML dependencies not available: {e}")

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


class IntentCategory(Enum):
    """Enhanced intent categories for comprehensive understanding."""
    
    # Core interaction intents
    GREETING = auto()
    FAREWELL = auto()
    QUESTION = auto()
    REQUEST = auto()
    COMMAND = auto()
    
    # Information and search intents
    SEARCH = auto()
    INFORMATION = auto()
    DEFINITION = auto()
    EXPLANATION = auto()
    COMPARISON = auto()
    
    # Task and productivity intents
    TASK_CREATE = auto()
    TASK_UPDATE = auto()
    TASK_DELETE = auto()
    TASK_QUERY = auto()
    REMINDER = auto()
    SCHEDULING = auto()
    
    # Personal assistant intents
    WEATHER = auto()
    NEWS = auto()
    ENTERTAINMENT = auto()
    CALCULATION = auto()
    TRANSLATION = auto()
    
    # System and control intents
    SYSTEM_CONTROL = auto()
    SETTINGS = auto()
    HELP = auto()
    FEEDBACK = auto()
    
    # Conversation management
    CONVERSATION = auto()
    CLARIFICATION = auto()
    CONFIRMATION = auto()
    NEGATION = auto()
    
    # Unknown or unclear
    UNKNOWN = auto()


class EntityType(Enum):
    """Comprehensive entity types for extraction."""
    
    # People and organizations
    PERSON = auto()
    ORGANIZATION = auto()
    LOCATION = auto()
    
    # Time and date
    DATE = auto()
    TIME = auto()
    DURATION = auto()
    
    # Numbers and quantities
    NUMBER = auto()
    MONEY = auto()
    PERCENTAGE = auto()
    QUANTITY = auto()
    
    # Technology and systems
    SOFTWARE = auto()
    HARDWARE = auto()
    FILE = auto()
    URL = auto()
    EMAIL = auto()
    
    # Tasks and activities
    TASK = auto()
    PROJECT = auto()
    EVENT = auto()
    REMINDER = auto()
    
    # Miscellaneous
    PRODUCT = auto()
    SKILL = auto()
    TOPIC = auto()
    CUSTOM = auto()


class SentimentType(Enum):
    """Sentiment classification types."""
    
    POSITIVE = auto()
    NEGATIVE = auto()
    NEUTRAL = auto()
    MIXED = auto()
    UNKNOWN = auto()


@dataclass
class Entity:
    """Represents an extracted named entity."""
    
    text: str
    entity_type: EntityType
    start_pos: int
    end_pos: int
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate entity data."""
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        if self.start_pos < 0 or self.end_pos <= self.start_pos:
            raise ValueError(f"Invalid position range: {self.start_pos}-{self.end_pos}")


@dataclass
class Intent:
    """Represents a classified intent."""
    
    category: IntentCategory
    confidence: float
    subcategory: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate intent data."""
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")


@dataclass
class Sentiment:
    """Represents sentiment analysis results."""
    
    sentiment_type: SentimentType
    confidence: float
    polarity: float  # -1 to 1
    subjectivity: float  # 0 to 1
    emotions: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate sentiment data."""
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        if not -1 <= self.polarity <= 1:
            raise ValueError(f"Polarity must be between -1 and 1, got {self.polarity}")
        if not 0 <= self.subjectivity <= 1:
            raise ValueError(f"Subjectivity must be between 0 and 1, got {self.subjectivity}")


@dataclass
class NLUResult:
    """Comprehensive NLU analysis results."""
    
    input_text: str
    processed_text: str
    intent: Intent
    entities: List[Entity]
    sentiment: Sentiment
    context_features: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    confidence_overall: float = 0.0
    
    def __post_init__(self):
        """Calculate overall confidence."""
        if not self.confidence_overall:
            # Weighted average of intent and sentiment confidence
            self.confidence_overall = (
                self.intent.confidence * 0.6 + 
                self.sentiment.confidence * 0.4
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert NLUResult to dictionary for JSON serialization."""
        return {
            'input_text': self.input_text,
            'processed_text': self.processed_text,
            'intent': {
                'category': self.intent.category.name if hasattr(self.intent.category, 'name') else str(self.intent.category),
                'confidence': self.intent.confidence,
                'subcategory': self.intent.subcategory,
                'parameters': self.intent.parameters
            },
            'entities': [
                {
                    'text': entity.text,
                    'entity_type': entity.entity_type.name if hasattr(entity.entity_type, 'name') else str(entity.entity_type),
                    'confidence': entity.confidence,
                    'start_pos': entity.start_pos,
                    'end_pos': entity.end_pos
                } for entity in self.entities
            ],
            'sentiment': {
                'sentiment_type': self.sentiment.sentiment_type.name if hasattr(self.sentiment.sentiment_type, 'name') else str(self.sentiment.sentiment_type),
                'confidence': self.sentiment.confidence,
                'polarity': self.sentiment.polarity,
                'subjectivity': self.sentiment.subjectivity,
                'emotions': self.sentiment.emotions
            },
            'context_features': self.context_features,
            'processing_time': self.processing_time,
            'confidence_overall': self.confidence_overall
        }


class MemoryManager:
    """Memory management for GTX 1050 Ti optimization."""
    
    def __init__(self, max_memory_mb: int = 20):
        """Initialize memory manager.
        
        Args:
            max_memory_mb: Maximum memory allocation in MB
        """
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.current_usage = 0
        self.allocations = {}
        
        self.logger = logging.getLogger(__name__)
    
    def allocate(self, component: str, size_bytes: int) -> bool:
        """Attempt to allocate memory for a component.
        
        Args:
            component: Component name
            size_bytes: Requested memory size
            
        Returns:
            True if allocation successful
        """
        if self.current_usage + size_bytes > self.max_memory_bytes:
            self.logger.warning(f"Memory allocation failed for {component}: "
                              f"would exceed limit ({size_bytes} bytes requested)")
            return False
        
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
            "allocations": self.allocations.copy()
        }


class BaseIntentClassifier(ABC):
    """Abstract base class for intent classifiers."""
    
    @abstractmethod
    async def classify_intent(self, text: str) -> Intent:
        """Classify intent from text."""
        pass
    
    @abstractmethod
    def get_supported_intents(self) -> List[IntentCategory]:
        """Get list of supported intent categories."""
        pass


class RuleBasedIntentClassifier(BaseIntentClassifier):
    """Rule-based intent classifier for fast, reliable classification."""
    
    def __init__(self):
        """Initialize rule-based classifier."""
        self.intent_patterns = self._build_intent_patterns()
        self.logger = logging.getLogger(__name__)
    
    def _build_intent_patterns(self) -> Dict[IntentCategory, List[re.Pattern]]:
        """Build regex patterns for intent classification."""
        patterns = {
            IntentCategory.GREETING: [
                re.compile(r'\b(hello|hi|hey|greetings|good\s+(morning|afternoon|evening))\b', re.I),
                re.compile(r'^(what\'s\s+up|how.*going|howdy)\b', re.I),
            ],
            IntentCategory.FAREWELL: [
                re.compile(r'\b(goodbye|bye|farewell|see\s+you|talk\s+later)\b', re.I),
                re.compile(r'\b(good\s+(night|day)|take\s+care)\b', re.I),
            ],
            IntentCategory.QUESTION: [
                re.compile(r'^(what|when|where|who|why|how|which|whose)\b', re.I),
                re.compile(r'\?\s*$'),
                re.compile(r'\b(can\s+you|could\s+you|would\s+you|do\s+you\s+know)\b', re.I),
            ],
            IntentCategory.TASK_CREATE: [
                re.compile(r'\b(create|add|make|new)\s+(task|todo|reminder)\b', re.I),
                re.compile(r'\b(remind\s+me|schedule|plan)\b', re.I),
            ],
            IntentCategory.WEATHER: [
                re.compile(r'\b(weather|forecast|temperature|rain|snow|sunny)\b', re.I),
                re.compile(r'\b(how.*weather|what.*weather)\b', re.I),
            ],
            IntentCategory.CALCULATION: [
                re.compile(r'\b(calculate|compute|math|arithmetic)\b', re.I),
                re.compile(r'[\d\+\-\*\/\(\)]+'),
                re.compile(r'\b(what.*is.*plus|minus|times|divided)\b', re.I),
            ],
            IntentCategory.SEARCH: [
                re.compile(r'\b(search|find|look\s+for|lookup)\b', re.I),
                re.compile(r'\b(google|bing|search\s+for)\b', re.I),
            ],
            IntentCategory.SYSTEM_CONTROL: [
                re.compile(r'\b(shutdown|restart|sleep|hibernate|lock)\b', re.I),
                re.compile(r'\b(open|close|start|stop|launch)\s+(application|app|program)\b', re.I),
            ],
            IntentCategory.HELP: [
                re.compile(r'\b(help|assist|support|guide|how\s+to)\b', re.I),
                re.compile(r'\b(what\s+can\s+you|show\s+me\s+how)\b', re.I),
            ]
        }
        
        # Compile all patterns
        for intent, pattern_list in patterns.items():
            patterns[intent] = [p if isinstance(p, re.Pattern) else re.compile(p, re.I) 
                              for p in pattern_list]
        
        return patterns
    
    async def classify_intent(self, text: str) -> Intent:
        """Classify intent using rule-based patterns."""
        text = text.strip().lower()
        best_intent = IntentCategory.UNKNOWN
        best_confidence = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            matches = 0
            total_patterns = len(patterns)
            
            for pattern in patterns:
                if pattern.search(text):
                    matches += 1
            
            if matches > 0:
                confidence = matches / total_patterns
                if confidence > best_confidence:
                    best_intent = intent
                    best_confidence = confidence
        
        # Boost confidence for exact matches
        if best_confidence > 0:
            best_confidence = min(0.95, best_confidence + 0.1)
        else:
            best_confidence = 0.1  # Minimum confidence for unknown
        
        return Intent(
            category=best_intent,
            confidence=best_confidence,
            parameters={"classification_method": "rule_based"}
        )
    
    def get_supported_intents(self) -> List[IntentCategory]:
        """Get list of supported intent categories."""
        return list(self.intent_patterns.keys())


class MLIntentClassifier(BaseIntentClassifier):
    """ML-based intent classifier using transformers."""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-small"):
        """Initialize ML classifier."""
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.logger = logging.getLogger(__name__)
        
        # Training data for few-shot learning
        self.training_examples = self._build_training_examples()
    
    def _build_training_examples(self) -> Dict[IntentCategory, List[str]]:
        """Build training examples for each intent category."""
        return {
            IntentCategory.GREETING: [
                "hello", "hi there", "good morning", "hey", "greetings"
            ],
            IntentCategory.QUESTION: [
                "what is the weather", "how do I", "when will", "where can I find"
            ],
            IntentCategory.TASK_CREATE: [
                "create a task", "remind me to", "add to my todo", "schedule meeting"
            ],
            IntentCategory.SEARCH: [
                "search for", "find information about", "look up", "google"
            ],
            IntentCategory.WEATHER: [
                "weather forecast", "is it raining", "temperature today", "sunny outside"
            ]
        }
    
    async def initialize(self) -> bool:
        """Initialize ML models."""
        if not ML_AVAILABLE:
            self.logger.warning("ML dependencies not available, using fallback")
            return False
        
        try:
            # Use a lightweight sentiment model for intent classification
            self.pipeline = pipeline(
                "text-classification",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=-1  # CPU only for GTX 1050 Ti compatibility
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize ML classifier: {e}")
            return False
    
    async def classify_intent(self, text: str) -> Intent:
        """Classify intent using ML models."""
        if not self.pipeline:
            # Fallback to rule-based
            fallback = RuleBasedIntentClassifier()
            return await fallback.classify_intent(text)
        
        try:
            # Simple ML-based classification
            # This is a simplified approach; in production, you'd train a proper intent classifier
            
            # Analyze sentiment to inform intent
            sentiment_result = self.pipeline(text)
            sentiment_score = sentiment_result[0]['score']
            
            # Use keyword matching with ML enhancement
            text_lower = text.lower()
            
            # Question patterns
            if any(word in text_lower for word in ['what', 'when', 'where', 'how', 'why', 'who']):
                return Intent(IntentCategory.QUESTION, confidence=0.8 + sentiment_score * 0.1)
            
            # Task creation patterns
            if any(word in text_lower for word in ['create', 'add', 'remind', 'schedule']):
                return Intent(IntentCategory.TASK_CREATE, confidence=0.7 + sentiment_score * 0.1)
            
            # Search patterns
            if any(word in text_lower for word in ['search', 'find', 'look', 'google']):
                return Intent(IntentCategory.SEARCH, confidence=0.75 + sentiment_score * 0.1)
            
            # Default classification
            return Intent(IntentCategory.CONVERSATION, confidence=0.5)
            
        except Exception as e:
            self.logger.error(f"ML classification failed: {e}")
            # Fallback to rule-based
            fallback = RuleBasedIntentClassifier()
            return await fallback.classify_intent(text)
    
    def get_supported_intents(self) -> List[IntentCategory]:
        """Get list of supported intent categories."""
        return list(self.training_examples.keys())


class EntityExtractor:
    """Named entity recognition and extraction."""
    
    def __init__(self):
        """Initialize entity extractor."""
        self.nlp = None
        self.custom_patterns = self._build_custom_patterns()
        self.logger = logging.getLogger(__name__)
    
    def _build_custom_patterns(self) -> Dict[EntityType, List[re.Pattern]]:
        """Build custom regex patterns for entity extraction."""
        return {
            EntityType.EMAIL: [
                re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
            ],
            EntityType.URL: [
                re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
                re.compile(r'\b(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}\b')
            ],
            EntityType.TIME: [
                re.compile(r'\b(?:[01]?[0-9]|2[0-3]):[0-5][0-9](?:\s*[AP]M)?\b', re.I),
                re.compile(r'\b(?:morning|afternoon|evening|night|noon|midnight)\b', re.I)
            ],
            EntityType.DATE: [
                re.compile(r'\b(?:today|tomorrow|yesterday)\b', re.I),
                re.compile(r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', re.I),
                re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b')
            ],
            EntityType.NUMBER: [
                re.compile(r'\b\d+(?:\.\d+)?\b'),
                re.compile(r'\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten)\b', re.I)
            ],
            EntityType.MONEY: [
                re.compile(r'\$\d+(?:\.\d{2})?\b'),
                re.compile(r'\b\d+(?:\.\d{2})?\s*(?:dollars?|cents?|USD)\b', re.I)
            ]
        }
    
    async def initialize(self) -> bool:
        """Initialize spaCy NLP model."""
        if not ML_AVAILABLE:
            self.logger.warning("spaCy not available, using regex-only extraction")
            return True
        
        try:
            # Use small English model for memory efficiency
            self.nlp = spacy.load("en_core_web_sm")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to load spaCy model: {e}")
            return True  # Continue with regex-only
    
    async def extract_entities(self, text: str) -> List[Entity]:
        """Extract named entities from text."""
        entities = []
        
        # spaCy-based extraction
        if self.nlp:
            try:
                doc = self.nlp(text)
                for ent in doc.ents:
                    entity_type = self._map_spacy_label(ent.label_)
                    if entity_type:
                        entities.append(Entity(
                            text=ent.text,
                            entity_type=entity_type,
                            start_pos=ent.start_char,
                            end_pos=ent.end_char,
                            confidence=0.8,  # spaCy doesn't provide confidence scores directly
                            metadata={"spacy_label": ent.label_}
                        ))
            except Exception as e:
                self.logger.error(f"spaCy extraction failed: {e}")
        
        # Custom regex-based extraction
        entities.extend(await self._extract_with_regex(text))
        
        # Remove duplicates and sort by position
        entities = self._deduplicate_entities(entities)
        entities.sort(key=lambda e: e.start_pos)
        
        return entities
    
    def _map_spacy_label(self, spacy_label: str) -> Optional[EntityType]:
        """Map spaCy entity labels to our EntityType enum."""
        mapping = {
            "PERSON": EntityType.PERSON,
            "ORG": EntityType.ORGANIZATION,
            "GPE": EntityType.LOCATION,  # Geopolitical entity
            "LOC": EntityType.LOCATION,
            "DATE": EntityType.DATE,
            "TIME": EntityType.TIME,
            "MONEY": EntityType.MONEY,
            "PERCENT": EntityType.PERCENTAGE,
            "QUANTITY": EntityType.QUANTITY,
            "CARDINAL": EntityType.NUMBER,
            "ORDINAL": EntityType.NUMBER
        }
        return mapping.get(spacy_label)
    
    async def _extract_with_regex(self, text: str) -> List[Entity]:
        """Extract entities using custom regex patterns."""
        entities = []
        
        for entity_type, patterns in self.custom_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    entities.append(Entity(
                        text=match.group(),
                        entity_type=entity_type,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.7,  # Lower confidence for regex
                        metadata={"extraction_method": "regex"}
                    ))
        
        return entities
    
    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remove duplicate entities based on text and position overlap."""
        if not entities:
            return entities
        
        # Sort by confidence (highest first)
        entities.sort(key=lambda e: e.confidence, reverse=True)
        
        deduplicated = []
        for entity in entities:
            overlap = False
            for existing in deduplicated:
                # Check for position overlap
                if (entity.start_pos < existing.end_pos and 
                    entity.end_pos > existing.start_pos):
                    overlap = True
                    break
            
            if not overlap:
                deduplicated.append(entity)
        
        return deduplicated


class SentimentAnalyzer:
    """Sentiment analysis with emotion detection."""
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        self.pipeline = None
        self.emotion_patterns = self._build_emotion_patterns()
        self.logger = logging.getLogger(__name__)
    
    def _build_emotion_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Build emotion detection patterns."""
        return {
            "joy": [
                re.compile(r'\b(happy|joy|excited|delighted|pleased|glad)\b', re.I),
                re.compile(r'[!]{2,}|\b(yay|woohoo|awesome|great)\b', re.I)
            ],
            "anger": [
                re.compile(r'\b(angry|mad|furious|irritated|annoyed)\b', re.I),
                re.compile(r'\b(damn|hate|stupid|ridiculous)\b', re.I)
            ],
            "sadness": [
                re.compile(r'\b(sad|depressed|disappointed|upset|down)\b', re.I),
                re.compile(r'\b(crying|tears|broken|hurt)\b', re.I)
            ],
            "fear": [
                re.compile(r'\b(afraid|scared|worried|anxious|nervous)\b', re.I),
                re.compile(r'\b(terrified|panic|frightened)\b', re.I)
            ],
            "surprise": [
                re.compile(r'\b(surprised|shocked|amazed|astonished)\b', re.I),
                re.compile(r'\b(wow|omg|unbelievable|incredible)\b', re.I)
            ]
        }
    
    async def initialize(self) -> bool:
        """Initialize sentiment analysis pipeline."""
        if not ML_AVAILABLE:
            self.logger.warning("ML dependencies not available for sentiment analysis")
            return True  # Continue with rule-based
        
        try:
            self.pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=-1  # CPU only
            )
            return True
        except Exception as e:
            self.logger.warning(f"Failed to initialize sentiment pipeline: {e}")
            return True  # Continue with rule-based
    
    async def analyze_sentiment(self, text: str) -> Sentiment:
        """Analyze sentiment and emotions in text."""
        # ML-based sentiment analysis
        if self.pipeline:
            try:
                result = self.pipeline(text)
                label = result[0]['label'].lower()
                score = result[0]['score']
                
                # Map transformer labels to our sentiment types
                sentiment_mapping = {
                    'positive': SentimentType.POSITIVE,
                    'negative': SentimentType.NEGATIVE,
                    'neutral': SentimentType.NEUTRAL
                }
                
                sentiment_type = sentiment_mapping.get(label, SentimentType.NEUTRAL)
                polarity = score if sentiment_type == SentimentType.POSITIVE else -score
                
            except Exception as e:
                self.logger.error(f"ML sentiment analysis failed: {e}")
                sentiment_type, score, polarity = await self._analyze_rule_based(text)
        else:
            sentiment_type, score, polarity = await self._analyze_rule_based(text)
        
        # Emotion detection
        emotions = await self._detect_emotions(text)
        
        # Calculate subjectivity based on emotion intensity
        subjectivity = min(1.0, sum(emotions.values()) / len(emotions) if emotions else 0.3)
        
        return Sentiment(
            sentiment_type=sentiment_type,
            confidence=score,
            polarity=polarity,
            subjectivity=subjectivity,
            emotions=emotions
        )
    
    async def _analyze_rule_based(self, text: str) -> Tuple[SentimentType, float, float]:
        """Rule-based sentiment analysis fallback."""
        text_lower = text.lower()
        
        positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied'
        ]
        
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike',
            'sad', 'angry', 'frustrated', 'disappointed', 'annoyed'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment_type = SentimentType.POSITIVE
            polarity = min(1.0, positive_count * 0.3)
            confidence = min(0.8, 0.5 + polarity * 0.3)
        elif negative_count > positive_count:
            sentiment_type = SentimentType.NEGATIVE
            polarity = -min(1.0, negative_count * 0.3)
            confidence = min(0.8, 0.5 + abs(polarity) * 0.3)
        else:
            sentiment_type = SentimentType.NEUTRAL
            polarity = 0.0
            confidence = 0.6
        
        return sentiment_type, confidence, polarity
    
    async def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions using pattern matching."""
        emotions = {}
        
        for emotion, patterns in self.emotion_patterns.items():
            matches = 0
            for pattern in patterns:
                matches += len(pattern.findall(text))
            
            if matches > 0:
                # Normalize emotion intensity
                emotions[emotion] = min(1.0, matches * 0.3)
        
        return emotions


class NLUEngine:
    """Main Natural Language Understanding Engine."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize NLU Engine.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.memory_manager = MemoryManager(
            max_memory_mb=self.config.get('max_memory_mb', 20)
        )
        
        # Component initialization
        self.intent_classifier = None
        self.entity_extractor = None
        self.sentiment_analyzer = None
        
        # Performance tracking
        self.processing_stats = {
            'total_requests': 0,
            'average_processing_time': 0.0,
            'error_count': 0,
            'cache_hits': 0
        }
        
        # Simple caching for repeated queries
        self.cache = {}
        self.cache_max_size = self.config.get('cache_size', 100)
        
        self.logger = logging.getLogger(__name__)
        
        if RICH_AVAILABLE:
            self.status_animation = StatusAnimation()
    
    async def initialize(self) -> bool:
        """Initialize all NLU components."""
        if RICH_AVAILABLE:
            console.print(info_panel("Initializing NLU Engine..."))
            await self.status_animation.start("Loading NLU components")
        
        try:
            # Allocate memory for components
            if not self.memory_manager.allocate("intent_classifier", 5 * 1024 * 1024):  # 5MB
                raise RuntimeError("Failed to allocate memory for intent classifier")
            
            if not self.memory_manager.allocate("entity_extractor", 8 * 1024 * 1024):  # 8MB
                raise RuntimeError("Failed to allocate memory for entity extractor")
            
            if not self.memory_manager.allocate("sentiment_analyzer", 7 * 1024 * 1024):  # 7MB
                raise RuntimeError("Failed to allocate memory for sentiment analyzer")
            
            # Initialize components
            if self.config.get('use_ml_intent', True) and ML_AVAILABLE:
                self.intent_classifier = MLIntentClassifier()
                await self.intent_classifier.initialize()
            else:
                self.intent_classifier = RuleBasedIntentClassifier()
            
            self.entity_extractor = EntityExtractor()
            await self.entity_extractor.initialize()
            
            self.sentiment_analyzer = SentimentAnalyzer()
            await self.sentiment_analyzer.initialize()
            
            if RICH_AVAILABLE:
                await self.status_animation.stop()
                console.print(success_panel("NLU Engine initialized successfully"))
            
            self.logger.info("NLU Engine initialization completed")
            return True
            
        except Exception as e:
            if RICH_AVAILABLE:
                await self.status_animation.stop()
                console.print(error_panel(f"NLU initialization failed: {str(e)}"))
            
            self.logger.error(f"NLU Engine initialization failed: {e}")
            return False
    
    async def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> NLUResult:
        """Process text through complete NLU pipeline.
        
        Args:
            text: Input text to process
            context: Optional context information
            
        Returns:
            Complete NLU analysis results
        """
        start_time = time.time()
        context = context or {}
        
        # Check cache first
        cache_key = f"{text}:{hash(str(context))}"
        if cache_key in self.cache:
            self.processing_stats['cache_hits'] += 1
            return self.cache[cache_key]
        
        try:
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            # Run NLU components in parallel for efficiency
            intent_task = asyncio.create_task(
                self.intent_classifier.classify_intent(processed_text)
            )
            entities_task = asyncio.create_task(
                self.entity_extractor.extract_entities(processed_text)
            )
            sentiment_task = asyncio.create_task(
                self.sentiment_analyzer.analyze_sentiment(processed_text)
            )
            
            # Wait for all tasks to complete
            intent, entities, sentiment = await asyncio.gather(
                intent_task, entities_task, sentiment_task
            )
            
            # Extract context features
            context_features = self._extract_context_features(processed_text, context)
            
            # Create result
            processing_time = time.time() - start_time
            result = NLUResult(
                input_text=text,
                processed_text=processed_text,
                intent=intent,
                entities=entities,
                sentiment=sentiment,
                context_features=context_features,
                processing_time=processing_time
            )
            
            # Update cache
            if len(self.cache) >= self.cache_max_size:
                # Remove oldest entry (simple FIFO)
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            
            self.cache[cache_key] = result
            
            # Update statistics
            self._update_processing_stats(processing_time)
            
            return result
            
        except Exception as e:
            self.processing_stats['error_count'] += 1
            self.logger.error(f"NLU processing failed: {e}")
            
            # Return fallback result
            return NLUResult(
                input_text=text,
                processed_text=text,
                intent=Intent(IntentCategory.UNKNOWN, 0.1),
                entities=[],
                sentiment=Sentiment(SentimentType.NEUTRAL, 0.5, 0.0, 0.5),
                processing_time=time.time() - start_time
            )
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess input text for better analysis."""
        # Basic preprocessing
        text = text.strip()
        
        # Expand contractions
        contractions = {
            "won't": "will not",
            "can't": "cannot",
            "n't": " not",
            "'re": " are",
            "'ve": " have",
            "'ll": " will",
            "'d": " would",
            "'m": " am"
        }
        
        for contraction, expansion in contractions.items():
            text = re.sub(contraction, expansion, text, flags=re.IGNORECASE)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _extract_context_features(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract contextual features from text and context."""
        features = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'has_question_mark': '?' in text,
            'has_exclamation': '!' in text,
            'is_uppercase': text.isupper(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add context information
        features.update(context)
        
        return features
    
    def _update_processing_stats(self, processing_time: float) -> None:
        """Update processing statistics."""
        self.processing_stats['total_requests'] += 1
        
        # Update rolling average
        total_requests = self.processing_stats['total_requests']
        current_avg = self.processing_stats['average_processing_time']
        
        self.processing_stats['average_processing_time'] = (
            (current_avg * (total_requests - 1) + processing_time) / total_requests
        )
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        stats = self.processing_stats.copy()
        stats.update(self.memory_manager.get_usage_stats())
        return stats
    
    def get_supported_intents(self) -> List[IntentCategory]:
        """Get list of supported intent categories."""
        if self.intent_classifier:
            return self.intent_classifier.get_supported_intents()
        return []
    
    async def cleanup(self) -> None:
        """Clean up resources and memory."""
        if RICH_AVAILABLE:
            console.print(info_panel("Cleaning up NLU Engine resources..."))
        
        # Clear cache
        self.cache.clear()
        
        # Deallocate memory
        self.memory_manager.deallocate("intent_classifier")
        self.memory_manager.deallocate("entity_extractor")
        self.memory_manager.deallocate("sentiment_analyzer")
        
        self.logger.info("NLU Engine cleanup completed")


# Example usage and testing
async def main():
    """Example usage of the NLU Engine."""
    if RICH_AVAILABLE:
        console.print(highlight_text("NLU Engine Demo", "bold blue"))
    
    # Initialize NLU Engine
    nlu = NLUEngine({
        'max_memory_mb': 20,
        'use_ml_intent': True,
        'cache_size': 50
    })
    
    if not await nlu.initialize():
        print("Failed to initialize NLU Engine")
        return
    
    # Test queries
    test_queries = [
        "Hello, how are you today?",
        "What's the weather like tomorrow?",
        "Create a reminder to call mom at 3 PM",
        "Search for information about machine learning",
        "I'm feeling really frustrated with this project",
        "Calculate 15 * 23 + 7",
        "Send an email to john.doe@example.com about the meeting"
    ]
    
    if RICH_AVAILABLE:
        console.print("\n[bold]Processing test queries:[/bold]")
    
    for query in test_queries:
        result = await nlu.process(query)
        
        if RICH_AVAILABLE:
            console.print(f"\n[blue]Query:[/blue] {query}")
            console.print(f"[green]Intent:[/green] {result.intent.category.name} "
                         f"(confidence: {result.intent.confidence:.2f})")
            console.print(f"[yellow]Entities:[/yellow] {len(result.entities)} found")
            for entity in result.entities:
                console.print(f"  - {entity.text} ({entity.entity_type.name})")
            console.print(f"[magenta]Sentiment:[/magenta] {result.sentiment.sentiment_type.name} "
                         f"(polarity: {result.sentiment.polarity:.2f})")
            console.print(f"[cyan]Processing time:[/cyan] {result.processing_time:.3f}s")
        else:
            print(f"\nQuery: {query}")
            print(f"Intent: {result.intent.category.name} (confidence: {result.intent.confidence:.2f})")
            print(f"Entities: {len(result.entities)} found")
            print(f"Sentiment: {result.sentiment.sentiment_type.name}")
            print(f"Processing time: {result.processing_time:.3f}s")
    
    # Show statistics
    stats = nlu.get_processing_stats()
    if RICH_AVAILABLE:
        console.print(f"\n[bold]Processing Statistics:[/bold]")
        console.print(f"Total requests: {stats['total_requests']}")
        console.print(f"Average processing time: {stats['average_processing_time']:.3f}s")
        console.print(f"Cache hits: {stats['cache_hits']}")
        console.print(f"Memory usage: {stats['current_usage_mb']:.1f}MB / {stats['max_memory_mb']:.1f}MB")
    
    # Cleanup
    await nlu.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
