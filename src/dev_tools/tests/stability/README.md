# ImpressionCore Long-term Stability Testing

This directory contains tools and utilities for performing long-term stability testing, memory leak detection, and stress testing for ImpressionCore visualization components.

## Overview

The stability testing framework is designed to:

1. Detect memory leaks in visualization components
2. Test long-term stability of components under continuous usage
3. Perform stress testing under high load and with limited resources
4. Generate detailed reports on stability, performance, and memory usage

All tools are optimized to work with limited VRAM systems (target: 4GB NVIDIA GTX 1050 Ti).

## Components

The stability testing suite includes:

- **Long-term Stability Testing**: Runs components continuously to detect stability issues
- **Memory Leak Detection**: Specifically designed to identify memory leaks in visualization components
- **Stress Testing**: Tests components under progressively increasing load until failure
- **Test Runner**: Command-line tool to run different types of tests

## Usage

### Running Stability Tests

To run stability tests:

```bash
python run_stability_tests.py stability --test-type [architecture|activation|stress|all] --duration 30
```

Options:
- `--test-type`: Type of stability test to run
- `--duration`: Duration of test in minutes

### Running Memory Leak Detection

To run memory leak detection:

```bash
python run_stability_tests.py leak --component [architecture|activation|all] --iterations 20
```

Options:
- `--component`: Component to test for memory leaks
- `--iterations`: Number of iterations for leak detection

### Running Stress Tests

To run stress tests:

```bash
python run_stability_tests.py stress --stress-type [architecture|activation|parallel|progressive|all] --complexity [low|medium|high] --iterations 10
```

Options:
- `--stress-type`: Type of stress test to run
- `--complexity`: Complexity level for models
- `--iterations`: Number of iterations for component tests

### Individual Test Modules

You can also run the individual test modules directly:

```bash
# Run stability test
python stability_test.py --test-type all --duration 30

# Run memory leak detection
python memory_leak_detector.py architecture 20

# Run stress test
python stress_test.py --test-type all --complexity medium
```

## Test Types

### Stability Tests

Stability tests run components continuously for an extended period to detect:
- Memory leaks over time
- Performance degradation
- Stability issues with repeated use

### Memory Leak Tests

Memory leak tests specifically focus on detecting memory leaks:
- Track RAM and VRAM usage during component execution
- Identify leaked Python objects
- Generate detailed leak reports with source information

### Stress Tests

Stress tests focus on component behavior under high load:
- Architecture visualization stress test: Tests model architecture visualization
- Activation visualization stress test: Tests layer activation visualization
- Parallel stress test: Tests multiple visualizations running in parallel
- Progressive load test: Increases load until failure to determine safe limits

## Reports and Outputs

All tests generate reports that include:
- Detailed test results
- Memory usage statistics
- Performance metrics
- System recommendations
- Hardware information

Reports are saved to timestamped directories for easy reference.

## Requirements

- Python 3.8+
- PyTorch
- NumPy
- Matplotlib
- psutil
- tracemalloc (built into Python 3.6+)
- ImpressionCore visualization components

## Hardware Considerations

The stability testing framework is designed with the target hardware requirements in mind:
- NVIDIA GTX 1050 Ti with 4GB VRAM
- Intel Core i5 4460 @ 3.20GHz
- 32GB DDR3 RAM

Tests automatically adapt to available resources and can run on systems without CUDA support.

## Extending the Framework

To add new test types:
1. Create a new test class in the appropriate module
2. Implement the required test methods
3. Update the test runner to include the new test type

## Troubleshooting

If you encounter issues:

- Check the log files for detailed error information
- Ensure visualization components are available and imported correctly
- Verify that system requirements are met
- For CUDA out-of-memory errors, try reducing model complexity or batch size
