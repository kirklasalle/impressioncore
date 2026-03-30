"""
HCEP Streaming Server for Avatar Integration
=============================================
WebSocket server that streams real-time HCEP (Human Conversation Eye Points)
data from Kinect to the frontend Avatar for eye tracking during conversation.

Data Flow:
    Kinect → Face Recognition → HCEP Analysis → WebSocket → Avatar

Usage:
    python hcep_avatar_server.py

    Frontend connects to: ws://localhost:8765

    Receives JSON:
    {
        "type": "hcep",
        "identity": "Alice",
        "gaze": {
            "region": "UPPER_LEFT",
            "pitch": 15.2,
            "yaw": -18.5,
            "roll": 2.1
        },
        "state": {
            "cognitive": "REMEMBERING",
            "valence": "NEUTRAL",
            "description": "recalling memories"
        },
        "confidence": 0.87,
        "timestamp": 1736646000.123
    }

Author: ImpressionCore Team
Created: January 2026
"""

import asyncio
import json
import logging
import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

# WebSocket library - use websockets if available, fallback to simple HTTP
try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False
    logger.warning("websockets not installed. Run: pip install websockets")


# ============================================================================
# HCEP AVATAR MESSAGE FORMAT
# ============================================================================

def format_hcep_for_avatar(reading) -> dict:
    """
    Format HCEP reading for Avatar consumption.

    Args:
        reading: HCEPReading from hcep.py

    Returns:
        Avatar-compatible JSON dict
    """
    return {
        "type": "hcep",
        "identity": reading.identity,
        "gaze": {
            "region": reading.gaze_region.name,
            "pitch": round(reading.pitch, 2),
            "yaw": round(reading.yaw, 2),
            "roll": round(reading.roll, 2)
        },
        "state": {
            "cognitive": reading.cognitive_state.name,
            "valence": reading.emotional_valence.name,
            "confidence": round(reading.confidence, 3)
        },
        "timestamp": reading.timestamp
    }


def format_skeleton_for_avatar(skeleton) -> dict:
    """
    Format skeleton data for Avatar body tracking.
    """
    return {
        "type": "skeleton",
        "tracking_id": skeleton.tracking_id,
        "position": {
            "x": round(skeleton.position[0], 3),
            "y": round(skeleton.position[1], 3),
            "z": round(skeleton.position[2], 3)
        },
        "head": {
            "x": round(skeleton.joints[3].x, 3),
            "y": round(skeleton.joints[3].y, 3),
            "z": round(skeleton.joints[3].z, 3)
        } if len(skeleton.joints) > 3 else None
    }


# ============================================================================
# WEBSOCKET SERVER
# ============================================================================

class HCEPAvatarServer:
    """
    WebSocket server for streaming HCEP data to Avatar frontend.
    """

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: set = set()
        self.running = False
        self.kinect = None
        self.hcep_integration = None

        # Stats
        self.frames_processed = 0
        self.messages_sent = 0

    async def register(self, websocket):
        """Register a new client connection"""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total: {len(self.clients)}")

        # Send welcome message
        await websocket.send(json.dumps({
            "type": "connected",
            "message": "HCEP Avatar Server ready",
            "version": "1.0"
        }))

    async def unregister(self, websocket):
        """Remove a client connection"""
        self.clients.discard(websocket)
        logger.info(f"Client disconnected. Total: {len(self.clients)}")

    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        if not self.clients:
            return

        json_msg = json.dumps(message)
        await asyncio.gather(
            *[client.send(json_msg) for client in self.clients],
            return_exceptions=True
        )
        self.messages_sent += 1

    async def handle_client(self, websocket, path):
        """Handle individual client connection"""
        await self.register(websocket)
        try:
            async for message in websocket:
                # Handle incoming commands from Avatar
                try:
                    data = json.loads(message)
                    await self.handle_command(websocket, data)
                except json.JSONDecodeError:
                    pass
        finally:
            await self.unregister(websocket)

    async def handle_command(self, websocket, data: dict):
        """Handle commands from Avatar frontend"""
        cmd = data.get("command")

        if cmd == "register_face":
            # Register a new face identity
            name = data.get("name")
            if name:
                await websocket.send(json.dumps({
                    "type": "response",
                    "command": "register_face",
                    "status": "ready",
                    "message": f"Ready to register {name}. Look at camera."
                }))

        elif cmd == "get_status":
            await websocket.send(json.dumps({
                "type": "status",
                "frames_processed": self.frames_processed,
                "messages_sent": self.messages_sent,
                "clients_connected": len(self.clients),
                "kinect_connected": self.kinect is not None and self.kinect.is_open
            }))

    async def kinect_loop(self):
        """Main loop for processing Kinect frames"""
        from src.vision.face_identity import FaceIdentityManager
        from src.vision.hcep import HCEPAnalyzer
        from tools.kinect_controller_app import KinectController

        logger.info("Initializing Kinect...")

        try:
            self.kinect = KinectController(sensor_index=0)
            if not self.kinect.open(use_color=True, use_depth=True, use_skeleton=True):
                logger.error("Failed to open Kinect. Broadcasting simulated data.")
                await self._simulated_loop()
                return

            logger.info("Kinect opened successfully!")

            # Initialize components
            face_manager = FaceIdentityManager("avatar_faces.pkl")
            hcep_analyzer = HCEPAnalyzer()

            # Broadcast device info
            info = self.kinect.get_device_info()
            await self.broadcast({
                "type": "device_info",
                "kinect": info
            })

            last_broadcast = 0
            target_fps = 30
            frame_interval = 1.0 / target_fps

            while self.running:
                # Get frames
                color = self.kinect.get_rgb_frame()
                if color is None:
                    await asyncio.sleep(0.01)
                    continue

                self.frames_processed += 1

                # Get skeleton data
                skeletons = self.kinect.get_skeleton_frame()

                # Broadcast skeleton data
                for skel in skeletons:
                    await self.broadcast(format_skeleton_for_avatar(skel))

                # Face tracking + HCEP
                face_data = self.kinect.get_face_data(color)
                if face_data and face_data.is_tracked:
                    # Identify face
                    name, conf = face_manager.identify(color)
                    if name != "Unknown":
                        # Run HCEP analysis
                        reading = hcep_analyzer.analyze(
                            identity=name,
                            pitch=face_data.pitch,
                            yaw=face_data.yaw,
                            roll=face_data.roll,
                            confidence=conf
                        )
                        await self.broadcast(format_hcep_for_avatar(reading))

                # Rate limiting
                now = time.time()
                elapsed = now - last_broadcast
                if elapsed < frame_interval:
                    await asyncio.sleep(frame_interval - elapsed)
                last_broadcast = time.time()

        except Exception as e:
            logger.exception(f"Kinect loop error: {e}")
        finally:
            if self.kinect:
                self.kinect.close()

    async def _simulated_loop(self):
        """Simulate HCEP data when no Kinect is connected"""
        import math

        from src.vision.hcep import HCEPAnalyzer

        logger.info("Running in SIMULATION mode")

        hcep_analyzer = HCEPAnalyzer()

        t = 0
        while self.running:
            # Simulate head movement in a pattern
            pitch = 15 * math.sin(t * 0.5)
            yaw = 20 * math.sin(t * 0.3)
            roll = 5 * math.sin(t * 0.7)

            reading = hcep_analyzer.analyze(
                identity="Simulated_User",
                pitch=pitch,
                yaw=yaw,
                roll=roll,
                confidence=0.9
            )

            await self.broadcast(format_hcep_for_avatar(reading))
            self.frames_processed += 1

            t += 0.1
            await asyncio.sleep(0.033)  # ~30 FPS

    async def run(self):
        """Start the server"""
        if not HAS_WEBSOCKETS:
            logger.error("websockets library required. pip install websockets")
            return

        self.running = True

        logger.info(f"Starting HCEP Avatar Server on ws://{self.host}:{self.port}")

        # Start Kinect processing in background
        asyncio.create_task(self.kinect_loop())  # noqa: RUF006

        # Start WebSocket server
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"Server listening on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever

    def stop(self):
        """Stop the server"""
        self.running = False


# ============================================================================
# STANDALONE TEST MODE
# ============================================================================

async def test_without_kinect():
    """Test server with simulated data"""
    server = HCEPAvatarServer()
    await server.run()


# ============================================================================
# MAIN
# ============================================================================

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print(" HCEP Avatar Streaming Server")
    print(" Human Conversation Eye Points → Avatar Eye Tracking")
    print("=" * 60)
    print()
    print("WebSocket endpoint: ws://localhost:8765")
    print("Press Ctrl+C to stop")
    print()

    server = HCEPAvatarServer()

    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()


if __name__ == "__main__":
    main()
