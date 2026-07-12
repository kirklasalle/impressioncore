"""
Response Generator for Phase 8B Personal Assistant

This module provides comprehensive response generation capabilities including contextual
response generation, multi-modal output handling, and template-based responses.
Optimized for GTX 1050 Ti hardware constraints with memory-efficient processing.

Author: ImpressionCore Development Team
Created: 2025-01-18
Version: 1.0.0
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
Memory Budget: 30MB maximum allocation
"""

import asyncio
import json
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

# Core ML imports with memory optimization
try:
    import torch
    import numpy as np
    from transformers import (
        AutoTokenizer, AutoModelForCausalLM, 
        pipeline, set_seed
    )
    import nltk
    from sentence_transformers import SentenceTransformer
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

# Import assistant types
try:
    from .context_manager import ContextManager, ContextItem, ContextType
    from ..nlp.nlu_engine import NLUResult, Intent, IntentCategory
    ASSISTANT_TYPES_AVAILABLE = True
except ImportError:
    ASSISTANT_TYPES_AVAILABLE = False


class ResponseType(Enum):
    """Types of responses that can be generated."""
    
    TEXT = auto()           # Plain text response
    STRUCTURED = auto()     # JSON/structured data response
    MULTIMODAL = auto()     # Text + images/audio/video
    INTERACTIVE = auto()    # Interactive elements (buttons, forms)
    STREAMING = auto()      # Streaming/progressive response
    ERROR = auto()          # Error response
    CONFIRMATION = auto()   # Confirmation/question response


class ResponseStyle(Enum):
    """Response style and tone options."""
    
    FORMAL = auto()         # Professional, formal tone
    CASUAL = auto()         # Friendly, conversational tone
    CONCISE = auto()        # Brief, to-the-point
    DETAILED = auto()       # Comprehensive, explanatory
    EMPATHETIC = auto()     # Understanding, supportive
    ENTHUSIASTIC = auto()   # Excited, energetic
    TECHNICAL = auto()      # Technical, precise
    HELPFUL = auto()        # Helpful, assistive tone


class ResponsePriority(Enum):
    """Response generation priority levels."""
    
    CRITICAL = auto()       # Emergency/critical responses
    HIGH = auto()           # Important responses
    NORMAL = auto()         # Standard responses
    LOW = auto()            # Background/supplementary responses


@dataclass
class ResponseContext:
    """Context information for response generation."""
    
    user_input: str
    nlu_result: Optional[Any] = None  # NLUResult if available
    conversation_history: List[Any] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    session_context: Dict[str, Any] = field(default_factory=dict)
    system_state: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResponseTemplate:
    """Template for generating responses."""
    
    template_id: str
    intent_category: IntentCategory
    template_text: str
    response_type: ResponseType
    response_style: ResponseStyle
    variables: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    priority: ResponsePriority = ResponsePriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedResponse:
    """A generated response with metadata."""
    
    content: str
    response_type: ResponseType
    response_style: ResponseStyle
    confidence: float
    template_used: Optional[str] = None
    context_items_used: List[str] = field(default_factory=list)
    generation_method: str = "unknown"
    generation_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate response data."""
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")


class MemoryManager:
    """Memory management for response generation."""
    
    def __init__(self, max_memory_mb: int = 30):
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
        else:
            # Rough estimate for other objects
            return len(str(obj).encode('utf-8'))
    
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


class BaseResponseGenerator(ABC):
    """Abstract base class for response generators."""
    
    @abstractmethod
    async def generate_response(self, context: ResponseContext) -> GeneratedResponse:
        """Generate a response based on context."""
        pass
    
    @abstractmethod
    def get_supported_intents(self) -> List[IntentCategory]:
        """Get list of supported intent categories."""
        pass


class TemplateResponseGenerator(BaseResponseGenerator):
    """Template-based response generator for fast, reliable responses."""
    
    def __init__(self):
        """Initialize template-based generator."""
        self.templates = self._build_response_templates()
        self.logger = logging.getLogger(__name__)
    
    def _build_response_templates(self) -> Dict[IntentCategory, List[ResponseTemplate]]:
        """Build response templates for different intents."""
        templates = {
            IntentCategory.GREETING: [
                ResponseTemplate(
                    template_id="greeting_basic",
                    intent_category=IntentCategory.GREETING,
                    template_text="Hello! How can I help you today?",
                    response_type=ResponseType.TEXT,
                    response_style=ResponseStyle.CASUAL
                ),
                ResponseTemplate(
                    template_id="greeting_personalized",
                    intent_category=IntentCategory.GREETING,
                    template_text="Hello {user_name}! How can I assist you today?",
                    response_type=ResponseType.TEXT,
                    response_style=ResponseStyle.CASUAL,
                    variables=["user_name"],
                    conditions={"has_user_name": True}
                )
            ],
            IntentCategory.FAREWELL: [
                ResponseTemplate(
                    template_id="farewell_basic",
                    intent_category=IntentCategory.FAREWELL,
                    template_text="Goodbye! Have a great day!",
                    response_type=ResponseType.TEXT,
                    response_style=ResponseStyle.CASUAL
                ),
                ResponseTemplate(
                    template_id="farewell_personalized",
                    intent_category=IntentCategory.FAREWELL,
                    template_text="Goodbye {user_name}! Take care and have a wonderful day!",
                    response_type=ResponseType.TEXT,
                    response_style=ResponseStyle.CASUAL,
                    variables=["user_name"],
                    conditions={"has_user_name": True}
                )
            ],
            IntentCategory.QUESTION: [
                ResponseTemplate(
                    template_id="question_research",
                    intent_category=IntentCategory.QUESTION,
                    template_text="Let me search for information about that. I'll look into {topic} and get back to you with what I find.",
                    response_type=ResponseType.TEXT,
                    response_style=ResponseStyle.HELPFUL,
                    variables=["topic"]
                ),
                ResponseTemplate(
                    template_id="question_clarification",
                    intent_category=IntentCategory.QUESTION,
                    template_text="I'd be happy to help with that question. Could you provide a bit more detail about what specifically you'd like to know?",
                    response_type=ResponseType.CONFIRMATION,
                    response_style=ResponseStyle.HELPFUL
                )
            ],
            IntentCategory.TASK_CREATE: [
                ResponseTemplate(
                    template_id="task_create_confirm",
                    intent_category=IntentCategory.TASK_CREATE,
                    template_text="I'll create that task for you: '{task_description}'. When would you like to be reminded?",
                    response_type=ResponseType.CONFIRMATION,
                    response_style=ResponseStyle.HELPFUL,
                    variables=["task_description"]
                ),
                ResponseTemplate(
                    template_id="task_create_success",
                    intent_category=IntentCategory.TASK_CREATE,
                    template_text="Task created successfully! I've added '{task_description}' to your list with a reminder for {reminder_time}.",
                    response_type=ResponseType.TEXT,
                    response_style=ResponseStyle.ENTHUSIASTIC,
                    variables=["task_description", "reminder_time"]
                )
            ],
            IntentCategory.SEARCH: [
                ResponseTemplate(
                    template_id="search_initiate",
                    intent_category=IntentCategory.SEARCH,
                    template_text="I'll search for '{search_query}' for you. Let me find the most relevant information.",
                    response_type=ResponseType.TEXT,
                    response_style=ResponseStyle.HELPFUL,
                    variables=["search_query"]
                ),
                ResponseTemplate(
                    template_id="search_results",
                    intent_category=IntentCategory.SEARCH,
                    template_text="I found {result_count} results for '{search_query}'. Here are the most relevant ones:\n\n{search_results}",
                    response_type=ResponseType.STRUCTURED,
                    response_style=ResponseStyle.DETAILED,
                    variables=["search_query", "result_count", "search_results"]
                )
            ],
            IntentCategory.WEATHER: [
                ResponseTemplate(
                    template_id="weather_current",
                    intent_category=IntentCategory.WEATHER,
                    template_text="The current weather in {location} is {condition} with a temperature of {temperature}°F. {additional_info}",
                    response_type=ResponseType.TEXT,
                    response_style=ResponseStyle.CONCISE,
                    variables=["location", "condition", "temperature", "additional_info"]
                ),
                ResponseTemplate(
                    template_id="weather_forecast",
                    intent_category=IntentCategory.WEATHER,
                    template_text="Here's the weather forecast for {location}:\n\n{forecast_details}",
                    response_type=ResponseType.STRUCTURED,
                    response_style=ResponseStyle.DETAILED,
                    variables=["location", "forecast_details"]
                )
            ],
            IntentCategory.HELP: [
                ResponseTemplate(
                    template_id="help_general",
                    intent_category=IntentCategory.HELP,
                    template_text="I'm here to help! I can assist you with:\n\n• Answering questions and finding information\n• Creating tasks and reminders\n• Checking weather and news\n• Managing your schedule\n• And much more!\n\nWhat would you like help with?",
                    response_type=ResponseType.STRUCTURED,
                    response_style=ResponseStyle.HELPFUL
                ),
                ResponseTemplate(
                    template_id="help_specific",
                    intent_category=IntentCategory.HELP,
                    template_text="I can help you with {help_topic}. Here's what you can do:\n\n{help_instructions}",
                    response_type=ResponseType.STRUCTURED,
                    response_style=ResponseStyle.DETAILED,
                    variables=["help_topic", "help_instructions"]
                )
            ],
            IntentCategory.UNKNOWN: [
                ResponseTemplate(
                    template_id="unknown_clarify",
                    intent_category=IntentCategory.UNKNOWN,
                    template_text="I'm not sure I understood that completely. Could you rephrase or provide more details about what you'd like me to help with?",
                    response_type=ResponseType.CONFIRMATION,
                    response_style=ResponseStyle.EMPATHETIC
                ),
                ResponseTemplate(
                    template_id="unknown_suggest",
                    intent_category=IntentCategory.UNKNOWN,
                    template_text="I'm not sure about that, but I can help you with questions, tasks, weather, searches, and more. What would you like to try?",
                    response_type=ResponseType.TEXT,
                    response_style=ResponseStyle.HELPFUL
                )
            ]
        }
        
        return templates
    
    async def generate_response(self, context: ResponseContext) -> GeneratedResponse:
        """Generate response using templates."""
        start_time = time.time()
        
        # Get intent from NLU result
        intent_category = IntentCategory.UNKNOWN
        if context.nlu_result and hasattr(context.nlu_result, 'intent'):
            intent_category = context.nlu_result.intent.category
        
        # Find appropriate template
        template = await self._select_template(intent_category, context)
        if not template:
            # Fallback to unknown intent
            template = self.templates[IntentCategory.UNKNOWN][0]
        
        # Generate response from template
        response_content = await self._fill_template(template, context)
        
        # Create response object
        generation_time = time.time() - start_time
        return GeneratedResponse(
            content=response_content,
            response_type=template.response_type,
            response_style=template.response_style,
            confidence=0.8,  # High confidence for template-based responses
            template_used=template.template_id,
            generation_method="template",
            generation_time=generation_time,
            metadata={
                "intent_category": intent_category.name,
                "template_variables": template.variables
            }
        )
    
    async def _select_template(self, intent: IntentCategory, context: ResponseContext) -> Optional[ResponseTemplate]:
        """Select the best template for the given intent and context."""
        if intent not in self.templates:
            return None
        
        candidate_templates = self.templates[intent]
        
        # Check conditions and select best template
        for template in candidate_templates:
            if await self._check_template_conditions(template, context):
                return template
        
        # Return first template as fallback
        return candidate_templates[0] if candidate_templates else None
    
    async def _check_template_conditions(self, template: ResponseTemplate, context: ResponseContext) -> bool:
        """Check if template conditions are met."""
        if not template.conditions:
            return True
        
        for condition, expected_value in template.conditions.items():
            if condition == "has_user_name":
                has_user_name = bool(context.user_preferences.get('user_name') or 
                                   context.session_context.get('user_name'))
                if has_user_name != expected_value:
                    return False
            # Add more condition checks as needed
        
        return True
    
    async def _fill_template(self, template: ResponseTemplate, context: ResponseContext) -> str:
        """Fill template with context variables."""
        response_text = template.template_text
        
        # Extract variables from context
        variables = await self._extract_template_variables(template, context)
        
        # Replace variables in template
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            response_text = response_text.replace(placeholder, str(var_value))
        
        return response_text
    
    async def _extract_template_variables(self, template: ResponseTemplate, context: ResponseContext) -> Dict[str, str]:
        """Extract variables for template filling."""
        variables = {}
        
        for var_name in template.variables:
            # Check different sources for variables
            var_value = None
            
            # User preferences
            if var_name == "user_name":
                var_value = (context.user_preferences.get('user_name') or 
                           context.session_context.get('user_name') or 
                           "there")
            
            # Extract from user input or entities
            elif var_name in ["topic", "search_query", "task_description"]:
                var_value = context.user_input
                
                # Try to extract from entities if available
                if context.nlu_result and hasattr(context.nlu_result, 'entities'):
                    for entity in context.nlu_result.entities:
                        if hasattr(entity, 'text'):
                            var_value = entity.text
                            break
            
            # Default values for missing variables
            elif var_name == "location":
                var_value = context.user_preferences.get('location', 'your area')
            elif var_name == "reminder_time":
                var_value = "the specified time"
            elif var_name == "result_count":
                var_value = "several"
            
            variables[var_name] = var_value or f"[{var_name}]"
        
        return variables
    
    async def generate_response_from_context(self, context: ResponseContext) -> GeneratedResponse:
        """Generate a response from ResponseContext.
        
        This is a convenience method that unpacks ResponseContext and calls the main generate_response method.
        
        Args:
            context: ResponseContext containing all necessary information
            
        Returns:
            Generated response
        """
        return await self.generate_response(
            user_input=context.user_input,
            nlu_result=context.nlu_result,
            conversation_history=context.conversation_history,
            # Pass the context manager if available in metadata or session_context
            context_manager=context.metadata.get('context_manager') or context.session_context.get('context_manager')
        )

    def get_supported_intents(self) -> List[IntentCategory]:
        """Get list of supported intent categories."""
        return list(self.templates.keys())


class MLResponseGenerator(BaseResponseGenerator):
    """ML-based response generator using transformers."""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-small"):
        """Initialize ML generator."""
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize ML models."""
        if not ML_AVAILABLE:
            self.logger.warning("ML dependencies not available, using fallback")
            return False
        
        try:
            # Use a lightweight text generation model
            self.pipeline = pipeline(
                "text-generation",
                model="gpt2",  # Small model for memory efficiency
                tokenizer="gpt2",
                device=-1,  # CPU only for GTX 1050 Ti compatibility
                max_length=150,
                do_sample=True,
                temperature=0.7
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize ML generator: {e}")
            return False
    
    async def generate_response(self, context: ResponseContext) -> GeneratedResponse:
        """Generate response using ML models."""
        start_time = time.time()
        
        if not self.pipeline:
            # Fallback to template-based
            fallback = TemplateResponseGenerator()
            return await fallback.generate_response(context)
        
        try:
            # Prepare input for generation
            prompt = await self._prepare_prompt(context)
            
            # Generate response
            generated = self.pipeline(prompt, max_length=len(prompt.split()) + 50, num_return_sequences=1)
            response_text = generated[0]['generated_text']
            
            # Extract only the new part (after the prompt)
            response_text = response_text[len(prompt):].strip()
            
            # Clean up the response
            response_text = await self._clean_response(response_text)
            
            generation_time = time.time() - start_time
            return GeneratedResponse(
                content=response_text,
                response_type=ResponseType.TEXT,
                response_style=ResponseStyle.CASUAL,
                confidence=0.6,  # Lower confidence for ML generation
                generation_method="ml_transformer",
                generation_time=generation_time,
                metadata={
                    "model_name": self.model_name,
                    "prompt_length": len(prompt)
                }
            )
            
        except Exception as e:
            self.logger.error(f"ML response generation failed: {e}")
            # Fallback to template-based
            fallback = TemplateResponseGenerator()
            return await fallback.generate_response(context)
    
    async def _prepare_prompt(self, context: ResponseContext) -> str:
        """Prepare prompt for text generation."""
        prompt_parts = []
        
        # Add conversation history for context
        if context.conversation_history:
            for turn in context.conversation_history[-3:]:  # Last 3 turns
                if hasattr(turn, 'user_input') and hasattr(turn, 'assistant_response'):
                    prompt_parts.append(f"User: {turn.user_input}")
                    prompt_parts.append(f"Assistant: {turn.assistant_response}")
        
        # Add current user input
        prompt_parts.append(f"User: {context.user_input}")
        prompt_parts.append("Assistant:")
        
        return "\n".join(prompt_parts)
    
    async def _clean_response(self, response: str) -> str:
        """Clean up generated response."""
        # Remove common artifacts
        response = re.sub(r'\n+', ' ', response)  # Replace newlines with spaces
        response = re.sub(r'\s+', ' ', response)  # Normalize whitespace
        response = response.strip()
        
        # Limit length
        if len(response) > 200:
            response = response[:200].rsplit(' ', 1)[0] + "..."
        
        # Ensure response doesn't start with "User:" or "Assistant:"
        response = re.sub(r'^(User:|Assistant:)\s*', '', response, flags=re.IGNORECASE)
        
        return response
    
    def get_supported_intents(self) -> List[IntentCategory]:
        """Get list of supported intent categories."""
        # ML generator can handle any intent
        return list(IntentCategory)


class ResponseGenerator:
    """Main response generation system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Response Generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.memory_manager = MemoryManager(
            max_memory_mb=self.config.get('max_memory_mb', 30)
        )
        
        # Response generators
        self.template_generator = None
        self.ml_generator = None
        
        # Response cache for frequently used responses
        self.response_cache = {}
        self.cache_max_size = self.config.get('cache_size', 50)
        
        # Performance tracking
        self.stats = {
            'total_responses': 0,
            'template_responses': 0,
            'ml_responses': 0,
            'cached_responses': 0,
            'average_generation_time': 0.0,
            'error_count': 0
        }
        
        self.logger = logging.getLogger(__name__)
        
        if RICH_AVAILABLE:
            self.status_animation = StatusAnimation()
    
    async def initialize(self) -> bool:
        """Initialize response generation system."""
        if RICH_AVAILABLE:
            console.print(info_panel("Initializing Response Generator..."))
            await self.status_animation.start("Loading response generators")
        
        try:
            # Allocate memory for components
            if not self.memory_manager.allocate("template_generator", 10 * 1024 * 1024):  # 10MB
                raise RuntimeError("Failed to allocate memory for template generator")
            
            if not self.memory_manager.allocate("ml_generator", 15 * 1024 * 1024):  # 15MB
                raise RuntimeError("Failed to allocate memory for ML generator")
            
            if not self.memory_manager.allocate("response_cache", 5 * 1024 * 1024):  # 5MB
                raise RuntimeError("Failed to allocate memory for response cache")
              # Initialize generators
            self.template_generator = TemplateResponseGenerator()
            
            if self.config.get('use_ml_generation', True) and ML_AVAILABLE:
                self.ml_generator = MLResponseGenerator()
                await self.ml_generator.initialize()
            
            if RICH_AVAILABLE:
                await self.status_animation.stop()
                console.print(success_panel("Response Generator initialized successfully"))
            
            self.logger.info("Response Generator initialization completed")
            return True
            
        except Exception as e:
            if RICH_AVAILABLE:
                await self.status_animation.stop()
                console.print(error_panel(f"Response Generator initialization failed: {str(e)}"))
            
            self.logger.error(f"Response Generator initialization failed: {e}")
            return False
    
    async def generate_response_from_context(self, context: ResponseContext) -> GeneratedResponse:
        """Generate a response from ResponseContext.
        
        This is a convenience method that unpacks ResponseContext and calls the main generate_response method.
        
        Args:
            context: ResponseContext containing all necessary information
            
        Returns:
            Generated response
        """
        return await self.generate_response(
            user_input=context.user_input,
            nlu_result=context.nlu_result,
            conversation_history=context.conversation_history,
            # Pass the context manager if available in metadata or session_context
            context_manager=context.metadata.get('context_manager') or context.session_context.get('context_manager')
        )

    async def generate_response(self, 
                              user_input_or_context,
                              nlu_result: Optional[Any] = None,
                              conversation_history: Optional[List[Any]] = None,
                              context_manager: Optional[Any] = None) -> GeneratedResponse:
        """Generate a response based on input and context.
        
        Args:
            user_input_or_context: Either a string (user input) or ResponseContext object
            nlu_result: NLU analysis result (used when first arg is string)
            conversation_history: Recent conversation turns (used when first arg is string)
            context_manager: Context manager instance (used when first arg is string)
            
        Returns:
            Generated response
        """
        # Handle both ResponseContext and individual parameters
        if isinstance(user_input_or_context, ResponseContext):
            # Extract parameters from ResponseContext
            user_input = user_input_or_context.user_input
            nlu_result = user_input_or_context.nlu_result
            conversation_history = user_input_or_context.conversation_history
            context_manager = user_input_or_context.metadata.get('context_manager') or user_input_or_context.session_context.get('context_manager')
        else:
            # Use parameters directly
            user_input = user_input_or_context
        
        start_time = time.time()
        
        # Check cache first
        cache_key = self._generate_cache_key(user_input, nlu_result)
        if cache_key in self.response_cache:
            self.stats['cached_responses'] += 1
            cached_response = self.response_cache[cache_key]
            cached_response.metadata['from_cache'] = True
            return cached_response
        
        try:
            # Prepare response context
            response_context = await self._prepare_response_context(
                user_input, nlu_result, conversation_history, context_manager
            )
            
            # Select appropriate generator
            generator = await self._select_generator(response_context)
            
            # Generate response
            response = await generator.generate_response(response_context)
            
            # Post-process response
            response = await self._post_process_response(response, response_context)
            
            # Update cache
            await self._update_cache(cache_key, response)
            
            # Update statistics
            generation_time = time.time() - start_time
            self._update_stats(response, generation_time)
            
            return response
            
        except Exception as e:
            self.stats['error_count'] += 1
            self.logger.error(f"Response generation failed: {e}")
            
            # Return fallback response
            return GeneratedResponse(
                content="I apologize, but I'm having trouble generating a response right now. Could you please try rephrasing your request?",
                response_type=ResponseType.ERROR,
                response_style=ResponseStyle.EMPATHETIC,
                confidence=0.5,
                generation_method="fallback",
                generation_time=time.time() - start_time
            )
    
    async def _prepare_response_context(self,
                                      user_input: str,
                                      nlu_result: Optional[Any],
                                      conversation_history: Optional[List[Any]],
                                      context_manager: Optional[Any]) -> ResponseContext:
        """Prepare context for response generation."""
        
        # Get user preferences and session context from context manager
        user_preferences = {}
        session_context = {}
        
        if context_manager:
            # Get user profile context
            user_context = await context_manager.get_context(
                context_type=ContextType.USER_PROFILE,
                limit=5
            )
            
            for item in user_context:
                if hasattr(item, 'content') and isinstance(item.content, dict):
                    user_preferences.update(item.content)
            
            # Get session context
            session_context_items = await context_manager.get_context(
                context_type=ContextType.SESSION,
                limit=1
            )
            
            if session_context_items:
                session_context = session_context_items[0].content
        
        return ResponseContext(
            user_input=user_input,
            nlu_result=nlu_result,
            conversation_history=conversation_history or [],
            user_preferences=user_preferences,
            session_context=session_context,
            system_state=self.config.get('system_state', {}),
            metadata={'timestamp': datetime.now().isoformat()}
        )
    
    async def _select_generator(self, context: ResponseContext) -> BaseResponseGenerator:
        """Select the appropriate response generator."""
        
        # Use ML generator for complex or conversational intents
        if (self.ml_generator and 
            context.nlu_result and 
            hasattr(context.nlu_result, 'intent')):
            
            complex_intents = [
                IntentCategory.CONVERSATION,
                IntentCategory.QUESTION,
                IntentCategory.EXPLANATION
            ]
            
            if context.nlu_result.intent.category in complex_intents:
                return self.ml_generator
        
        # Default to template generator for reliability
        return self.template_generator
    
    async def _post_process_response(self, response: GeneratedResponse, context: ResponseContext) -> GeneratedResponse:
        """Post-process the generated response."""
        
        # Apply user preferences for response style
        if context.user_preferences.get('response_style') == 'formal':
            response.content = await self._make_formal(response.content)
        elif context.user_preferences.get('response_style') == 'casual':
            response.content = await self._make_casual(response.content)
        
        # Add personalization if user name is available
        user_name = context.user_preferences.get('user_name')
        if user_name and response.response_type != ResponseType.ERROR:
            # Optionally add user name to response
            pass
        
        # Ensure appropriate length
        max_length = context.user_preferences.get('max_response_length', 500)
        if len(response.content) > max_length:
            response.content = response.content[:max_length-3] + "..."
        
        return response
    
    async def _make_formal(self, text: str) -> str:
        """Make text more formal."""
        # Simple transformations to make text more formal
        replacements = {
            "hey": "hello",
            "hi": "hello",
            "gonna": "going to",
            "wanna": "want to",
            "can't": "cannot",
            "won't": "will not",
            "!": "."
        }
        
        for informal, formal in replacements.items():
            text = re.sub(r'\b' + re.escape(informal) + r'\b', formal, text, flags=re.IGNORECASE)
        
        return text
    
    async def _make_casual(self, text: str) -> str:
        """Make text more casual."""
        # Simple transformations to make text more casual
        if not text.endswith(('!', '?')):
            text = text.rstrip('.') + '!'
        
        return text
    
    def _generate_cache_key(self, user_input: str, nlu_result: Optional[Any]) -> str:
        """Generate cache key for response."""
        intent_name = "unknown"
        if nlu_result and hasattr(nlu_result, 'intent'):
            intent_name = nlu_result.intent.category.name
        
        # Simple hash-based key
        return f"{intent_name}:{hash(user_input.lower())}"
    
    async def _update_cache(self, cache_key: str, response: GeneratedResponse) -> None:
        """Update response cache."""
        # Remove oldest entries if cache is full
        if len(self.response_cache) >= self.cache_max_size:
            oldest_key = next(iter(self.response_cache))
            del self.response_cache[oldest_key]
        
        # Add new response to cache
        self.response_cache[cache_key] = response
    
    def _update_stats(self, response: GeneratedResponse, generation_time: float) -> None:
        """Update generation statistics."""
        self.stats['total_responses'] += 1
        
        if response.generation_method == "template":
            self.stats['template_responses'] += 1
        elif response.generation_method.startswith("ml"):
            self.stats['ml_responses'] += 1
        
        # Update rolling average
        total_responses = self.stats['total_responses']
        current_avg = self.stats['average_generation_time']
        
        self.stats['average_generation_time'] = (
            (current_avg * (total_responses - 1) + generation_time) / total_responses
        )
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        stats = self.stats.copy()
        stats.update(self.memory_manager.get_usage_stats())
        return stats
    
    async def cleanup(self) -> None:
        """Clean up resources and memory."""
        if RICH_AVAILABLE:
            console.print(info_panel("Cleaning up Response Generator resources..."))
        
        # Clear cache
        self.response_cache.clear()
        
        # Deallocate memory
        self.memory_manager.deallocate("template_generator")
        self.memory_manager.deallocate("ml_generator")
        self.memory_manager.deallocate("response_cache")
        
        self.logger.info("Response Generator cleanup completed")


# Example usage and testing
async def main():
    """Example usage of the Response Generator."""
    if RICH_AVAILABLE:
        console.print(highlight_text("Response Generator Demo", "bold blue"))
    
    # Initialize Response Generator
    response_generator = ResponseGenerator({
        'max_memory_mb': 30,
        'use_ml_generation': True,
        'cache_size': 25,
        'user_preferences': {
            'user_name': 'Alice',
            'response_style': 'casual',
            'max_response_length': 200
        }
    })
    
    if not await response_generator.initialize():
        print("Failed to initialize Response Generator")
        return
    
    # Test response generation
    test_inputs = [
        ("Hello there!", "greeting"),
        ("What's the weather like?", "weather"),
        ("Create a reminder to call mom", "task_create"),
        ("Search for machine learning tutorials", "search"),
        ("I need help with this project", "help"),
        ("Goodbye!", "farewell")
    ]
    
    if RICH_AVAILABLE:
        console.print("\n[bold]Generating responses:[/bold]")
    
    for user_input, intent_name in test_inputs:
        # Create mock NLU result
        class MockIntent:
            def __init__(self, name):
                self.category = getattr(IntentCategory, name.upper(), IntentCategory.UNKNOWN)
        
        class MockNLUResult:
            def __init__(self, intent_name):
                self.intent = MockIntent(intent_name)
                self.entities = []
        
        nlu_result = MockNLUResult(intent_name)
        
        # Generate response
        response = await response_generator.generate_response(user_input, nlu_result)
        
        if RICH_AVAILABLE:
            console.print(f"\n[blue]Input:[/blue] {user_input}")
            console.print(f"[green]Response:[/green] {response.content}")
            console.print(f"[yellow]Method:[/yellow] {response.generation_method}")
            console.print(f"[cyan]Confidence:[/cyan] {response.confidence:.2f}")
            console.print(f"[magenta]Time:[/magenta] {response.generation_time:.3f}s")
        else:
            print(f"\nInput: {user_input}")
            print(f"Response: {response.content}")
            print(f"Method: {response.generation_method}")
            print(f"Confidence: {response.confidence:.2f}")
            print(f"Time: {response.generation_time:.3f}s")
    
    # Show statistics
    stats = response_generator.get_processing_stats()
    if RICH_AVAILABLE:
        console.print(f"\n[bold]Generation Statistics:[/bold]")
        console.print(f"Total responses: {stats['total_responses']}")
        console.print(f"Template responses: {stats['template_responses']}")
        console.print(f"ML responses: {stats['ml_responses']}")
        console.print(f"Cached responses: {stats['cached_responses']}")
        console.print(f"Average generation time: {stats['average_generation_time']:.3f}s")
        console.print(f"Memory usage: {stats['current_usage_mb']:.1f}MB")
    
    # Cleanup
    await response_generator.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
