# ImpressionCore Wiki

A static documentation wiki for the ImpressionCore project, styled with the Cyberpunk theme from the Builder Client.

## Quick Start

```bash
# Install dependencies (from project root with .venv activated)
pip install -r docs/wiki/requirements.txt

# Build the wiki
python docs/wiki/build_wiki.py

# Build and preview locally
python docs/wiki/build_wiki.py --serve
```

The built site outputs to `docs/wiki/site/` and opens at `http://localhost:8080`.

## Architecture

docs/wiki/
├── build_wiki.py          # Python static site generator
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Master layout (sidebar + content + footer)
│   ├── page.html          # Single documentation page
│   ├── index.html         # Landing page with category grid
│   ├── category.html      # Category listing page
│   └── search.html        # Full-text search page
├── static/
│   ├── css/cyberpunk.css  # Complete Cyberpunk theme (vanilla CSS)
│   └── js/
│       ├── nav.js         # Sidebar, TOC scroll-spy, mobile menu
│       ├── search.js      # Client-side full-text search
│       └── theme.js       # Code copy, Mermaid diagrams, lightbox
├── site/                  # BUILD OUTPUT (gitignored)
├── requirements.txt       # Python dependencies
└── README.md              # This file

## Features

- **Cyberpunk Theme** — Dark navy background, neon cyan/indigo accents, Inter + JetBrains Mono fonts — matching the Builder Client
- **Automatic Categorization** — 14 categories auto-assigned from document paths, titles, and content patterns
- **Full-Text Search** — Client-side search with scored results, tag filtering (`tag:keyword`), and highlighted snippets
- **TOC Scroll-Spy** — Right-side table of contents with active heading tracking
- **Mermaid Diagrams** — Auto-rendered architecture diagrams from mermaid code blocks
- **Code Highlighting** — Pygments syntax highlighting with copy-to-clipboard buttons
- **Responsive** — Mobile hamburger menu, collapsible sidebar, full-width content on small screens
- **Image Lightbox** — Click-to-enlarge images with keyboard dismiss (Escape)
- **Print Stylesheet** — Clean white-background layout for printing
- **Internal Link Rewriting** — `.md` links automatically resolved to `.html` wiki pages

## CLI Options

| Flag | Description |
|------|-------------|
| `--serve` | Build and start a local HTTP server (default port 8080) |
| `--port N` | Set the server port (use with `--serve`) |
| `--clean` | Remove `site/` directory before building |

## Dependencies

- Python 3.10+
- `markdown` — Markdown to HTML conversion
- `Jinja2` — HTML templating
- `PyYAML` — YAML parsing (metadata)
- `Pygments` — Syntax highlighting for code blocks

## How It Works

1. **Discovery** — Scans `docs/` recursively for `.md` files, excluding metadata/system files
2. **Processing** — Extracts IDS metadata (title, tags, status, dates), converts markdown to HTML
3. **Categorization** — Assigns each doc to one of 14 categories via regex pattern matching
4. **Link Rewriting** — Resolves internal `.md` cross-references to wiki `.html` pages
5. **Rendering** — Generates HTML pages from Jinja2 templates with the Cyberpunk theme
6. **Search Index** — Builds `search-index.json` with titles, tags, and content snippets
7. **Assets** — Copies CSS, JS, and images from `docs/assets/` to the output site
