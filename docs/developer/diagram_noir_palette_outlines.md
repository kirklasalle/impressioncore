# Diagram Noir Palette Outlines

**Created:** June 04, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\developer\diagram_noir_palette_outlines.md #documentation  
**Category:** Developer Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

Last updated: 2025-06-04
Responsible: @GitHubCopilot
---

# ImpressionCore Noir Palette: Outlined Node Styles Example

## Purpose

This example demonstrates how to use the Noir palette with colored outlines for node emphasis. Each color represents a different type of significance or annotation in ImpressionCore diagrams.

---

## Available Outline Colors & Their Representations

- **Blue (`#1976d2`)**: Data flow, input, or trusted source
- **Green (`#388e3c`)**: Processing, validation, or success
- **Red (`#d32f2f`)**: Error, alert, or critical
- **Amber (`#fbc02d`)**: Warning, caution, or special
- **Purple (`#8e24aa`)**: Cognitive/creative module
- **Cyan (`#00bcd4`)**: Communication, external interface
- **Pink (`#d81b60`)**: User interaction, feedback
- **Black (`#000000`)**: Default/neutral

---

## Example Advanced Noir Diagram with Outlined Nodes

```mermaid
flowchart TD
    subgraph Input["Input Modalities"]
        A1[Text]:::input
        A2[Image]:::input
        A3[Audio]:::input
    end
    subgraph Core["Core Processing"]
        B1[Encoder]:::process
        B2[Fusion Layer]:::fusion
        B3[Decoder]:::process
        B4[Validator]:::success
        B5[Alert Handler]:::error
        B6[Warning Filter]:::warning
        B7[Creative Engine]:::cognitive
        B8[Comm Module]:::comm
        B9[User Feedback]:::user
    end
    subgraph Output["Output Modalities"]
        C1[Text Output]:::output
        C2[Image Output]:::output
        C3[Audio Output]:::output
    end
    A1 --> B1
    A2 --> B1
    A3 --> B1
    B1 --> B2
    B2 --> B3
    B3 --> C1
    B3 --> C2
    B3 --> C3
    B2 --> B4
    B2 --> B5
    B2 --> B6
    B2 --> B7
    B2 --> B8
    B2 --> B9
    %% Outlined node styles
    classDef input fill:#ffffff,stroke:#000000,color:#000000
    classDef process fill:#f5f5f5,stroke:#000000,color:#000000
    classDef output fill:#ffffff,stroke:#000000,color:#000000
    classDef fusion fill:#f5f5f5,stroke:#1976d2,stroke-width:3px,color:#1976d2
    classDef success fill:#f5f5f5,stroke:#388e3c,stroke-width:3px,color:#388e3c
    classDef error fill:#ffffff,stroke:#d32f2f,stroke-width:3px,color:#d32f2f
    classDef warning fill:#ffffff,stroke:#fbc02d,stroke-width:3px,color:#fbc02d
    classDef cognitive fill:#ffffff,stroke:#8e24aa,stroke-width:3px,color:#8e24aa
    classDef comm fill:#ffffff,stroke:#00bcd4,stroke-width:3px,color:#00bcd4
    classDef user fill:#ffffff,stroke:#d81b60,stroke-width:3px,color:#d81b60
```

---

## Usage

- Use colored outlines for nodes to indicate their role or status.
- Always include a legend or color key for clarity.
- Keep text black for maximum readability.

---

**This example is the recommended template for advanced ImpressionCore Noir diagrams with outlined node significance.**
