# ImpressionCore B3-Triad API Reference

**Created:** December 25, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle  
**Tags:** #docs\api\TRIAD_API_REFERENCE.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

**Version:** 1.0.0  
**Author:** Kirk LaSalle  
**Status:** Production

---

## Executive Summary

The ImpressionCore B3-Triad API provides a comprehensive interface to the revolutionary brain-inspired multimodal AI system. This document covers all endpoints, request/response schemas, and includes detailed architecture diagrams.

### Quick Start

```bash
# Start the backend
python src/interfaces/triad_api.py

# Start the frontend  
cd src/interfaces/web_client && npm run dev

# Access the API
curl http://localhost:8000/v1/hardware
```

---

## 🧠 Brain-Triad Architecture

### System Overview

```mermaid
flowchart TB
    subgraph Client["🌐 Frontend Client"]
        UI[React App<br/>localhost:3000]
    end

    subgraph API["⚡ FastAPI Server"]
        direction TB
        EP1["/v1/process"]
        EP2["/v1/hardware"]
        EP3["/v1/vision/stream"]
        EP4["/v1/sessions/*"]
        EP5["/v1/memory/search"]
    end

    subgraph Triad["🧠 Brain-Triad Core"]
        direction LR
        LEFT["🔵 Left Hemisphere<br/>InternVL2-1B<br/>Analytical"]
        RIGHT["🟢 Right Hemisphere<br/>InternVL2-1B<br/>Creative"]
        COLOSSUS["🟣 Colossus<br/>Integrator<br/>Synthesis"]
        
        LEFT --> COLOSSUS
        RIGHT --> COLOSSUS
    end

    subgraph Vision["👁️ Vision Layer"]
        direction TB
        PS[PS Eye<br/>libusb/pseyepy]
        CV[OpenCV<br/>DSHOW/MSMF]
        MJPEG[MJPEG<br/>Stream Generator]
        
        PS --> MJPEG
        CV --> MJPEG
    end

    subgraph Memory["💾 Session Memory"]
        SM[Session Manager]
        HIST[JSON Files<br/>history/]
    end

    UI --> API
    EP1 --> Triad
    EP2 --> Vision
    EP3 --> MJPEG
    EP4 --> Memory
    EP5 --> SM
    
    Triad --> TTS[🔊 Neural TTS<br/>Ava Voice]

    style LEFT fill:#1976d2,color:#fff
    style RIGHT fill:#388e3c,color:#fff
    style COLOSSUS fill:#7b1fa2,color:#fff
    style PS fill:#e65100,color:#fff
```

### Processing Pipeline

```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI
    participant L as Left Hemisphere
    participant R as Right Hemisphere
    participant COL as Colossus
    participant NEX as Nexus Interpreter
    participant TTS as Neural TTS

    C->>API: POST /v1/process
    Note over API: Decode image (if present)
    Note over API: Load session history
    
    par Parallel Processing
        API->>L: Analytical inference
        API->>R: Creative inference
    end
    
    L-->>COL: Left output
    R-->>COL: Right output
    
    COL->>COL: Synthesize response
    COL-->>NEX: Check for S-expressions
    
    alt Has Nexus Commands
        NEX->>NEX: Execute commands
        NEX-->>API: Command logs
    end
    
    opt Voice Enabled
        API->>TTS: Generate speech
        TTS-->>API: Audio file path
    end
    
    API-->>C: Response + monitors + audio
```

---

## 📡 API Endpoints

### POST /v1/process

**Multimodal AI Generation** - The primary inference endpoint.

#### Request Schema

```json
{
  "prompt": "string (required)",
  "image_base64": "string (optional)",
  "voice_enabled": true,
  "session_id": "string (optional)"
}
```

#### Response Schema

```json
{
  "response": "The AI-generated text response",
  "monitors": {
    "left_output": "Analytical perspective...",
    "right_output": "Creative interpretation...",
    "synthesis_confidence": 0.92
  },
  "nexus_logs": ["(LOG \"Processing complete\")"],
  "audio_url": "/audio/last_speech.mp3"
}
```

#### Example

```bash
curl -X POST http://localhost:8000/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What do you see?",
    "image_base64": "/9j/4AAQ...",
    "voice_enabled": true,
    "session_id": "abc123"
  }'
```

---

### GET /v1/hardware

**Hardware Status** - Returns vision layer and GPU telemetry.

#### Response Schema

```json
{
  "status": "OK",
  "vision_active": true,
  "detected_cameras": [
    {
      "id": 99,
      "active": true,
      "backend": "LIBUSB_PSEYEPY",
      "model": "PS Eye (Native)"
    }
  ],
  "vram_mode": true,
  "hardware_telemetry": {...}
}
```

---

### GET /v1/vision/stream

**Live MJPEG Video Stream** - Real-time camera feed.

#### Stream Architecture

```mermaid
flowchart LR
    subgraph Camera["📷 Camera Sources"]
        PS[PS Eye<br/>Index 99]
        OCV[OpenCV<br/>Index 0-10]
        FB[Fallback<br/>NO SIGNAL]
    end

    subgraph Pipeline["⚙️ Processing Pipeline"]
        CAP[Frame Capture]
        ENC[JPEG Encode]
        YLD[Yield Frame]
    end

    subgraph Client["🌐 Client"]
        IMG["<img> Element"]
    end

    PS -->|Priority 1| CAP
    OCV -->|Priority 2| CAP
    FB -->|Fallback| CAP
    
    CAP --> ENC
    ENC --> YLD
    YLD -->|multipart/x-mixed-replace| IMG

    style PS fill:#e65100,color:#fff
    style FB fill:#c62828,color:#fff
```

#### Usage

```html
<!-- Direct HTML embedding -->
<img src="http://localhost:8000/v1/vision/stream" alt="Live Feed" />
```

```javascript
// JavaScript with cache-busting
const streamUrl = `http://localhost:8000/v1/vision/stream?t=${Date.now()}`;
document.getElementById('video').src = streamUrl;
```

---

### Session Management Endpoints

```mermaid
erDiagram
    SESSION {
        string id PK
        string title
        datetime created_at
        datetime updated_at
    }
    MESSAGE {
        string id PK
        string session_id FK
        string role
        string content
        datetime timestamp
    }
    
    SESSION ||--o{ MESSAGE : contains
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/sessions` | GET | List all sessions |
| `/v1/sessions` | POST | Create new session |
| `/v1/sessions/{id}` | GET | Get session details |
| `/v1/sessions/{id}` | DELETE | Delete session |

---

### GET /v1/memory/search

**Semantic Memory Search** - Search across all session memories.

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `q` | string | Yes | Search query |
| `limit` | integer | No | Max results (default: 5) |

#### Example

```bash
curl "http://localhost:8000/v1/memory/search?q=consciousness&limit=10"
```

---

## 👁️ Vision System Architecture

### OrbCloudVision Component Diagram

```mermaid
flowchart TB
    subgraph OrbCloudVision["OrbCloudVision Class"]
        direction TB
        
        subgraph Detection["Camera Detection"]
            WMI[WMI PnP Scan]
            OPENCV[OpenCV Probe<br/>Indices 0-10]
            PSEYEPY[pseyepy Scan<br/>Index 99]
        end
        
        subgraph Wrappers["Camera Wrappers"]
            CVW[cv2.VideoCapture]
            PSW[PSEyeWrapper]
        end
        
        subgraph Storage["Frame Storage"]
            CAPS["caps dict<br/>{idx: capture}"]
            META["hardware_metadata<br/>{idx: info}"]
            BUFFER["visual_buffer<br/>deque(maxlen=30)"]
        end
    end
    
    WMI --> Detection
    OPENCV --> CVW
    PSEYEPY --> PSW
    
    CVW --> CAPS
    PSW --> CAPS
    CAPS --> BUFFER

    style PSEYEPY fill:#e65100,color:#fff
    style PSW fill:#e65100,color:#fff
```

### PSEyeWrapper Class

```python
class PSEyeWrapper:
    """Wraps pseyepy Camera to mimic cv2.VideoCapture interface."""
    
    def __init__(self, eye_cam):
        self.eye = eye_cam
        
    def read(self) -> Tuple[bool, np.ndarray]:
        """Returns (success, frame) tuple like cv2.VideoCapture."""
        result = self.eye.read()  # Returns (frame, timestamp)
        frame, timestamp = result
        if isinstance(frame, np.ndarray) and frame.size > 0:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return True, frame
        return False, None
```

---

## 🔧 Nexus Language Interpreter

### Command Flow

```mermaid
flowchart TD
    INPUT[Model Output] --> PARSE{Contains<br/>S-expression?}
    
    PARSE -->|No| OUTPUT[Return Text]
    PARSE -->|Yes| EXTRACT[Extract Command]
    
    EXTRACT --> EVAL{Evaluate}
    
    EVAL --> CMD1["(FILE-READ path)"]
    EVAL --> CMD2["(FILE-WRITE path content)"]
    EVAL --> CMD3["(SYS-STAT)"]
    EVAL --> CMD4["(MEMORY-SEARCH query)"]
    EVAL --> CMD5["(LOG message)"]
    
    CMD1 --> RESULT[Command Result]
    CMD2 --> RESULT
    CMD3 --> RESULT
    CMD4 --> RESULT
    CMD5 --> RESULT
    
    RESULT --> LOG[Nexus Logs]
    LOG --> OUTPUT

    style PARSE fill:#1976d2,color:#fff
    style EVAL fill:#7b1fa2,color:#fff
```

### Supported Commands

| Command | Description | Example |
|---------|-------------|---------|
| `(FILE-READ path)` | Read file contents | `(FILE-READ "config.json")` |
| `(FILE-WRITE path content)` | Write to file | `(FILE-WRITE "log.txt" "Hello")` |
| `(SYS-STAT)` | System status | `(SYS-STAT)` |
| `(MEMORY-SEARCH query)` | Search memory | `(MEMORY-SEARCH "topic")` |
| `(LOG message)` | Log message | `(LOG "Processing")` |

---

## 🔌 Sensory Hot-Swap System

### State Machine

```mermaid
stateDiagram-v2
    [*] --> OFFLINE: System Boot
    
    OFFLINE --> SCANNING: detect_hardware()
    SCANNING --> ACTIVE: Hardware Found
    SCANNING --> OFFLINE: No Hardware
    
    ACTIVE --> DEGRADED: Partial Failure
    ACTIVE --> OFFLINE: Full Disconnect
    
    DEGRADED --> ACTIVE: Recovery
    DEGRADED --> OFFLINE: Total Failure
    
    ACTIVE --> ACTIVE: Hot-Swap Event
    
    note right of ACTIVE
        Hardware operational
        Streaming active
    end note
    
    note right of DEGRADED
        Some cameras offline
        Fallback active
    end note
```

---

## 🖥️ Frontend Architecture

### React Component Hierarchy

```mermaid
flowchart TB
    subgraph App["App.jsx"]
        direction TB
        
        subgraph Header["Header Section"]
            TITLE[Title]
            STATUS[Connection Status]
        end
        
        subgraph Main["Main Content"]
            direction LR
            
            subgraph Left["Left Panel"]
                SESSIONS[Session List]
                DEVICES[Device Selectors]
            end
            
            subgraph Center["Center Panel"]
                CHAT[Chat Messages]
                INPUT[Message Input]
            end
            
            subgraph Right["Right Panel"]
                VISION[Vision Layer]
                MONITORS[System Monitors]
                LOGS[Nexus Logs]
            end
        end
    end

    style VISION fill:#e65100,color:#fff
    style CHAT fill:#1976d2,color:#fff
```

### Data Flow

```mermaid
flowchart LR
    subgraph State["React State"]
        MSG[messages]
        SID[sessionId]
        CAM[selectedCamera]
        MIC[selectedMic]
    end
    
    subgraph API["API Calls"]
        PROC[POST /v1/process]
        HW[GET /v1/hardware]
        STREAM[GET /v1/vision/stream]
        SESS[/v1/sessions/*]
    end
    
    subgraph UI["UI Components"]
        CHAT[Chat Display]
        VIDEO[Video Feed]
        SELECT[Device Dropdowns]
    end
    
    MSG --> CHAT
    CAM --> VIDEO
    
    INPUT[User Input] --> PROC
    PROC --> MSG
    
    CAM -->|BRAIN camera| STREAM
    STREAM --> VIDEO
    
    HW --> SELECT

    style STREAM fill:#e65100,color:#fff
```

---

## 📊 Error Responses

All error responses follow this schema:

```json
{
  "detail": "Error message describing the issue"
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Request completed |
| 404 | Not Found | Session doesn't exist |
| 500 | Server Error | Processing failure |
| 503 | Unavailable | Triad not initialized |

---

## 🔗 Related Documentation

- [OpenAPI Specification](./openapi.yaml) - Full OpenAPI 3.1 spec
- [Vision System Architecture](../technical/VISION_SYSTEM_ARCHITECTURE.md)
- [Brain-Triad Design](../architecture/BRAIN_TRIAD_DESIGN.md)
- [PS Eye Integration Guide](../hardware/PS_EYE_INTEGRATION_GUIDE.md)

---

## 📜 Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-25 | Initial release with PS Eye support |