# System Oversight Module

**Created:** May 31, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\technical\system_oversight_module.md #api #command_line #documentation #gpu_optimization #memory_management #testing  
**Category:** Technical Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

Last updated: 2025-05-31
Responsible: @GitHubCopilot
---

# System Oversight Module

## 1. Introduction

### 1.1. Purpose

The System Oversight Module (`src/services/system_oversight.py`) is a critical component of the ImpressionCore framework, designed to monitor system health, manage resources, and ensure operational stability, especially within memory-constrained environments like the target NVIDIA GTX 1050 Ti (4GB VRAM). It provides mechanisms for health checks, anomaly detection, adaptive memory management, and component status tracking.

### 1.2. Key Functionalities

- Real-time monitoring of system resources (CPU, RAM, VRAM).
- Health status tracking for registered software components.
- Anomaly detection and recording.
- Adaptive memory management to prevent Out-Of-Memory (OOM) errors by triggering mitigation actions.
- Centralized logging for oversight activities.

### 1.3. API Endpoints

The System Oversight Module's functionalities are exposed via the following API endpoints (defined in `docs/api/complete_api_reference.md` and `docs/api/api_contracts.md`):

- **GET `/api/v1/system/memory_metrics`**: Retrieves current system-wide memory metrics.
    - Response Schema: `SystemMemoryMetrics`
- **POST `/api/v1/system/trigger_mitigation`**: Manually triggers a specific memory mitigation strategy.
    - Request Schema: `TriggerMitigationRequest`
- **GET `/api/v1/system/health_status`**: Retrieves overall system health status and recent anomalies.
    - Response Schema: `SystemHealthStatusResponse`

## 2. Core Components and Classes

### 2.1. `SystemState`

This class encapsulates the overall state of the system being monitored.

- **Attributes:**
  - `memory_usage (Dict[str, float])`: Stores current VRAM, RAM, and swap usage and totals.
  - `active_components (List[str])`: List of IDs of registered components.
  - `last_health_check (datetime)`: Timestamp of the last comprehensive health check.
  - `anomalies (List[Dict[str, Any]])`: A log of detected anomalies (stores the last 100).

### 2.2. `ComponentStatus`

Represents the state of an individual registered component.

- **Attributes:**
  - `id (str)`: Unique identifier for the component.
  - `name (str)`: Human-readable name of the component.
  - `status (str)`: Current operational status (e.g., 'ONLINE', 'DEGRADED', 'OFFLINE').
  - `last_checked (datetime)`: Timestamp of the last health check for this component.
  - `memory_footprint_mb (float)`: Estimated memory usage of the component.
  - `health_score (float)`: A score from 0-100 representing component health.

### 2.3. `SystemOversightService`

The main service class that orchestrates all oversight activities.

- **Key Methods:**
  - `async initialize()`: Initializes the service and registers default components (e.g., 'digital-identity', 'memory-optimizer', 'token-processor'). This should be called once at application startup.
  - `register_component(id: str, name: str) -> ComponentStatus`: Registers a new software component for monitoring.
  - `async update_memory_metrics() -> Dict[str, float]`: Retrieves/simulates current system memory usage (VRAM, RAM). Records an anomaly if VRAM usage is critically high.
  - `async run_system_health_check()`: Performs a comprehensive health check by updating memory metrics and checking the health of all registered components.
  - `async check_component_health(component_id: str) -> ComponentStatus`: Simulates/performs a health check for a specific component. Updates its status and health score, and records an anomaly if health is poor.
  - `record_anomaly(component_id: str, severity: str, description: str, mitigation_applied: str = None)`: Logs a detected anomaly and adds it to the `SystemState`. Anomalies are logged with severity levels (LOW, MEDIUM, HIGH, CRITICAL).
  - `async get_system_health() -> Dict`: Returns a dictionary with current CPU usage (%), RAM usage (%), and GPU VRAM usage (%).
  - `async _get_gpu_vram_usage_windows() -> float`: (Windows specific) Uses `nvidia-smi` to fetch GPU VRAM usage percentage.

### 2.4. `async adaptive_memory_management(oversight_service_or_callback, on_mitigation_or_logger, custom_logger=None)`

A standalone asynchronous function crucial for dynamic resource management.

- **Purpose:** Monitors VRAM utilization. If it exceeds a threshold (e.g., 85%), it triggers a user-defined mitigation action.
- **Parameters:**
  - `oversight_service_or_callback`: Either an instance of `SystemOversightService` or, in a test pattern, the mitigation callback itself.
  - `on_mitigation_or_logger`: The asynchronous callback function to execute if mitigation is needed (e.g., `async def my_mitigation_handler(action_type: str)`) or, in a test pattern, a logger instance.
  - `custom_logger` (Optional): A specific logger to use.
- **Usage:** This function should be called before and after memory-intensive operations. The `on_mitigation` callback is responsible for implementing actual memory-saving strategies (e.g., reducing model precision, offloading data to CPU).

## 3. Integration Guide

### 3.1. Initialization

At the startup of your application (e.g., in `main.py`, `run_server.py`, or the beginning of a CLI script):

1. Create an instance of `SystemOversightService`.
2. Call `await system_oversight_service.initialize()`.

```python
# Example:
import asyncio
from src.services.system_oversight import SystemOversightService

async def main_application_startup():
    oversight_service = SystemOversightService()
    await oversight_service.initialize()
    # ... rest of your application startup
    return oversight_service

# In your main entry point:
# oversight_service = asyncio.run(main_application_startup())
```

### 3.2. Registering Custom Components

If your application has specific components that need monitoring:

```python
# oversight_service is an initialized SystemOversightService instance
oversight_service.register_component("my_custom_module", "My Custom Processing Module")
```

### 3.3. Periodic Health Checks (Optional)

For long-running applications, you might want to run health checks periodically:

```python
# oversight_service is an initialized SystemOversightService instance
# async def periodic_checker(oversight_service):
#     while True:
#         await asyncio.sleep(300) # Check every 5 minutes
#         await oversight_service.run_system_health_check()

# asyncio.create_task(periodic_checker(oversight_service))
```

*(Note: The periodic check loop is commented out in `system_oversight.py` but can be implemented as shown above.)*

### 3.4. Adaptive Memory Management

Wrap memory-intensive operations with calls to `adaptive_memory_management`.

1. Define a mitigation handler function.
2. Call `adaptive_memory_management` before and potentially after the operation.

```python
from src.services.system_oversight import adaptive_memory_management, logger # or your custom logger

# oversight_service is an initialized SystemOversightService instance

async def example_mitigation_handler(action_type: str):
    logger.warn(f"Mitigation action triggered: {action_type}")
    if action_type == 'reduce_precision_or_offload':
        # Implement logic to reduce model precision, offload tensors to CPU, etc.
        logger.info("Attempting to reduce precision or offload to CPU...")
        # Example: my_model.half() or my_tensor.to('cpu')
        pass

async def perform_heavy_computation(data):
    # Before operation
    await adaptive_memory_management(oversight_service, example_mitigation_handler)
    
    logger.info("Starting heavy computation...")
    # ... your memory-intensive code ...
    result = data * 2 # Placeholder
    logger.info("Heavy computation finished.")
    
    # Optionally, check again after operation if it might have freed memory
    # await adaptive_memory_management(oversight_service, example_mitigation_handler)
    return result

# Usage:
# await perform_heavy_computation(my_data)
```

### 3.5. Manual Anomaly Reporting

If other parts of your system detect issues, they can report them via the oversight service:

```python
# oversight_service is an initialized SystemOversightService instance
oversight_service.record_anomaly(
    component_id='data_pipeline',
    severity='MEDIUM',
    description='Unexpected data format encountered.',
    mitigation_applied='Skipped problematic record.'
)
```

## 4. Logging

The module uses the `default_logger` from `src/utils/logger`. All significant events, health statuses, and anomalies are logged, providing a detailed trail for debugging and monitoring.

## 5. Configuration

Currently, the module has minimal external configuration. Thresholds (like VRAM > 85% for `adaptive_memory_management`) are hardcoded but could be externalized if needed. The target hardware (GTX 1050 Ti 4GB, 32GB RAM) is implicitly configured in some default values in `SystemState`.

## 6. Extensibility

- **New Components:** Easily register new components for monitoring.
- **Custom Health Checks:** The `check_component_health` method currently simulates checks. It can be modified to perform actual health assessments based on component-specific logic or APIs.
- **Mitigation Strategies:** The `adaptive_memory_management` function relies on a flexible callback, allowing diverse and sophisticated mitigation techniques to be implemented.

## 7. Considerations for GTX 1050 Ti

The module is designed with the GTX 1050 Ti's 4GB VRAM limit in mind.

- `_get_gpu_vram_usage_windows()` specifically targets NVIDIA GPUs.
- `adaptive_memory_management` is critical for staying within VRAM limits.
- Default VRAM total in `SystemState` is set to 4.0 GB.

This module is fundamental to maintaining the stability and performance of ImpressionCore on its target hardware.

## 8. Testing

The `SystemOversightService` and the `adaptive_memory_management` function are tested in `src/tests/services/test_system_oversight.py`.

Key test scenarios include:

- Basic system health checks under normal and mocked conditions.
- `adaptive_memory_management`:
  - Verification that mitigation is NOT triggered when VRAM usage is below the threshold.
  - Verification that mitigation IS triggered when VRAM usage is above the threshold.
  - Correct invocation of the `on_mitigation` callback.
  - Correct logging of events and anomalies.
- Graceful handling of errors during health checks (e.g., GPU VRAM check failures).
- Correct parsing of `nvidia-smi` output on Windows.

Testing `adaptive_memory_management` involves:

1. A `SystemOversightService` instance.
2. An `AsyncMock` for the `on_mitigation` callback.
3. Patching the `get_system_health` method of the `SystemOversightService` instance to return controlled VRAM usage percentages, simulating different system states.
4. Asserting that the `on_mitigation` callback is called (or not called) appropriately.
5. Asserting that the correct log messages (e.g., warnings for high VRAM, info for normal VRAM) are generated via a mocked logger.
6. Asserting that `record_anomaly` is called on the service instance when mitigation is triggered.

This approach ensures that the standalone `adaptive_memory_management` function's logic is tested in conjunction with the service it relies on for health data.

## 9. Considerations for GTX 1050 Ti

The module is designed with the GTX 1050 Ti's 4GB VRAM limit in mind.

- `_get_gpu_vram_usage_windows()` specifically targets NVIDIA GPUs.
- `adaptive_memory_management` is critical for staying within VRAM limits.
- Default VRAM total in `SystemState` is set to 4.0 GB.

This module is fundamental to maintaining the stability and performance of ImpressionCore on its target hardware.
