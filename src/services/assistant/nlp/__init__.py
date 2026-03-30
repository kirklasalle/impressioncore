"""
Natural Language Processing Module for ImpressionCore Assistant

This module provides comprehensive NLP capabilities including natural language understanding,
intent recognition, entity extraction, and sentiment analysis. Optimized for GTX 1050 Ti
hardware constraints with memory-efficient processing.

Author: ImpressionCore Development Team
Created: 2025-01-18
Version: 1.0.0
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
"""

from .nlu_engine import (
    # Main NLU Engine
    NLUEngine,
    
    # Data structures
    Intent,
    Entity,
    Sentiment,
    NLUResult,
    
    # Enums
    IntentCategory,
    EntityType,
    SentimentType,
    
    # Components
    BaseIntentClassifier,
    RuleBasedIntentClassifier,
    MLIntentClassifier,
    EntityExtractor,
    SentimentAnalyzer,
    MemoryManager
)

__all__ = [
    # Main engine
    'NLUEngine',
    
    # Data structures
    'Intent',
    'Entity', 
    'Sentiment',
    'NLUResult',
    
    # Enums
    'IntentCategory',
    'EntityType',
    'SentimentType',
    
    # Components
    'BaseIntentClassifier',
    'RuleBasedIntentClassifier',
    'MLIntentClassifier',
    'EntityExtractor',
    'SentimentAnalyzer',
    'MemoryManager'
]

# Version information
__version__ = "1.0.0"
__author__ = "ImpressionCore Development Team"
__hardware_target__ = "NVIDIA GTX 1050 Ti (4GB VRAM)"
