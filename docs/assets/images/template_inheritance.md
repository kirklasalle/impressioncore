# Template Inheritance Diagram

**Created:** June 03, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\assets\images\template_inheritance.md #deployment #documentation #training #web_interface  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

```mermaid
graph TD
    BASE[base.html<br/>Main Template] --> INDEX[index.html<br/>Dashboard]
    BASE --> WALK[walkthrough.html<br/>Onboarding]
    BASE --> TRAIN[training.html<br/>Training Interface]
    BASE --> EVAL[evaluation.html<br/>Evaluation Interface]
    BASE --> DEPLOY[deployment.html<br/>Deployment Interface]
    BASE --> CONFIG[configuration/*.html<br/>Config Templates]
    BASE --> METRICS[metrics/*.html<br/>Metrics Templates]
    BASE --> VIZ[visualization/*.html<br/>Visualization Templates]
    BASE --> ERRORS[Error Pages<br/>400.html, 404.html, etc.]
    
    classDef baseTemplate fill:#ff9999,stroke:#333,stroke-width:3px
    classDef mainTemplates fill:#99ccff,stroke:#333,stroke-width:2px
    classDef subTemplates fill:#99ff99,stroke:#333,stroke-width:1px
    classDef errorTemplates fill:#ffcc99,stroke:#333,stroke-width:1px
    
    class BASE baseTemplate
    class INDEX,WALK,TRAIN,EVAL,DEPLOY mainTemplates
    class CONFIG,METRICS,VIZ subTemplates
    class ERRORS errorTemplates
```

This diagram shows how all templates inherit from the base template, ensuring consistent styling and structure across the entire web interface.
