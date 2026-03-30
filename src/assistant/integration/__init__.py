"""
Integration module for ImpressionCore Assistant

This module provides integration capabilities for task management, reminders,
calendar synchronization, productivity analytics, accessibility, and user experience.

Created: June 6, 2025
Updated: January 6, 2025 (Phase 8B Week 3 - Accessibility & UX)
"""

from .task_integration import TaskIntegrationManager, TaskIntegration
from .calendar_integration import CalendarIntegration, CalendarEvent, CalendarProvider
from .productivity_analytics import ProductivityAnalytics, ProductivityStats, AnalyticsTimeframe
from ..accessibility.accessibility_integration import AccessibilityIntegrationManager, AccessibilityIntegration
from .comprehensive_integration import AssistantIntegrationManager

__all__ = [
    'TaskIntegrationManager',
    'TaskIntegration', 
    'CalendarIntegration',
    'CalendarEvent',
    'CalendarProvider',
    'ProductivityAnalytics',
    'ProductivityStats',
    'AnalyticsTimeframe',
    'AccessibilityIntegrationManager',
    'AccessibilityIntegration',
    'AssistantIntegrationManager'
]
