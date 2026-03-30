# Trainer Compatibility

**Created:** March 04, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\TRAINER_COMPATIBILITY.md #api #docs\reference\trainer_compatibility.md #documentation #training  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# Trainer Compatibility Guide

This document provides guidance on working with different implementations of the DistillationTrainer class in ImpressionCore.

## Common Trainer Variations

Different versions or implementations of the DistillationTrainer may have different APIs and attributes. This guide helps you understand and adapt to these differences.

### Setting Training Steps

Depending on the implementation, you may need to set the number of training steps in different ways:

#### Method 1: Through config object before trainer initialization
