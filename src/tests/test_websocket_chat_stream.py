import asyncio
import json
import pytest
from fastapi.testclient import TestClient
from src.interfaces.triad_api import app
from src.interfaces import api_state
from src.orchestrator.session_manager import session_manager

class MockTriadInstance:
    def __init__(self):
        self.last_audio_url = "/audio/mock_speech.mp3"
        self.snapshot_url = "/captures/mock_snap.jpg"
        self.snapshot_urls = ["/captures/mock_snap.jpg"]
        
    def generate(self, prompt: str, sensory_data: dict = None, history: list = None):
        return {
            "response": "This is a mock response from Colossus synthesis.",
            "internal_monitors": {
                "left_hemisphere": "Logical thought process analysis.",
                "right_hemisphere": "Creative imagery association."
            },
            "nexus_logs": ["Command Executed: LOG"],
            "affective_state": "HAPPY",
            "snapshot_url": "/captures/mock_snap.jpg",
            "snapshot_urls": ["/captures/mock_snap.jpg"]
        }
        
    def speak(self, text: str, play_now: bool = True):
        pass


@pytest.fixture(autouse=True)
def setup_mock_triad():
    # Save original state
    orig_triad = api_state.triad_instance
    # Setup mock
    api_state.triad_instance = MockTriadInstance()
    yield
    # Restore original state
    api_state.triad_instance = orig_triad


def test_websocket_chat_stream_success():
    """
    Test that connecting, sending a handshake, and receiving streamed events works perfectly.
    """
    client = TestClient(app)
    session_id = "test-stream-session-123"
    
    # Ensure session exists or can be written to
    session_manager.save_session(session_id, {"messages": []})
    
    with client.websocket_connect("/v1/chat/stream") as websocket:
        # Send Handshake Request
        websocket.send_json({
            "prompt": "Hello test world",
            "session_id": session_id,
            "voice_enabled": False
        })
        
        events = []
        # Receive events
        while True:
            try:
                data = websocket.receive_json()
                events.append(data)
                if data.get("event") in ("done", "error"):
                    break
            except Exception:
                break
                
        # Assertions
        assert len(events) > 0
        
        # Verify specific events exist in the stream
        event_types = [e.get("event") for e in events]
        assert "left_thought" in event_types
        assert "right_thought" in event_types
        assert "token" in event_types
        assert "done" in event_types
        
        # Check Left Lobe Thought Content
        left_event = next(e for e in events if e.get("event") == "left_thought")
        assert "Logical" in left_event.get("text")
        
        # Check Right Lobe Thought Content
        right_event = next(e for e in events if e.get("event") == "right_thought")
        assert "Creative" in right_event.get("text")
        
        # Check Done Event
        done_event = next(e for e in events if e.get("event") == "done")
        assert done_event.get("response") == "This is a mock response from Colossus synthesis."
        assert done_event.get("affective_state") == "HAPPY"


class MockWebSocket:
    def __init__(self, payload):
        self.payload = payload
        self.sent_messages = []
        self.closed = False
        
    async def accept(self):
        pass
        
    async def receive_json(self):
        return self.payload
        
    async def send_json(self, data):
        self.sent_messages.append(data)
        # Simulate disconnect immediately after sending the first event
        if len(self.sent_messages) == 1:
            raise Exception("Mock Client Disconnect")
            
    async def close(self, code=1000):
        self.closed = True


def test_websocket_chat_stream_disconnect_resilience():
    """
    Test that if a client disconnects mid-generation, the background task still completes,
    and the response is fully saved to the session history/database.
    """
    async def run_resilience_test():
        session_id = "resilient-session-456"
        session_manager.save_session(session_id, {"messages": []})
        
        payload = {
            "prompt": "Persistent background check",
            "session_id": session_id,
            "voice_enabled": False
        }
        
        ws = MockWebSocket(payload)
        
        from src.interfaces.routes.chat import chat_stream
        # Run route handler. It will hit Mock Client Disconnect and catch it.
        await chat_stream(ws)
        
        # Await the background task on the same event loop to finish executing
        assert api_state.last_bg_task is not None
        await api_state.last_bg_task
        
        # Read session from session manager
        session = session_manager.get_session(session_id)
        assert session is not None
        messages = session.get("messages", [])
        
        # Verify that BOTH the user message and the assistant response were successfully written to history
        roles = [m.get("role") for m in messages]
        assert "user" in roles
        assert "assistant" in roles
        
        assistant_msg = next(m for m in messages if m.get("role") == "assistant")
        assert assistant_msg.get("content") == "This is a mock response from Colossus synthesis."
        print("Resilience check succeeded: assistant response persistent in database after websocket disconnect.")

    asyncio.run(run_resilience_test())
