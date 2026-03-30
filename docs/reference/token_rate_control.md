# Token Rate Control

**Created:** March 15, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\token_rate_control.md #documentation #inference #transformer  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# Token Rate Control System

The token rate control system ensures that token generation adheres to a specified rate limit, preventing overuse of resources and maintaining system stability.

## Features

- **Rate Limiting**: Enforces a maximum token generation rate (default: 35,000 tokens per minute).
- **Continuous Monitoring**: Tracks token usage and adjusts generation speed dynamically.
- **Queueing**: Pauses generation and waits until sufficient tokens are available.
- **Error Handling**: Logs warnings when token requests exceed the available budget.

## Usage

### Initialization

The `TokenRateController` can be initialized with a custom rate limit:

```python
from utils.token_rate_control import TokenRateController

controller = TokenRateController(rate_limit=35000)
```

### Checking Token Availability

Before generating tokens, check if the request can be fulfilled:

```python
if controller.can_generate(tokens_requested):
    # Proceed with generation
else:
    controller.wait_for_tokens(tokens_requested)
```

### Updating Token Usage

After generating tokens, update the usage:

```python
controller.update_token_usage(tokens_generated)
```

### Integration with Inference Pipeline

The `InferencePipeline` integrates the token rate control system to manage token generation for both text and image outputs. The system ensures that all requests comply with the rate limit.

```python
pipeline = InferencePipeline(transformer=transformer_model, diffusion_model=diffusion_model)
generated_text = pipeline.generate_text(prompt="Hello world", max_length=50)
```

## Configuration

- **Rate Limit**: The maximum number of tokens allowed per minute. Default: 35,000.
- **Window Seconds**: The time window for rate calculation. Default: 60 seconds.

## Error Handling

- **Exceeding Rate Limit**: If a request exceeds the available tokens, the system pauses and waits until enough tokens are available.
- **Logging**: All token usage and rate limit violations are logged for monitoring and debugging.

## Example

```python
from pipelines.inference import InferencePipeline

pipeline = InferencePipeline(transformer=transformer_model, diffusion_model=diffusion_model)

# Generate text
text = pipeline.generate_text(prompt="Generate a story", max_length=100)

# Generate image
image = pipeline.generate_image(prompt="A beautiful sunset", steps=50)
```
