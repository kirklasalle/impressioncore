"""
ImpressionCore UX API - Production Integration
Phase 7D: Production Integration and Optimization

This module provides RESTful API endpoints for all user experience features,
integrating Phase 7A-7C components into a production-ready system.

Author: GitHub Copilot & Kirk LaSalle
Date: June 1, 2025
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
import asyncio
import json
import logging
from datetime import datetime, timedelta
import uuid
from dataclasses import dataclass

# Import UX components from previous phases
try:
    from ...core.ux.hardware_detector import AdvancedHardwareDetector
    from ...core.ux.user_profiles import IntelligentUserProfiles
    from ...core.ux.config_optimizer import ConfigurationOptimizer
    from ...core.ux.interactive_dashboard import InteractiveControlDashboard
    from ...core.ux.generation_visualizer import ProgressiveGenerationVisualizer
    from ...core.ux.advanced_controls import AdvancedUserControls
    from ...core.ux.ml_adaptation import MLAdaptationEngine
    from ...core.ux.feedback_system import ComprehensiveFeedbackSystem
    from ...core.ux.predictive_optimizer import PredictiveOptimizationEngine
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"UX components not fully available: {e}")
    COMPONENTS_AVAILABLE = False

# Rich console enhancements
try:
    from ...core.utils.rich_enhancements import get_console, create_status
    from ...core.utils.rich_logging import setup_logger
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    import logging
    logging.basicConfig(level=logging.INFO)

# Setup logging
if RICH_AVAILABLE:
    logger = setup_logger("ux_api", level="INFO")
else:
    logger = logging.getLogger("ux_api")

# Initialize router
router = APIRouter(prefix="/api/ux", tags=["user-experience"])

# Pydantic models for API requests/responses
class SessionCreateRequest(BaseModel):
    """Request model for creating a new user session."""
    user_id: Optional[str] = Field(None, description="User identifier")
    session_name: Optional[str] = Field(None, description="Session name")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    hardware_config: Optional[Dict[str, Any]] = Field(default_factory=dict)

class SessionResponse(BaseModel):
    """Response model for session operations."""
    session_id: str
    user_id: Optional[str]
    status: str
    created_at: datetime
    last_activity: datetime
    configuration: Dict[str, Any]
    performance_metrics: Dict[str, Any]

class ConfigurationRequest(BaseModel):
    """Request model for configuration updates."""
    hardware_settings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    user_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    optimization_goals: Optional[List[str]] = Field(default_factory=list)

class FeedbackRequest(BaseModel):
    """Request model for feedback submission."""
    session_id: str
    feedback_type: str = Field(..., pattern="^(explicit|implicit|performance)$")
    content: Union[str, Dict[str, Any]]
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    category: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class AnalyticsResponse(BaseModel):
    """Response model for analytics dashboard."""
    session_analytics: Dict[str, Any]
    user_analytics: Dict[str, Any]
    performance_trends: Dict[str, Any]
    optimization_recommendations: List[Dict[str, Any]]

@dataclass
class UXSession:
    """Session data class for managing user sessions."""
    session_id: str
    user_id: Optional[str]
    created_at: datetime
    last_activity: datetime
    status: str
    configuration: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    websocket: Optional[WebSocket] = None

class UXAPIManager:
    """
    Main manager class for UX API operations.
    Coordinates all Phase 7A-7C components for production use.
    """
    
    def __init__(self):
        """Initialize the UX API manager with all components."""
        self.sessions: Dict[str, UXSession] = {}
        self.websockets: Dict[str, WebSocket] = {}
        
        # Initialize components if available
        if COMPONENTS_AVAILABLE:
            try:
                self.hardware_detector = AdvancedHardwareDetector()
                self.user_profiles = IntelligentUserProfiles()
                self.config_optimizer = ConfigurationOptimizer()
                self.dashboard = InteractiveControlDashboard()
                self.visualizer = ProgressiveGenerationVisualizer()
                self.controls = AdvancedUserControls()
                self.ml_adaptation = MLAdaptationEngine()
                self.feedback_system = ComprehensiveFeedbackSystem()
                self.predictive_optimizer = PredictiveOptimizationEngine()
                
                logger.info("UX API Manager initialized with all components")
            except Exception as e:
                logger.error(f"Failed to initialize UX components: {e}")
                self.components_available = False
        else:
            self.components_available = False
            logger.warning("UX components not available, API will run in limited mode")
    
    async def create_session(self, request: SessionCreateRequest) -> UXSession:
        """Create a new user session with full UX integration."""
        session_id = str(uuid.uuid4())
        
        # Generate user ID if not provided
        user_id = request.user_id or f"user_{session_id[:8]}"
        
        # Detect hardware capabilities
        if hasattr(self, 'hardware_detector'):
            hardware_info = self.hardware_detector.detect_hardware()
            performance_tier = self.hardware_detector.classify_performance_tier()
        else:
            hardware_info = {"status": "detection_unavailable"}
            performance_tier = "unknown"
        
        # Load or create user profile
        if hasattr(self, 'user_profiles'):
            profile = self.user_profiles.get_or_create_profile(user_id)
            profile.update(request.preferences)
        else:
            profile = request.preferences
        
        # Optimize configuration
        if hasattr(self, 'config_optimizer'):
            optimal_config = self.config_optimizer.optimize_configuration(
                hardware_info,
                profile,
                goals=["performance", "quality", "memory_efficiency"]
            )
        else:
            optimal_config = {
                "precision": "mixed_fp16",
                "batch_size": 1,
                "context_length": 32768
            }
        
        # Initialize session
        session = UXSession(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            status="active",
            configuration=optimal_config,
            performance_metrics={
                "hardware_tier": performance_tier,
                "memory_usage": 0,
                "processing_speed": 0,
                "quality_score": 0
            }
        )
        
        self.sessions[session_id] = session
        
        # Start ML adaptation for the session
        if hasattr(self, 'ml_adaptation'):
            await self.ml_adaptation.start_session_adaptation(session_id, profile)
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session
    
    async def get_session(self, session_id: str) -> Optional[UXSession]:
        """Get session information by ID."""
        session = self.sessions.get(session_id)
        if session:
            session.last_activity = datetime.now()
        return session
    
    async def end_session(self, session_id: str) -> bool:
        """End a user session and clean up resources."""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        # Stop ML adaptation
        if hasattr(self, 'ml_adaptation'):
            await self.ml_adaptation.end_session_adaptation(session_id)
        
        # Close WebSocket if connected
        if session_id in self.websockets:
            websocket = self.websockets[session_id]
            try:
                await websocket.close()
            except:
                pass
            del self.websockets[session_id]
        
        # Remove session
        session.status = "ended"
        del self.sessions[session_id]
        
        logger.info(f"Ended session {session_id}")
        return True
    
    async def update_configuration(self, session_id: str, request: ConfigurationRequest) -> Dict[str, Any]:
        """Update session configuration with optimization."""
        session = self.sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update hardware settings
        if request.hardware_settings and hasattr(self, 'hardware_detector'):
            hardware_info = self.hardware_detector.detect_hardware()
            hardware_info.update(request.hardware_settings)
        
        # Update user preferences
        if request.user_preferences and hasattr(self, 'user_profiles'):
            profile = self.user_profiles.get_profile(session.user_id)
            if profile:
                profile.update(request.user_preferences)
        
        # Optimize new configuration
        if hasattr(self, 'config_optimizer'):
            optimal_config = self.config_optimizer.optimize_configuration(
                hardware_info if 'hardware_info' in locals() else {},
                profile if 'profile' in locals() else {},
                goals=request.optimization_goals or ["performance", "quality"]
            )
            session.configuration.update(optimal_config)
        
        session.last_activity = datetime.now()
        
        # Notify via WebSocket if connected
        if session_id in self.websockets:
            await self.notify_websocket(session_id, {
                "type": "configuration_updated",
                "configuration": session.configuration
            })
        
        return session.configuration
    
    async def submit_feedback(self, request: FeedbackRequest) -> Dict[str, Any]:
        """Submit feedback for a session."""
        session = self.sessions.get(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if hasattr(self, 'feedback_system'):
            # Submit feedback to the comprehensive feedback system
            feedback_result = await self.feedback_system.submit_feedback(
                session_id=request.session_id,
                user_id=session.user_id,
                feedback_type=request.feedback_type,
                content=request.content,
                rating=request.rating,
                category=request.category,
                metadata=request.metadata
            )
            
            # Trigger ML adaptation based on feedback
            if hasattr(self, 'ml_adaptation'):
                await self.ml_adaptation.process_feedback(
                    request.session_id,
                    feedback_result
                )
            
            return feedback_result
        else:
            # Simple feedback storage without full system
            feedback_data = {
                "session_id": request.session_id,
                "type": request.feedback_type,
                "content": request.content,
                "rating": request.rating,
                "timestamp": datetime.now().isoformat(),
                "status": "received"
            }
            
            # Notify via WebSocket
            if request.session_id in self.websockets:
                await self.notify_websocket(request.session_id, {
                    "type": "feedback_received",
                    "feedback": feedback_data
                })
            
            return feedback_data
    
    async def get_analytics(self, session_id: Optional[str] = None) -> AnalyticsResponse:
        """Get analytics dashboard data."""
        if hasattr(self, 'ml_adaptation') and hasattr(self, 'feedback_system'):
            # Get comprehensive analytics
            if session_id:
                session_analytics = await self.ml_adaptation.get_session_analytics(session_id)
                user_analytics = await self.feedback_system.get_user_analytics(
                    self.sessions[session_id].user_id if session_id in self.sessions else None
                )
            else:
                session_analytics = await self.ml_adaptation.get_all_sessions_analytics()
                user_analytics = await self.feedback_system.get_global_analytics()
            
            performance_trends = await self.predictive_optimizer.get_performance_trends()
            recommendations = await self.predictive_optimizer.get_optimization_recommendations()
        else:
            # Basic analytics
            session_analytics = {
                "total_sessions": len(self.sessions),
                "active_sessions": len([s for s in self.sessions.values() if s.status == "active"])
            }
            user_analytics = {"total_users": len(set(s.user_id for s in self.sessions.values() if s.user_id))}
            performance_trends = {"status": "unavailable"}
            recommendations = []
        
        return AnalyticsResponse(
            session_analytics=session_analytics,
            user_analytics=user_analytics,
            performance_trends=performance_trends,
            optimization_recommendations=recommendations
        )
    
    async def run_optimization(self, session_id: str) -> Dict[str, Any]:
        """Trigger optimization for a specific session."""
        session = self.sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        optimization_results = {}
        
        # Run ML-based optimization
        if hasattr(self, 'ml_adaptation'):
            ml_results = await self.ml_adaptation.optimize_session(session_id)
            optimization_results.update(ml_results)
        
        # Run predictive optimization
        if hasattr(self, 'predictive_optimizer'):
            predictive_results = await self.predictive_optimizer.optimize_session(session_id)
            optimization_results.update(predictive_results)
        
        # Update session configuration
        if optimization_results.get('recommended_config'):
            session.configuration.update(optimization_results['recommended_config'])
            session.last_activity = datetime.now()
        
        # Notify via WebSocket
        if session_id in self.websockets:
            await self.notify_websocket(session_id, {
                "type": "optimization_completed",
                "results": optimization_results
            })
        
        return optimization_results
    
    async def notify_websocket(self, session_id: str, message: Dict[str, Any]):
        """Send notification to WebSocket if connected."""
        if session_id in self.websockets:
            try:
                await self.websockets[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {e}")
                # Remove disconnected WebSocket
                del self.websockets[session_id]

# Global UX API manager instance
ux_manager = UXAPIManager()

# API Routes
@router.post("/session/create", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest):
    """Create a new user session with UX optimization."""
    try:
        session = await ux_manager.create_session(request)
        
        return SessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            status=session.status,
            created_at=session.created_at,
            last_activity=session.last_activity,
            configuration=session.configuration,
            performance_metrics=session.performance_metrics
        )
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=f"Session creation failed: {str(e)}")

@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session status and information."""
    session = await ux_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        status=session.status,
        created_at=session.created_at,
        last_activity=session.last_activity,
        configuration=session.configuration,
        performance_metrics=session.performance_metrics
    )

@router.delete("/session/{session_id}")
async def end_session(session_id: str):
    """End a user session and clean up resources."""
    success = await ux_manager.end_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"status": "session_ended", "session_id": session_id}

@router.put("/config/hardware")
async def update_hardware_config(session_id: str, request: ConfigurationRequest):
    """Update hardware configuration for a session."""
    try:
        configuration = await ux_manager.update_configuration(session_id, request)
        return {"status": "configuration_updated", "configuration": configuration}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration update failed: {str(e)}")

@router.get("/config/profile")
async def get_user_profile(session_id: str):
    """Get user profile for a session."""
    session = await ux_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if hasattr(ux_manager, 'user_profiles') and session.user_id:
        profile = ux_manager.user_profiles.get_profile(session.user_id)
        return {"profile": profile or {}, "session_id": session_id}
    else:
        return {"profile": {}, "session_id": session_id, "status": "profile_system_unavailable"}

@router.post("/feedback/submit")
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for analysis and optimization."""
    try:
        result = await ux_manager.submit_feedback(request)
        return {"status": "feedback_submitted", "result": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Feedback submission failed: {str(e)}")

@router.get("/analytics/dashboard", response_model=AnalyticsResponse)
async def get_analytics_dashboard(session_id: Optional[str] = None):
    """Get analytics dashboard data."""
    try:
        analytics = await ux_manager.get_analytics(session_id)
        return analytics
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics retrieval failed: {str(e)}")

@router.post("/optimization/run")
async def run_optimization(session_id: str):
    """Trigger optimization for a specific session."""
    try:
        results = await ux_manager.run_optimization(session_id)
        return {"status": "optimization_completed", "results": results}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to run optimization: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

# WebSocket endpoint for real-time updates
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time session updates."""
    await websocket.accept()
    
    # Verify session exists
    session = await ux_manager.get_session(session_id)
    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return
    
    # Register WebSocket
    ux_manager.websockets[session_id] = websocket
    session.websocket = websocket
    
    try:
        # Send initial status
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif message.get("type") == "request_update":
                    # Send current session status
                    await websocket.send_text(json.dumps({
                        "type": "session_update",
                        "configuration": session.configuration,
                        "performance_metrics": session.performance_metrics,
                        "timestamp": datetime.now().isoformat()
                    }))
                
                # Update session activity
                session.last_activity = datetime.now()
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"type": "error", "message": "Invalid JSON"}))
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        # Clean up WebSocket connection
        if session_id in ux_manager.websockets:
            del ux_manager.websockets[session_id]
        if session:
            session.websocket = None

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(ux_manager.sessions),
        "websocket_connections": len(ux_manager.websockets),
        "components_available": ux_manager.components_available if hasattr(ux_manager, 'components_available') else True
    }
