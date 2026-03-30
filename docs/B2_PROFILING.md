# B2 Profiling & Bottleneck Detection

**Created:** July 01, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\B2_PROFILING.md #docs\b2_profiling.md #documentation #memory_management #training  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Overview

This document covers the integration of automated profiling, live monitoring, and memory optimization in the B2 pipeline.

## Features

- Real-time profiling and VRAM tracking via ImpressionCoreLiveMonitor
- Memory and performance profiling (e.g., memory_profiler, torch.utils.bottleneck)
- Quantization-aware training and model pruning (configurable)
- Automatic logging of bottlenecks and VRAM usage to wandb and logs

## Usage

- Profiling and live monitoring are enabled by default in the B2 trainer
- Quantization and pruning can be toggled via config
- Review logs and wandb for bottleneck and memory stats

## Status

- [x] Design planned
- [x] Implementation in progress
- [ ] Complete

---
Last updated: 2025-07-01. Responsible: GitHub Copilot
