"""
ImpressionCore WebSocket Handler
Phase 7D: Production Integration and Optimization

Real-time WebSocket communication for live updates and interactive sessions.

Author: GitHub Copilot & Kirk LaSalle
Date: June 1, 2025
"""

import asyncio
import json
import time
import weakref
from typing import Dict, List, Optional, Any, Set, Callable, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect
import uvloop

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
    logger = setup_logger("websocket_handler", level="INFO")
else:
    logger = logging.getLogger("websocket_handler")

class MessageType(Enum):
    """WebSocket message types."""
    # Connection management
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"
    
    # Session updates
    SESSION_UPDATE = "session_update"
    CONFIG_UPDATE = "config_update"
    STATUS_UPDATE = "status_update"
    
    # Real-time data
    PERFORMANCE_UPDATE = "performance_update"
    PROGRESS_UPDATE = "progress_update"
    METRICS_UPDATE = "metrics_update"
    
    # Feedback and interaction
    FEEDBACK_RECEIVED = "feedback_received"
    USER_INPUT = "user_input"
    SYSTEM_NOTIFICATION = "system_notification"
    
    # Optimization
    OPTIMIZATION_START = "optimization_start"
    OPTIMIZATION_COMPLETE = "optimization_complete"
    RECOMMENDATION = "recommendation"
    
    # Errors
    ERROR = "error"
    WARNING = "warning"

@dataclass
class WebSocketMessage:
    """Standard WebSocket message format."""
    type: MessageType
    session_id: Optional[str]
    timestamp: datetime
    data: Any
    message_id: Optional[str] = None
    requires_response: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for JSON serialization."""
        return {
            "type": self.type.value,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "message_id": self.message_id,
            "requires_response": self.requires_response
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebSocketMessage':
        """Create message from dictionary."""
        return cls(
            type=MessageType(data["type"]),
            session_id=data.get("session_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            data=data["data"],
            message_id=data.get("message_id"),
            requires_response=data.get("requires_response", False)
        )

@dataclass
class ConnectionInfo:
    """Information about a WebSocket connection."""
    connection_id: str
    session_id: Optional[str]
    user_id: Optional[str]
    websocket: WebSocket
    connected_at: datetime
    last_activity: datetime
    message_count: int = 0
    subscriptions: Set[str] = None
    
    def __post_init__(self):
        if self.subscriptions is None:
            self.subscriptions = set()

class WebSocketManager:
    """
    Central WebSocket connection manager for real-time communication.
    Handles connection lifecycle, message routing, and event broadcasting.
    """
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.connections: Dict[str, ConnectionInfo] = {}
        self.session_connections: Dict[str, Set[str]] = defaultdict(set)
        self.user_connections: Dict[str, Set[str]] = defaultdict(set)
        
        # Message handlers
        self.message_handlers: Dict[MessageType, List[Callable]] = defaultdict(list)
        
        # Broadcasting subscriptions
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)  # topic -> connection_ids
        
        # Rate limiting
        self.rate_limits: Dict[str, List[float]] = defaultdict(list)  # connection_id -> timestamps
        self.max_messages_per_minute = 60
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        self._start_background_tasks()
        
        logger.info("WebSocketManager initialized")
    
    def _start_background_tasks(self):
        """Start background tasks for connection management."""
        # Heartbeat task
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self.background_tasks.add(heartbeat_task)
        heartbeat_task.add_done_callback(self.background_tasks.discard)
        
        # Cleanup task
        cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.background_tasks.add(cleanup_task)
        cleanup_task.add_done_callback(self.background_tasks.discard)
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages to maintain connections."""
        while True:
            try:
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
                # Send ping to all connections
                ping_message = WebSocketMessage(
                    type=MessageType.PING,
                    session_id=None,
                    timestamp=datetime.now(),
                    data={"timestamp": datetime.now().isoformat()}
                )
                
                await self.broadcast_to_all(ping_message)
                
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(60)  # Back off on error
    
    async def _cleanup_loop(self):
        """Clean up stale connections and rate limit data."""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
                current_time = datetime.now()
                stale_connections = []
                
                # Find stale connections (no activity for 30 minutes)
                for conn_id, conn_info in self.connections.items():
                    time_since_activity = (current_time - conn_info.last_activity).total_seconds()
                    if time_since_activity > 1800:  # 30 minutes
                        stale_connections.append(conn_id)
                
                # Remove stale connections
                for conn_id in stale_connections:
                    await self._remove_connection(conn_id)
                    logger.info(f"Removed stale connection {conn_id}")
                
                # Clean up rate limit data
                one_minute_ago = time.time() - 60
                for conn_id in list(self.rate_limits.keys()):
                    self.rate_limits[conn_id] = [
                        ts for ts in self.rate_limits[conn_id] 
                        if ts > one_minute_ago
                    ]
                    if not self.rate_limits[conn_id]:
                        del self.rate_limits[conn_id]
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(300)
    
    async def connect(self, websocket: WebSocket, connection_id: str, 
                     session_id: Optional[str] = None, user_id: Optional[str] = None) -> bool:
        """Accept a new WebSocket connection."""
        try:
            await websocket.accept()
            
            # Create connection info
            conn_info = ConnectionInfo(
                connection_id=connection_id,
                session_id=session_id,
                user_id=user_id,
                websocket=websocket,
                connected_at=datetime.now(),
                last_activity=datetime.now()
            )
            
            # Store connection
            self.connections[connection_id] = conn_info
            
            # Index by session and user
            if session_id:
                self.session_connections[session_id].add(connection_id)
            if user_id:
                self.user_connections[user_id].add(connection_id)
            
            # Send connection confirmation
            connect_message = WebSocketMessage(
                type=MessageType.CONNECT,
                session_id=session_id,
                timestamp=datetime.now(),
                data={
                    "connection_id": connection_id,
                    "status": "connected",
                    "server_time": datetime.now().isoformat()
                }
            )
            
            await self.send_to_connection(connection_id, connect_message)
            
            logger.info(f"WebSocket connection established: {connection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection: {e}")
            return False
    
    async def disconnect(self, connection_id: str):
        """Disconnect a WebSocket connection."""
        await self._remove_connection(connection_id)
    
    async def _remove_connection(self, connection_id: str):
        """Remove a connection and clean up references."""
        conn_info = self.connections.get(connection_id)
        if not conn_info:
            return
        
        # Remove from indexes
        if conn_info.session_id:
            self.session_connections[conn_info.session_id].discard(connection_id)
        if conn_info.user_id:
            self.user_connections[conn_info.user_id].discard(connection_id)
        
        # Remove from subscriptions
        for topic, subscribers in self.subscriptions.items():
            subscribers.discard(connection_id)
        
        # Close WebSocket if still open
        try:
            await conn_info.websocket.close()
        except:
            pass
        
        # Remove from connections
        del self.connections[connection_id]
        
        logger.info(f"WebSocket connection removed: {connection_id}")
    
    def _check_rate_limit(self, connection_id: str) -> bool:
        """Check if connection exceeds rate limit."""
        current_time = time.time()
        
        # Clean old timestamps
        one_minute_ago = current_time - 60
        self.rate_limits[connection_id] = [
            ts for ts in self.rate_limits[connection_id] 
            if ts > one_minute_ago
        ]
        
        # Check rate limit
        if len(self.rate_limits[connection_id]) >= self.max_messages_per_minute:
            return False
        
        # Add current timestamp
        self.rate_limits[connection_id].append(current_time)
        return True
    
    async def handle_message(self, connection_id: str, message_data: Dict[str, Any]):
        """Handle incoming WebSocket message."""
        conn_info = self.connections.get(connection_id)
        if not conn_info:
            return
        
        # Check rate limit
        if not self._check_rate_limit(connection_id):
            error_message = WebSocketMessage(
                type=MessageType.ERROR,
                session_id=conn_info.session_id,
                timestamp=datetime.now(),
                data={"error": "Rate limit exceeded", "max_per_minute": self.max_messages_per_minute}
            )
            await self.send_to_connection(connection_id, error_message)
            return
        
        try:
            # Parse message
            message = WebSocketMessage.from_dict(message_data)
            
            # Update activity
            conn_info.last_activity = datetime.now()
            conn_info.message_count += 1
            
            # Handle specific message types
            if message.type == MessageType.PING:
                await self._handle_ping(connection_id, message)
            elif message.type == MessageType.USER_INPUT:
                await self._handle_user_input(connection_id, message)
            elif message.type == MessageType.FEEDBACK_RECEIVED:
                await self._handle_feedback(connection_id, message)
            else:
                # Call registered handlers
                for handler in self.message_handlers[message.type]:
                    try:
                        await handler(connection_id, message)
                    except Exception as e:
                        logger.error(f"Error in message handler: {e}")
            
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            error_message = WebSocketMessage(
                type=MessageType.ERROR,
                session_id=conn_info.session_id,
                timestamp=datetime.now(),
                data={"error": "Failed to process message", "details": str(e)}
            )
            await self.send_to_connection(connection_id, error_message)
    
    async def _handle_ping(self, connection_id: str, message: WebSocketMessage):
        """Handle ping message with pong response."""
        pong_message = WebSocketMessage(
            type=MessageType.PONG,
            session_id=message.session_id,
            timestamp=datetime.now(),
            data={"ping_timestamp": message.timestamp.isoformat()}
        )
        await self.send_to_connection(connection_id, pong_message)
    
    async def _handle_user_input(self, connection_id: str, message: WebSocketMessage):
        """Handle user input message."""
        # Broadcast to session subscribers
        if message.session_id:
            await self.broadcast_to_session(message.session_id, message)
    
    async def _handle_feedback(self, connection_id: str, message: WebSocketMessage):
        """Handle feedback message."""
        # Process feedback data
        feedback_data = message.data
        
        # Acknowledge receipt
        ack_message = WebSocketMessage(
            type=MessageType.SYSTEM_NOTIFICATION,
            session_id=message.session_id,
            timestamp=datetime.now(),
            data={"message": "Feedback received", "feedback_id": feedback_data.get("id")}
        )
        await self.send_to_connection(connection_id, ack_message)
    
    async def send_to_connection(self, connection_id: str, message: WebSocketMessage):
        """Send message to a specific connection."""
        conn_info = self.connections.get(connection_id)
        if not conn_info:
            return False
        
        try:
            message_json = json.dumps(message.to_dict())
            await conn_info.websocket.send_text(message_json)
            return True
        except Exception as e:
            logger.warning(f"Failed to send message to {connection_id}: {e}")
            await self._remove_connection(connection_id)
            return False
    
    async def broadcast_to_session(self, session_id: str, message: WebSocketMessage):
        """Broadcast message to all connections in a session."""
        connection_ids = self.session_connections.get(session_id, set()).copy()
        
        for conn_id in connection_ids:
            await self.send_to_connection(conn_id, message)
    
    async def broadcast_to_user(self, user_id: str, message: WebSocketMessage):
        """Broadcast message to all connections of a user."""
        connection_ids = self.user_connections.get(user_id, set()).copy()
        
        for conn_id in connection_ids:
            await self.send_to_connection(conn_id, message)
    
    async def broadcast_to_all(self, message: WebSocketMessage):
        """Broadcast message to all connections."""
        connection_ids = list(self.connections.keys())
        
        for conn_id in connection_ids:
            await self.send_to_connection(conn_id, message)
    
    async def subscribe_to_topic(self, connection_id: str, topic: str):
        """Subscribe a connection to a topic for broadcasting."""
        if connection_id in self.connections:
            self.subscriptions[topic].add(connection_id)
            self.connections[connection_id].subscriptions.add(topic)
            logger.info(f"Connection {connection_id} subscribed to {topic}")
    
    async def unsubscribe_from_topic(self, connection_id: str, topic: str):
        """Unsubscribe a connection from a topic."""
        self.subscriptions[topic].discard(connection_id)
        if connection_id in self.connections:
            self.connections[connection_id].subscriptions.discard(topic)
            logger.info(f"Connection {connection_id} unsubscribed from {topic}")
    
    async def broadcast_to_topic(self, topic: str, message: WebSocketMessage):
        """Broadcast message to all subscribers of a topic."""
        connection_ids = self.subscriptions.get(topic, set()).copy()
        
        for conn_id in connection_ids:
            await self.send_to_connection(conn_id, message)
    
    def register_message_handler(self, message_type: MessageType, handler: Callable):
        """Register a handler for a specific message type."""
        self.message_handlers[message_type].append(handler)
        logger.info(f"Registered handler for {message_type.value}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics."""
        total_connections = len(self.connections)
        session_distribution = {
            session_id: len(conn_ids) 
            for session_id, conn_ids in self.session_connections.items()
        }
        user_distribution = {
            user_id: len(conn_ids) 
            for user_id, conn_ids in self.user_connections.items()
        }
        
        # Calculate average message count
        total_messages = sum(conn.message_count for conn in self.connections.values())
        avg_messages = total_messages / total_connections if total_connections > 0 else 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_connections": total_connections,
            "active_sessions": len(self.session_connections),
            "active_users": len(self.user_connections),
            "total_messages_processed": total_messages,
            "average_messages_per_connection": avg_messages,
            "subscription_topics": len(self.subscriptions),
            "session_distribution": session_distribution,
            "user_distribution": user_distribution
        }
    
    async def shutdown(self):
        """Shutdown the WebSocket manager."""
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Close all connections
        connection_ids = list(self.connections.keys())
        for conn_id in connection_ids:
            await self._remove_connection(conn_id)
        
        logger.info("WebSocketManager shutdown complete")

class RealTimeUpdater:
    """
    Real-time update service for pushing live data to WebSocket clients.
    Integrates with session management and performance monitoring.
    """
    
    def __init__(self, websocket_manager: WebSocketManager):
        """Initialize the real-time updater."""
        self.websocket_manager = websocket_manager
        self.update_intervals = {
            "performance": 2.0,  # 2 seconds
            "progress": 1.0,     # 1 second
            "metrics": 5.0,      # 5 seconds
            "status": 10.0       # 10 seconds
        }
        
        # Update tasks
        self.update_tasks: Dict[str, asyncio.Task] = {}
        self._start_update_tasks()
        
        logger.info("RealTimeUpdater initialized")
    
    def _start_update_tasks(self):
        """Start real-time update tasks."""
        for update_type, interval in self.update_intervals.items():
            task = asyncio.create_task(self._update_loop(update_type, interval))
            self.update_tasks[update_type] = task
    
    async def _update_loop(self, update_type: str, interval: float):
        """Generic update loop for different data types."""
        while True:
            try:
                await asyncio.sleep(interval)
                
                if update_type == "performance":
                    await self._send_performance_updates()
                elif update_type == "progress":
                    await self._send_progress_updates()
                elif update_type == "metrics":
                    await self._send_metrics_updates()
                elif update_type == "status":
                    await self._send_status_updates()
                
            except Exception as e:
                logger.error(f"Error in {update_type} update loop: {e}")
                await asyncio.sleep(interval * 2)  # Back off on error
    
    async def _send_performance_updates(self):
        """Send performance updates to subscribed clients."""
        # Get system performance data (placeholder)
        performance_data = {
            "cpu_percent": 45.2,
            "memory_percent": 62.8,
            "gpu_memory_percent": 78.5,
            "timestamp": datetime.now().isoformat()
        }
        
        message = WebSocketMessage(
            type=MessageType.PERFORMANCE_UPDATE,
            session_id=None,
            timestamp=datetime.now(),
            data=performance_data
        )
        
        await self.websocket_manager.broadcast_to_topic("performance", message)
    
    async def _send_progress_updates(self):
        """Send progress updates for active operations."""
        # This would integrate with actual processing systems
        pass
    
    async def _send_metrics_updates(self):
        """Send metrics updates to monitoring clients."""
        # Get connection stats
        stats = self.websocket_manager.get_connection_stats()
        
        message = WebSocketMessage(
            type=MessageType.METRICS_UPDATE,
            session_id=None,
            timestamp=datetime.now(),
            data=stats
        )
        
        await self.websocket_manager.broadcast_to_topic("metrics", message)
    
    async def _send_status_updates(self):
        """Send general status updates."""
        status_data = {
            "server_status": "healthy",
            "active_connections": len(self.websocket_manager.connections),
            "uptime": "unknown",  # Would calculate actual uptime
            "timestamp": datetime.now().isoformat()
        }
        
        message = WebSocketMessage(
            type=MessageType.STATUS_UPDATE,
            session_id=None,
            timestamp=datetime.now(),
            data=status_data
        )
        
        await self.websocket_manager.broadcast_to_topic("status", message)
    
    async def send_optimization_update(self, session_id: str, optimization_data: Dict[str, Any]):
        """Send optimization update to a specific session."""
        message = WebSocketMessage(
            type=MessageType.OPTIMIZATION_COMPLETE,
            session_id=session_id,
            timestamp=datetime.now(),
            data=optimization_data
        )
        
        await self.websocket_manager.broadcast_to_session(session_id, message)
    
    async def send_recommendation(self, session_id: str, recommendation_data: Dict[str, Any]):
        """Send optimization recommendation to a session."""
        message = WebSocketMessage(
            type=MessageType.RECOMMENDATION,
            session_id=session_id,
            timestamp=datetime.now(),
            data=recommendation_data
        )
        
        await self.websocket_manager.broadcast_to_session(session_id, message)
    
    async def shutdown(self):
        """Shutdown the real-time updater."""
        for task in self.update_tasks.values():
            task.cancel()
        
        logger.info("RealTimeUpdater shutdown complete")

# Global WebSocket manager instance
websocket_manager = WebSocketManager()
real_time_updater = RealTimeUpdater(websocket_manager)

def get_websocket_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance."""
    return websocket_manager

def get_real_time_updater() -> RealTimeUpdater:
    """Get the global real-time updater instance."""
    return real_time_updater

async def shutdown_websocket_system():
    """Shutdown the WebSocket system."""
    await real_time_updater.shutdown()
    await websocket_manager.shutdown()
