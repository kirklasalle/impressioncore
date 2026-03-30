# Rule Engine API Guide

This guide explains how to correctly use the Rule Engine system in ImpressionCore.

## Core Components

### Context

The `Context` class represents the environment in which rules are evaluated. It stores properties that rules can access and stores inferred facts from rule application.

### Relationship-based Inferred Facts

The imported Context class uses a relationship model for inferred facts rather than a simple key-value model. The `add_inferred_fact` method creates relationships between nodes:

❌ Incorrect (key-value mental model):

## Common Pitfalls and Solutions

### Wrong Property Access

### Incorrect Context

## Step 5: Update API Documentation to Clarify Method Usage
