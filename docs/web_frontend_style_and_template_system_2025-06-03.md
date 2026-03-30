# ImpressionCore Web Frontend: Template, Style, and Asset System (2025-06-03)

**Created:** June 03, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\web_frontend_style_and_template_system_2025-06-03.md #command_line #deployment #docs\web_frontend_style_and_template_system_2025_06_03.md #documentation #testing #training #web_interface  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Overview

This document provides a comprehensive analysis of the ImpressionCore web frontend’s style, CSS, `base.html` management, and template file structure as of June 3, 2025. It is intended for developers and maintainers to understand, extend, and maintain the UI/UX system without breaking existing functionality.

---

## 1. Template System Architecture

### a. `base.html` (Master Layout)

- **Purpose:** Serves as the foundational template for all other HTML templates.
- **Features:**
  - Responsive layout using Bootstrap 5.3 and custom CSS.
  - Fixed sidebar navigation (`.sidebar`) for consistent navigation.
  - Main content area (`.main-container`, `.content`) for dynamic page content.
  - Loads FontAwesome for icons and includes both `style.css` and `custom.css`.
  - Provides blocks for `title`, `content`, and `scripts` for child templates to override.
- **Best Practice:** All templates should extend `base.html` using `{% extends "base.html" %}` to ensure consistent look and feel.

#### Diagram: Template Inheritance

See [Template Inheritance Diagram](assets/images/template_inheritance.md) for a visual representation of how all templates inherit from the base template.

The inheritance hierarchy ensures:

- Consistent styling and structure
- Shared navigation and footer
- Common CSS and JavaScript loading
- Unified error handling

---

### b. Template Directory Structure

- All templates are located in `src/web/templates/`.
- Subdirectories (e.g., `configuration/`, `metrics/`, `training/`, `visualization/`) group related templates for modularity.
- Common templates include:
  - `index.html` (home/dashboard)
  - `walkthrough.html` (interactive onboarding)
  - `training.html`, `evaluation.html`, `deployment.html`, etc.
  - Error pages: `400.html`, `404.html`, etc.

#### Advanced Diagram: Template and Asset Flow

See [Template and Asset Flow Diagram](assets/images/template_asset_flow.md) for a detailed view of how user requests are processed through the template system and how assets are loaded and combined to create the final rendered page.

This flow demonstrates:

- Request routing and template rendering
- Template inheritance and block processing
- Static asset loading and optimization
- Final HTML generation and browser delivery

---

## 2. CSS and Style Management

### a. CSS File Structure

- Located in `src/web/static/css/`:
  - `style.css`: General layout, utility classes, progress bars, form validation, WebSocket status, etc.
  - `custom.css`: Sidebar, navigation, main content, and ImpressionCore-specific branding.
  - Additional CSS for specialized pages (e.g., `terminal.css`, `evaluation.css`).
- All CSS is loaded via `<link>` tags in `base.html`.

### b. Style Principles

- **Responsive Design:** Uses Bootstrap grid and custom flexbox for layout.
- **Brand Consistency:** Colors, fonts, and spacing are unified across all pages.
- **Sidebar:** Fixed, dark-themed, with active link highlighting and icon support.
- **Main Content:** Light background, card-based sections, and clear separation of navigation/content.
- **Accessibility:** High-contrast text, large clickable areas, and semantic HTML.

#### Example: Sidebar and Content Layout

``` text
+---------------------+-----------------------------------+
|      Sidebar        |           Main Content            |
|  (fixed, dark)      |   (scrollable, light background)  |
+---------------------+-----------------------------------+
```

---

## 3. Template Extension and Best Practices

- All new templates **must** extend `base.html`.
- Use `{% block content %}` for main page content.
- Use `{% block scripts %}` for page-specific JavaScript.
- Place reusable components (navbars, cards, etc.) in partials or include files if needed.
- Keep page logic in Flask routes; templates should be presentational only.

---

## 4. Asset Management

- **Static files** (CSS, JS, images) are in `src/web/static/` and referenced via `url_for('static', filename=...)`.
- **Images**: Organized in `static/images/`, `static/img/`.
- **JS**: Page-specific scripts in `static/js/`.
- **Versioning:** Use cache-busting or versioned filenames for major updates.

---

## 5. Expansion and Maintenance

- When adding new features:
  - Create a new template in the appropriate subdirectory.
  - Extend `base.html` and use existing CSS classes for consistency.
  - Add new CSS only if necessary, and document it.
  - Update the documentation index and memlog with changes.
- When updating styles:
  - Test across all major templates to ensure no regressions.
  - Use browser dev tools to inspect and debug layout issues.

---

## 6. Diagrams: Advanced Asset Flow

``` text
[User Action]
   ↓
[Flask Route]
   ↓
[Template Render]
   ↓
[base.html]
   ↓
[Child Template]
   ↓
[Static CSS/JS]
   ↓
[Browser Render]
```

---

## 7. Summary Table: Key Files

| File/Dir                        | Purpose                                    |
|----------------------------------|--------------------------------------------|
| templates/base.html              | Master layout, sidebar, CSS includes        |
| templates/index.html             | Home/dashboard, extends base               |
| templates/walkthrough.html       | Interactive onboarding, extends base       |
| static/css/style.css             | General layout, utility classes            |
| static/css/custom.css            | Sidebar, branding, main content            |
| static/images/, static/img/      | Image assets                               |
| static/js/                       | JavaScript assets                          |

---

## 8. Recommendations

- Always extend `base.html` for new templates.
- Reuse existing CSS classes and layout patterns.
- Document all changes in the documentation index and memlog.
- Test UI on multiple devices and browsers.

---

## 9. References

- See `docs/DOCUMENTATION_INDEX.md` for up-to-date documentation links.
- For style and template changes, update `src/memlog/` with a summary and timestamp.

---

*Document generated by GitHub Copilot, 2025-06-03. For questions, contact the ImpressionCore maintainers.*
