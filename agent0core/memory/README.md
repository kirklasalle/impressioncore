# Agent0Core Memory Storage

This directory stores persistent memory for Agent0Core agents.

## Structure

```
memory/
├── agent_0/           # Primary agent memory
│   └── fragments.json
├── agent_1/           # Subordinate 1 memory
│   └── fragments.json
└── shared/            # Shared across all agents
    └── fragments.json
```

## Memory Types

- **conversation**: Chat history fragments
- **solution**: Problem-solution pairs
- **fact**: Learned facts
- **instruction**: Behavioral instructions

## Privacy

All memory is stored locally. Never transmitted externally.

## Clearing Memory

To clear memory for an agent:

```python
from agent0core.core import MemoryManager

memory = MemoryManager(agent_id=0)
memory.clear()  # Clear all
memory.clear(memory_type="conversation")  # Clear only conversations
```
