# Agent0Core Instruments

This directory stores custom instruments for Agent0Core.

## What are Instruments?

Instruments are reusable scripts stored in long-term memory that extend agent capabilities. Unlike tools (which are always loaded), instruments are recalled on-demand when needed, saving memory.

## Structure

Each instrument should be in its own directory:

```
instruments/
├── my_instrument/
│   ├── description.md   # What this instrument does
│   ├── run.sh           # Shell implementation (optional)
│   └── run.py           # Python implementation (optional)
```

## Example

```markdown
<!-- instruments/code_review/description.md -->

# Code Review Instrument

Reviews code for:
- Style compliance
- Security issues
- Performance problems
- Documentation gaps

Usage: Called when agent needs to review code quality.
```

## Prime Directive Compliance

All instruments must comply with the 7 Laws. The governance layer validates instrument actions before execution.
