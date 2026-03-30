# Template and Asset Flow Diagram

**Created:** June 03, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\assets\images\template_asset_flow.md #documentation #training  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

```mermaid
graph TD
    REQ[User Request] --> ROUTE[Flask Route Handler]
    ROUTE --> RENDER[render_template()]
    RENDER --> BASE[base.html Template]
    
    subgraph "Template Processing"
        BASE --> CHILD[Child Template<br/>e.g., training.html]
        CHILD --> BLOCKS[Template Blocks<br/>title, content, scripts]
        BLOCKS --> STATIC[Static Asset References<br/>url_for('static', ...)]
    end
    
    subgraph "Asset Loading"
        STATIC --> CSS[CSS Files<br/>style.css, custom.css]
        STATIC --> JS[JavaScript Files<br/>main.js, components.js]
        STATIC --> IMAGES[Image Assets<br/>logos, icons, charts]
        STATIC --> FONTS[Font Assets<br/>FontAwesome, custom fonts]
    end
    
    subgraph "Final Output"
        CSS --> RENDERED[Rendered HTML Page]
        JS --> RENDERED
        IMAGES --> RENDERED
        FONTS --> RENDERED
    end
    
    RENDERED --> BROWSER[Browser Display]
    
    classDef requestFlow fill:#ffe6e6,stroke:#333,stroke-width:2px
    classDef templateProc fill:#e6f3ff,stroke:#333,stroke-width:2px
    classDef assetLoad fill:#e6ffe6,stroke:#333,stroke-width:2px
    classDef finalOutput fill:#fff2e6,stroke:#333,stroke-width:2px
    
    class REQ,ROUTE,RENDER requestFlow
    class BASE,CHILD,BLOCKS,STATIC templateProc
    class CSS,JS,IMAGES,FONTS assetLoad
    class RENDERED,BROWSER finalOutput
```

This diagram illustrates the complete flow from user request to rendered page, showing how templates and assets are processed and combined.
