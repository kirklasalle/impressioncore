# Agent0Core Knowledge Base

This directory stores knowledge for Agent0Core's RAG (Retrieval-Augmented Generation) system.

## Supported Formats

- Markdown (`.md`)
- Text (`.txt`)
- PDF (`.pdf`) 
- JSON (`.json`)

## Organization

Organize knowledge by topic:

```
knowledge/
├── impressioncore_docs/    # Indexed project documentation
├── training_guides/        # B3 training knowledge
├── hardware_manuals/       # Kinect, PS Eye documentation
└── custom/                 # User-uploaded knowledge
```

## Auto-Indexing

Files placed here are automatically:
1. Parsed and chunked
2. Embedded using ImpressionCore's vector index
3. Made available to agents for retrieval

## Privacy

All knowledge stays local. Nothing is sent to external services.
