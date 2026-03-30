"""
ImpressionCore User Experience (UX) Package
Core components for advanced user interface and experience features.

This package contains Phase 7B components:
- Interactive Dashboard: Real-time monitoring and control interface
- Generation Visualizer: Advanced visualization for processing states  
- Advanced Controls: Granular user controls for quality and performance
- Phase 7B Integration: Unified system combining all components

Created: 2025-05-30
Component: Priority 7 Phase 7B - Advanced Progressive Generation UI
"""

# Import main components for easier access
from .interactive_dashboard import InteractiveDashboard, DashboardMetrics
from .generation_visualizer import GenerationVisualizer, PipelineState, ProcessingStage
from .advanced_controls import AdvancedControls, QualitySpeedProfile, MemoryProfile
from .phase_7b_integration import Phase7BIntegration, UIConfiguration, UIMode

__version__ = "1.0.0"
__author__ = "ImpressionCore Development Team"

__all__ = [
    "InteractiveDashboard",
    "DashboardMetrics", 
    "GenerationVisualizer",
    "PipelineState",
    "ProcessingStage",
    "AdvancedControls",
    "QualitySpeedProfile",
    "MemoryProfile",
    "Phase7BIntegration",
    "UIConfiguration",
    "UIMode"
]
