```markdown
```mermaid
%% ImpressionCore-b1 Modular Functional Architecture (Professional)
flowchart TD
    %% Title
    title[ImpressionCore-b1 Modular Functional Architecture]
    style title fill:#f4f6fa,stroke:#222,stroke-width:3px,font-size:26px,font-weight:bold,color:#1a237e

    %% Input Encoders
    TextEncoder["<b style='color:#1565c0;font-size:18px;'>Text Encoder</b><br><span style='color:#333;font-size:14px;'>(128k context)</span>"]
    ImageEncoder["<b style='color:#1565c0;font-size:18px;'>Image Encoder</b>"]

    %% Core Components
    Fusion["<b style='color:#2e7d32;font-size:18px;'>Multimodal Fusion Layer</b>"]
    MoE["<b style='color:#2e7d32;font-size:18px;'>MoE Router</b>"]
    Experts["<b style='color:#2e7d32;font-size:18px;'>Experts</b><br><span style='color:#333;font-size:14px;'>1 2 3 4</span>"]
    GradCheckpoint["<b style='color:#2e7d32;font-size:18px;'>Gradient Checkpoint</b>"]
    OutputHead["<b style='color:#2e7d32;font-size:18px;'>Output Head</b>"]

    %% Hooks
    MemoryEfficient["<b style='color:#ef6c00;font-size:16px;'>Memory-Efficient<br>Attention</b>"]
    MixedPrecision["<b style='color:#ef6c00;font-size:16px;'>Mixed Precision<br>(FP16/BF16)</b>"]
    ShadowModel["<b style='color:#ef6c00;font-size:16px;'>Shadow Model<br>Sync</b>"]
    BrainHooks["<b style='color:#ef6c00;font-size:16px;'>Brain-Inspired<br>Hooks</b>"]

    %% Connections
    TextEncoder --> Fusion
    ImageEncoder --> Fusion
    Fusion --> MoE
    MoE --> Experts
    Experts --> GradCheckpoint
    GradCheckpoint --> OutputHead

    %% Hook Connections
    MemoryEfficient -.-> Fusion
    MixedPrecision -.-> GradCheckpoint
    ShadowModel -.-> OutputHead
    BrainHooks -.-> Fusion
    BrainHooks -.-> MoE

    %% Styling
    classDef input fill:#e3f2fd,stroke:#1565c0,stroke-width:3px,color:#1a237e,font-size:16px
    classDef core fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px,color:#1b5e20,font-size:16px
    classDef hooks fill:#fff3e0,stroke:#ef6c00,stroke-width:3px,color:#bf360c,font-size:15px
    classDef title fill:#f4f6fa,stroke:#222,stroke-width:3px,font-size:26px,font-weight:bold,color:#1a237e

    class TextEncoder,ImageEncoder input
    class Fusion,MoE,Experts,GradCheckpoint,OutputHead core
    class MemoryEfficient,MixedPrecision,ShadowModel,BrainHooks hooks
```

## Web Server and User Interface Integration (2025-04-19)

### Overview
ImpressionCore-b1 includes a modular web server and user interface designed to streamline model management, inference, and knowledge interaction. The web server is implemented in Flask with support for WebSockets, secure file uploads, and robust logging. The UI, built with Bootstrap, provides a chat interface and a knowledge management panel, serving as a guided walkthrough for users.

### Key Features
- **Model Management:**
  - Models are loaded from disk using PyTorch, with a global cache and thread lock for efficiency and thread safety.
  - The system supports multiple models and exposes endpoints for model metadata and management.
- **API & Routing:**
  - REST and WebSocket endpoints for chat, training, inference, and knowledge management.
  - Secure session and file handling, hardware validation, and integration with training and inference modules.
- **User Interface:**
  - Responsive, menu-driven UI with chat and knowledge management panels.
  - Users can interact with the LLM, add/query knowledge, and follow a guided workflow.

### Integration Points
- The web server interfaces directly with model loading, inference, and training modules in `/src`.
- The UI is designed to be extensible, supporting future steps such as data selection, model configuration, training progress, and evaluation.

### Gaps & Recommendations
- **Walkthrough Expansion:** The current menu system covers chat and knowledge management. It should be expanded to include:
  1. Data selection and upload
  2. Model configuration (architecture, memory settings)
  3. Training progress and controls
  4. Evaluation and benchmarking
  5. Model export and deployment
- **Documentation:**
  - Update API and UI documentation as new features are added.
  - Maintain a living document (see `docs/web_interface.md`) for technical details and user guidance.

### See Also
- [docs/web_interface.md](web_interface.md) for a detailed technical overview and actionable recommendations.

---
