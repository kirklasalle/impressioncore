# B2 Experiment Tracking Integration

**Created:** July 01, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\B2_EXPERIMENT_TRACKING.md #docs\b2_experiment_tracking.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Overview

This document describes the integration of experiment tracking tools into the B2 curriculum distillation pipeline for full reproducibility and auditability. **Weights & Biases (wandb)** is prioritized for its collaborative dashboards and real-time monitoring. MLflow is supported optionally.

## Features

- Logs all hyperparameters, metrics, artifacts, and checkpoints
- Supports Weights & Biases (wandb) as primary tracker
- Optional MLflow support for advanced users
- Enables dashboard visualization and experiment comparison

## Usage

1. Install dependencies:

   ```bash
   pip install wandb

   # (Optional) pip install mlflow

   ```

2. By default, wandb tracking is enabled. To disable, set the environment variable:

   ```bash
   export WANDB_DISABLED=1
   ```

3. All runs are grouped by teacher, curriculum stage, and timestamp.
4. View experiment dashboards at https://wandb.ai/ (login required).

## Implementation Notes

- Tracking is initialized at the start of each run.
- All key metrics and artifacts (including best checkpoints) are logged automatically.
- See code comments for details and configuration options.

## Status

- [x] Initial integration planned
- [x] Implementation in progress
- [ ] Complete

---
Last updated: 2025-07-01. Responsible: GitHub Copilot
