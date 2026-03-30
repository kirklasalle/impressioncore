"""
Accessibility and User Experience Module for ImpressionCore Assistant
====================================================================

This module provides comprehensive accessibility support and user experience
enhancements for the ImpressionCore Personal Assistant, implementing Phase 8B
Week 3 accessibility and UX improvements.

Features:
- Accessibility Management (WCAG 2.1 AA compliance)
- User Experience Management (adaptive interfaces, personalization)
- Screen reader and assistive technology support
- Content transformation and adaptation
- User preference management
- Analytics and feedback systems

Author: ImpressionCore Development Team
Created: 2025-01-06 (Phase 8B Week 3)
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
Memory Budget: Optimized for resource-constrained environments
"""

from .accessibility_manager import (
    AccessibilityManager,
    AccessibilityProfile,
    AccessibilityLevel,
    MotorAbility,
    VisualAbility,
    AuditoryAbility,
    CognitiveAbility
)
from .user_experience_manager import (
    UserExperienceManager,
    UserPreferences,
    InteractionPattern,
    ExperienceLevel,
    InterfaceTheme,
    NotificationStyle,
    UsageAnalytics
)
from .accessibility_integration import (
    AccessibilityIntegrationManager,
    AccessibilityIntegration
)

__version__ = "8B.3.0"
__phase__ = "8B Week 3 - Accessibility & UX Enhancements"

__all__ = [
    # Accessibility Management
    'AccessibilityManager',
    'UserAccessibilityProfile',
    'AccessibilityLevel',
    'AccessibilityFeature',
    'ContentTransformation',
    
    # User Experience Management
    'UserExperienceManager',
    'UserPersonalizationProfile',
    'UserInterfaceMode',
    'UserPreference',
    'UserAnalytics',
    
    # Integration Components
    'AccessibilityIntegrationManager',
    'AccessibilityIntegration'
]

# Default accessibility and UX configuration
DEFAULT_ACCESSIBILITY_CONFIG = {
    'screen_reader_support': True,
    'high_contrast_mode': False,
    'large_text_mode': False,
    'keyboard_navigation': True,
    'audio_descriptions': False,
    'reduced_motion': False,
    'simplified_ui': False
}

DEFAULT_UX_CONFIG = {
    'interface_mode': 'adaptive',
    'theme_preference': 'system',
    'response_style': 'balanced',
    'interaction_style': 'conversational',
    'personalization_level': 'medium',
    'analytics_enabled': True,
    'feedback_collection': True
}
