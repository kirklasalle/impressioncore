#!/usr/bin/env python3
"""
ImpressionCore Wiki — Static Site Generator
Converts all docs/*.md files into a navigable, searchable HTML wiki
with the ImpressionCore Cyberpunk theme.

Usage:
    python build_wiki.py              # Full build
    python build_wiki.py --serve      # Build + local HTTP server on port 8080
    python build_wiki.py --clean      # Remove site/ output before building
"""

import argparse
import html
import http.server
import json
import os
import re
import shutil
import threading
from pathlib import Path

# Third-party
import markdown
from jinja2 import Environment, FileSystemLoader
import yaml

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────
WIKI_DIR = Path(__file__).parent.resolve()
DOCS_DIR = WIKI_DIR.parent.resolve()          # docs/
PROJECT_ROOT = DOCS_DIR.parent.resolve()       # project root
TEMPLATE_DIR = WIKI_DIR / "templates"
STATIC_DIR = WIKI_DIR / "static"
SITE_DIR = WIKI_DIR / "site"

# ──────────────────────────────────────────────
# Category definitions
# ──────────────────────────────────────────────
CATEGORY_RULES = [
    {
        "slug": "constitutional",
        "name": "Constitutional & Governance",
        "icon": "🛡️",
        "description": "Foundational documents, permanent directives, ethics charters, and governance frameworks.",
        "patterns": [
            r"(?i)permanent.*directive", r"(?i)sacred.*covenant", r"(?i)fifth.*law",
            r"(?i)ai_ethics", r"(?i)constitutional", r"(?i)charter",
            r"(?i)COPILOT_PRIME", r"(?i)COPILOT_SACRED", r"(?i)prime_directive",
            r"(?i)compliance.*framework", r"(?i)governance",
        ],
    },
    {
        "slug": "architecture",
        "name": "Architecture",
        "icon": "🏛️",
        "description": "System architecture, design documents, brain-triad design, and architectural reviews.",
        "patterns": [
            r"(?i)^ARCHITECTURE", r"(?i)Architectural_Definitions",
            r"(?i)BRAIN_TRIAD", r"(?i)_ARCHITECTURAL_",
            r"(?i)ARCHITECTURE_REVIEW", r"(?i)architectural.*blueprint",
            r"(?i)cognitive_arch",
        ],
    },
    {
        "slug": "training",
        "name": "Training & Distillation",
        "icon": "🎓",
        "description": "Knowledge distillation pipelines, DPO alignment, training guides, and curriculum design.",
        "patterns": [
            r"(?i)distillation", r"(?i)training.*guide", r"(?i)training.*plan",
            r"(?i)dpo", r"(?i)curriculum", r"(?i)TRAINING_METHODOLOGY",
            r"(?i)hyperparameter", r"(?i)fine.?tun",
        ],
    },
    {
        "slug": "user-guides",
        "name": "User Guides",
        "icon": "📖",
        "description": "Getting started, walkthroughs, complete user guides, and onboarding materials.",
        "patterns": [
            r"(?i)user_guide", r"(?i)walkthrough", r"(?i)getting.?started",
            r"(?i)complete_user_guide", r"(?i)onboarding", r"(?i)quickstart",
        ],
    },
    {
        "slug": "api-reference",
        "name": "API Reference",
        "icon": "⚡",
        "description": "API documentation, endpoint specifications, OpenAPI definitions, and contracts.",
        "patterns": [
            r"(?i)api_reference", r"(?i)api_contracts", r"(?i)openapi",
            r"(?i)TRIAD_API", r"(?i)embedding.*api", r"(?i)endpoint",
        ],
    },
    {
        "slug": "memory-optimization",
        "name": "Memory & Optimization",
        "icon": "🧠",
        "description": "Memory management, GPU optimization, VRAM strategies, and performance tuning.",
        "patterns": [
            r"(?i)memory.*optim", r"(?i)memory.*efficient",
            r"(?i)gpu.*memory", r"(?i)GPU_SETUP", r"(?i)gpu.?optim",
            r"(?i)VRAM", r"(?i)hardware.*optim", r"(?i)profiling",
        ],
    },
    {
        "slug": "data-tokenization",
        "name": "Data & Tokenization",
        "icon": "🗃️",
        "description": "Dataset preparation, tokenization guides, data versioning, and preprocessing pipelines.",
        "patterns": [
            r"(?i)tokeniz", r"(?i)DATA_PREPARATION", r"(?i)dataset.*valid",
            r"(?i)data.*version", r"(?i)preprocessing",
            r"(?i)token_converter",
        ],
    },
    {
        "slug": "security",
        "name": "Security",
        "icon": "🔒",
        "description": "Security frameworks, compliance documentation, and safety requirements.",
        "patterns": [
            r"(?i)^security", r"(?i)compliance", r"(?i)safety.*require",
            r"(?i)quantum.*resist", r"(?i)cryptograph",
        ],
    },
    {
        "slug": "deployment",
        "name": "Deployment & DevOps",
        "icon": "🚀",
        "description": "Deployment guides, CI/CD pipelines, community deployment, and DevOps practices.",
        "patterns": [
            r"(?i)deploy", r"(?i)devops", r"(?i)ci.?cd",
            r"(?i)production.*package", r"(?i)release",
        ],
    },
    {
        "slug": "b-series",
        "name": "B-Series Evolution",
        "icon": "🔀",
        "description": "B1, B2, B3 architectural iterations — evolution of the ImpressionCore model series.",
        "patterns": [
            r"(?i)^B[123]_", r"(?i)B_SERIES", r"(?i)b1.*phase",
            r"(?i)b2.*phase", r"(?i)b3.*phase", r"(?i)ROLLOUT_PLAN",
        ],
    },
    {
        "slug": "analysis-reports",
        "name": "Analysis & Reports",
        "icon": "📊",
        "description": "Performance analysis, breakthrough reports, evaluation results, and session summaries.",
        "patterns": [
            r"(?i)analysis/", r"(?i)reports/", r"(?i)breakthrough",
            r"(?i)evaluation.*report", r"(?i)session.*report",
            r"(?i)HOPE.*phase", r"(?i)production.*recomm",
        ],
    },
    {
        "slug": "technical-reference",
        "name": "Technical Reference",
        "icon": "📋",
        "description": "Technical specifications, reference implementations, standards, and detailed specifications.",
        "patterns": [
            r"(?i)technical/", r"(?i)reference/", r"(?i)STANDARDS_OFFICIAL",
            r"(?i)specifications", r"(?i)PERMANENT.*FRAMEWORK",
        ],
    },
    {
        "slug": "troubleshooting",
        "name": "Troubleshooting",
        "icon": "⚠️",
        "description": "Error handling guides, troubleshooting steps, debugging tips, and known issues.",
        "patterns": [
            r"(?i)TROUBLESHOOT", r"(?i)error_handling",
            r"(?i)debugging", r"(?i)known.*issue",
        ],
    },
    {
        "slug": "archive",
        "name": "Archive",
        "icon": "📦",
        "description": "Archived documents, historical records, and deprecated content preserved for reference.",
        "patterns": [
            r"(?i)archive/", r"(?i)ARCHIVE_INDEX", r"(?i)_ARCHIVE_",
            r"(?i)deprecated", r"(?i)history/",
        ],
    },
]

# Files/dirs to exclude from the wiki
EXCLUDE_PATTERNS = [
    r"__pycache__",
    r"\.system_generated",
    r"\.pyc$",
    r"ids_index_snapshot_",
    r"ids_tags_snapshot_",
    r"lint_fix",
    r"standardization_run_",
    r"docs_header_dedup",
    r"docs_inventory\.json",
    r"documentation_enhancement_report",
    r"markdown_lint_fix",
    r"file_metadata\.yaml",
    r"code_index\.yaml",
    r"tags_index\.yaml",
    r"unified_tags_index\.yaml",
    r"reverse_tag_index\.yaml",
    r"bookmarks\.yaml",
    r"bookmarks_database\.yaml",
    r"_lightweight_index\.json",
    r"\.backup\.",
    r"wiki/",  # Don't process wiki itself
]

# ──────────────────────────────────────────────
# Markdown processor setup
# ──────────────────────────────────────────────
MD_EXTENSIONS = [
    "tables",
    "fenced_code",
    "toc",
    "meta",
    "codehilite",
    "attr_list",
    "admonition",
    "nl2br",
    "sane_lists",
]

MD_EXTENSION_CONFIGS = {
    "codehilite": {
        "css_class": "highlight",
        "guess_lang": True,
        "use_pygments": True,
    },
    "toc": {
        "permalink": False,
        "toc_depth": "2-4",
    },
}


def create_md_processor():
    return markdown.Markdown(
        extensions=MD_EXTENSIONS,
        extension_configs=MD_EXTENSION_CONFIGS,
    )


# ──────────────────────────────────────────────
# Utility functions
# ──────────────────────────────────────────────
def slugify(text: str, max_len: int = 80) -> str:
    """Convert text to a URL-safe slug, capped at max_len chars."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    if len(text) > max_len:
        text = text[:max_len].rsplit("-", 1)[0]
    return text or "untitled"


def should_exclude(rel_path: str) -> bool:
    """Check if a file should be excluded from the wiki."""
    for pat in EXCLUDE_PATTERNS:
        if re.search(pat, rel_path):
            return True
    return False


def classify_document(rel_path: str, title: str) -> str:
    """Assign a document to a category based on its path and title."""
    test_str = rel_path + " " + title
    for cat in CATEGORY_RULES:
        for pat in cat["patterns"]:
            if re.search(pat, test_str):
                return cat["slug"]
    return "uncategorized"


def extract_metadata(content: str, file_path: Path):
    """Extract IDS-style metadata from markdown content."""
    meta = {
        "title": None,
        "tags": [],
        "status": None,
        "updated": None,
        "created": None,
        "category_ids": None,
    }

    lines = content.split("\n")

    # Title: first H1
    for line in lines[:30]:
        m = re.match(r"^#\s+(.+)$", line)
        if m:
            # Strip bold markers and leading special chars
            title = m.group(1).strip().strip("*").strip("#").strip()
            if title and len(title) <= 200:
                meta["title"] = title
                break

    # Fallback title from filename
    if not meta["title"]:
        meta["title"] = file_path.stem.replace("_", " ").replace("-", " ").title()
        # Cap at 120 characters
        if len(meta["title"]) > 120:
            meta["title"] = meta["title"][:120].rsplit(" ", 1)[0]

    # Tags line: **Tags:** #tag1 #tag2
    for line in lines[:40]:
        m = re.match(r"\*\*Tags?:\*\*\s*(.+)", line, re.IGNORECASE)
        if m:
            meta["tags"] = [
                t.strip().lstrip("#").strip()
                for t in re.split(r"[,\s]+", m.group(1))
                if t.strip().lstrip("#").strip()
            ]
            break

    # Status
    for line in lines[:20]:
        m = re.match(r"\*\*Status:\*\*\s*(.+)", line, re.IGNORECASE)
        if m:
            meta["status"] = m.group(1).strip()
            break

    # Updated date
    for line in lines[:20]:
        m = re.match(r"\*\*Updated?:\*\*\s*(.+)", line, re.IGNORECASE)
        if m:
            meta["updated"] = m.group(1).strip()
            break

    # Created date
    for line in lines[:20]:
        m = re.match(r"\*\*Created?:\*\*\s*(.+)", line, re.IGNORECASE)
        if m:
            meta["created"] = m.group(1).strip()
            break

    return meta


def extract_toc_items(html_content: str):
    """Extract heading IDs and text for the right-side TOC."""
    items = []
    # Match <h2 id="...">text</h2> and <h3 id="...">text</h3>
    pattern = re.compile(r"<(h[234])\s+id=\"([^\"]+)\"[^>]*>(.*?)</\1>", re.IGNORECASE | re.DOTALL)
    for match in pattern.finditer(html_content):
        tag = match.group(1).lower()
        hid = match.group(2)
        # Strip HTML tags from heading text
        text = re.sub(r"<[^>]+>", "", match.group(3)).strip()
        if text:
            items.append({"tag": tag, "id": hid, "text": text})
    return items


def rewrite_links(html_content: str, doc_slug_map: dict, category_slug: str) -> str:
    """Rewrite internal .md links to .html wiki links."""

    def replacer(match):
        href = match.group(1)
        # Skip external, anchor-only, and non-md links
        if href.startswith(("http://", "https://", "mailto:", "#")):
            return match.group(0)
        if not href.endswith(".md") and ".md#" not in href:
            return match.group(0)

        # Split anchor
        parts = href.split("#", 1)
        md_path = parts[0]
        anchor = "#" + parts[1] if len(parts) > 1 else ""

        # Normalize the path
        basename = Path(md_path).stem
        slug = slugify(basename)

        if slug in doc_slug_map:
            cat_slug, doc_slug = doc_slug_map[slug]
            return match.group(0).replace(href, f"../{cat_slug}/{doc_slug}.html{anchor}")

        return match.group(0)

    return re.sub(r'href="([^"]+)"', replacer, html_content)


def generate_snippet(content: str, max_len: int = 300) -> str:
    """Generate a plain-text snippet for search index."""
    # Remove markdown headers, links, images, code blocks
    text = re.sub(r"```[\s\S]*?```", "", content)
    text = re.sub(r"`[^`]+`", "", text)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#{1,6}\s+.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"[|\-]{3,}", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_len:
        text = text[:max_len].rsplit(" ", 1)[0] + "…"
    return text


# ──────────────────────────────────────────────
# Main build pipeline
# ──────────────────────────────────────────────
def discover_documents():
    """Find all markdown files in docs/ that should be included."""
    documents = []
    for md_file in sorted(DOCS_DIR.rglob("*.md")):
        rel = md_file.relative_to(DOCS_DIR).as_posix()
        if should_exclude(rel):
            continue
        documents.append(md_file)
    return documents


def process_document(md_file: Path):
    """Process a single markdown file into a document dict."""
    rel_path = md_file.relative_to(DOCS_DIR).as_posix()

    try:
        content = md_file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    if not content.strip():
        return None

    meta = extract_metadata(content, md_file)
    slug = slugify(meta["title"] or md_file.stem)

    # Ensure unique slug
    category = classify_document(rel_path, meta["title"] or "")

    # Convert markdown to HTML
    md_proc = create_md_processor()
    html_content = md_proc.convert(content)

    # Add IDs to headings that don't have them
    def add_heading_ids(html_str):
        counter = {}

        def replacer(match):
            tag = match.group(1)
            attrs = match.group(2) or ""
            text = match.group(3)
            if 'id="' in attrs:
                return match.group(0)
            plain = re.sub(r"<[^>]+>", "", text).strip()
            hid = slugify(plain)
            if hid in counter:
                counter[hid] += 1
                hid = f"{hid}-{counter[hid]}"
            else:
                counter[hid] = 0
            return f"<{tag} id=\"{hid}\"{attrs}>{text}</{tag}>"

        return re.sub(
            r"<(h[2-6])(\s[^>]*)?>(.+?)</\1>",
            replacer,
            html_str,
            flags=re.IGNORECASE | re.DOTALL,
        )

    html_content = add_heading_ids(html_content)
    toc_items = extract_toc_items(html_content)
    snippet = generate_snippet(content)

    return {
        "title": meta["title"],
        "slug": slug,
        "tags": meta["tags"],
        "status": meta["status"],
        "updated": meta["updated"],
        "created": meta["created"],
        "category_slug": category,
        "source_path": rel_path,
        "html_content": html_content,
        "toc_items": toc_items,
        "snippet": snippet,
    }


def ensure_unique_slugs(docs: list) -> list:
    """Make sure all slugs are unique within their category."""
    seen = {}
    for doc in docs:
        key = f"{doc['category_slug']}/{doc['slug']}"
        if key in seen:
            seen[key] += 1
            doc["slug"] = f"{doc['slug']}-{seen[key]}"
        else:
            seen[key] = 0
    return docs


def build_categories(docs: list) -> list:
    """Organize documents into category structures."""
    cat_map = {}

    for cat in CATEGORY_RULES:
        cat_map[cat["slug"]] = {
            "slug": cat["slug"],
            "name": cat["name"],
            "icon": cat["icon"],
            "description": cat["description"],
            "docs": [],
            "doc_count": 0,
        }

    # Add uncategorized
    cat_map["uncategorized"] = {
        "slug": "uncategorized",
        "name": "Uncategorized",
        "icon": "📄",
        "description": "Documents that don't fit into a specific category.",
        "docs": [],
        "doc_count": 0,
    }

    for doc in docs:
        cat_slug = doc["category_slug"]
        if cat_slug not in cat_map:
            cat_slug = "uncategorized"
            doc["category_slug"] = cat_slug
        cat_map[cat_slug]["docs"].append(doc)

    # Sort docs within each category
    for cat in cat_map.values():
        cat["docs"].sort(key=lambda d: d["title"].lower())
        cat["doc_count"] = len(cat["docs"])

    # Return only categories that have documents
    categories = [cat for cat in cat_map.values() if cat["doc_count"] > 0]
    categories.sort(key=lambda c: (-c["doc_count"] if c["slug"] != "uncategorized" else 0, c["name"]))
    return categories


def build_slug_map(docs: list) -> dict:
    """Build a lookup: slug -> (category_slug, doc_slug) for link rewriting."""
    slug_map = {}
    for doc in docs:
        base_slug = slugify(Path(doc["source_path"]).stem)
        slug_map[base_slug] = (doc["category_slug"], doc["slug"])
        slug_map[doc["slug"]] = (doc["category_slug"], doc["slug"])
    return slug_map


def build_search_index(docs: list) -> list:
    """Generate the search-index.json data."""
    index = []
    for doc in docs:
        index.append({
            "title": doc["title"],
            "url": f"{doc['category_slug']}/{doc['slug']}.html",
            "source": doc["source_path"],
            "tags": doc["tags"],
            "snippet": doc["snippet"],
        })
    return index


def copy_assets():
    """Copy images and static assets to the site."""
    # Copy static/ (css, js)
    dest_static = SITE_DIR
    for subdir in ("css", "js"):
        src = STATIC_DIR / subdir
        dst = dest_static / subdir
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)

    # Copy docs/assets/ images
    assets_src = DOCS_DIR / "assets"
    assets_dst = SITE_DIR / "img"
    if assets_src.is_dir():
        shutil.copytree(assets_src, assets_dst, dirs_exist_ok=True)

    # Copy any other image dirs
    for img_dir_name in ("diagrams", "images", "screenshots"):
        img_src = DOCS_DIR / img_dir_name
        if img_src.is_dir():
            shutil.copytree(img_src, SITE_DIR / "img" / img_dir_name, dirs_exist_ok=True)


def build_wiki():
    """Main build pipeline."""
    print("=" * 60)
    print("  ImpressionCore Wiki — Build")
    print("=" * 60)

    # Clean output
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True)

    # Set up Jinja2
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=False,
    )

    # Add truncate filter
    def truncate_filter(s, length=50, end="…"):
        s = str(s)
        return s[:length] + end if len(s) > length else s
    env.filters["truncate"] = truncate_filter

    # Discover and process documents
    print("\n[1/7] Discovering documents…")
    md_files = discover_documents()
    print(f"       Found {len(md_files)} markdown files")

    print("[2/7] Processing documents…")
    docs = []
    errors = []
    for mf in md_files:
        try:
            doc = process_document(mf)
            if doc:
                docs.append(doc)
        except Exception as e:
            errors.append(f"  ERROR: {mf.relative_to(DOCS_DIR)} — {e}")

    docs = ensure_unique_slugs(docs)
    print(f"       Processed {len(docs)} documents ({len(errors)} errors)")
    for err in errors[:10]:
        print(err)

    # Build categories
    print("[3/7] Building categories…")
    categories = build_categories(docs)
    slug_map = build_slug_map(docs)

    for cat in categories:
        print(f"       {cat['icon']} {cat['name']}: {cat['doc_count']} docs")

    # Collect all unique tags
    all_tags = set()
    for doc in docs:
        all_tags.update(doc["tags"])

    # Quick links for landing page
    quick_links = []
    for label, pattern in [
        ("Getting Started", r"(?i)getting.?started|complete_user_guide"),
        ("Architecture Overview", r"(?i)^ARCHITECTURE\.md$|ARCHITECTURE_REVIEW"),
        ("API Reference", r"(?i)complete_api_reference|api_reference"),
        ("Training Guide", r"(?i)B1_DISTILLATION_TRAINING_GUIDE"),
        ("GPU Setup", r"(?i)GPU_SETUP"),
        ("Troubleshooting", r"(?i)^TROUBLESHOOT"),
    ]:
        for doc in docs:
            if re.search(pattern, doc["source_path"]):
                quick_links.append({
                    "label": label,
                    "url": f"{doc['category_slug']}/{doc['slug']}.html",
                })
                break

    # Recent docs (sort by updated date or fallback to title)
    recent_docs = sorted(
        [d for d in docs if d.get("updated")],
        key=lambda d: d["updated"],
        reverse=True,
    )[:12]

    # Common template context
    base_ctx = {
        "categories": categories,
        "total_docs": len(docs),
        "total_tags": len(all_tags),
    }

    # Rewrite internal links in all docs
    print("[4/7] Rewriting internal links…")
    for doc in docs:
        doc["html_content"] = rewrite_links(doc["html_content"], slug_map, doc["category_slug"])

    # Render pages
    print("[5/7] Rendering pages…")

    # 5a. Landing page
    tpl_index = env.get_template("index.html")
    index_html = tpl_index.render(
        **base_ctx,
        root_path="",
        page_title="Home",
        active_category=None,
        active_page=None,
        quick_links=quick_links,
        recent_docs=recent_docs,
    )
    (SITE_DIR / "index.html").write_text(index_html, encoding="utf-8")

    # 5b. Search page
    tpl_search = env.get_template("search.html")
    search_html = tpl_search.render(
        **base_ctx,
        root_path="",
        active_category=None,
        active_page=None,
    )
    (SITE_DIR / "search.html").write_text(search_html, encoding="utf-8")

    # 5c. Category pages + document pages
    tpl_category = env.get_template("category.html")
    tpl_page = env.get_template("page.html")

    for cat in categories:
        cat_dir = SITE_DIR / cat["slug"]
        cat_dir.mkdir(parents=True, exist_ok=True)

        # Category tags
        cat_tags = set()
        for doc in cat["docs"]:
            cat_tags.update(doc["tags"])

        # Category index
        cat_html = tpl_category.render(
            **base_ctx,
            root_path="../",
            category=cat,
            category_tags=sorted(cat_tags),
            active_category=cat["slug"],
            active_page=None,
        )
        (cat_dir / "index.html").write_text(cat_html, encoding="utf-8")

        # Document pages
        for i, doc in enumerate(cat["docs"]):
            doc["category_name"] = cat["name"]

            prev_doc = cat["docs"][i - 1] if i > 0 else None
            next_doc = cat["docs"][i + 1] if i < len(cat["docs"]) - 1 else None

            page_html = tpl_page.render(
                **base_ctx,
                root_path="../",
                doc=doc,
                toc_items=doc["toc_items"],
                prev_doc=prev_doc,
                next_doc=next_doc,
                tags=doc["tags"],
                active_category=cat["slug"],
                active_page=doc["slug"],
            )
            (cat_dir / f"{doc['slug']}.html").write_text(page_html, encoding="utf-8")

    # 5d. 404 page
    four04 = env.get_template("base.html")
    four04_html = four04.render(
        **base_ctx,
        root_path="",
        page_title="404 — Not Found",
        active_category=None,
        active_page=None,
    )
    # Inject 404 content
    four04_html = four04_html.replace(
        "{% block content %}{% endblock %}",
        ""
    )
    # Write a simple 404
    four04_content = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>404 — ImpressionCore Wiki</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/cyberpunk.css">
</head><body>
<div style="min-height:100vh;display:flex;align-items:center;justify-content:center">
<div class="page-404">
<div class="code-404 gradient-text">404</div>
<h2>Page Not Found</h2>
<p>The document you're looking for doesn't exist or has been moved.</p>
<a href="index.html" class="btn btn-primary" style="margin-top:16px">← Back to Home</a>
</div></div>
<script src="js/nav.js"></script>
</body></html>"""
    (SITE_DIR / "404.html").write_text(four04_content, encoding="utf-8")

    print(f"       Rendered {len(docs) + len(categories) + 3} pages")

    # Copy assets
    print("[6/7] Copying static assets…")
    copy_assets()

    # Search index
    print("[7/7] Generating search index…")
    search_data = build_search_index(docs)
    (SITE_DIR / "search-index.json").write_text(
        json.dumps(search_data, indent=None, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"       Search index: {len(search_data)} entries")

    # Summary
    total_pages = len(docs) + len(categories) + 3  # index + search + 404
    site_size = sum(f.stat().st_size for f in SITE_DIR.rglob("*") if f.is_file())
    print(f"\n{'=' * 60}")
    print(f"  BUILD COMPLETE")
    print(f"  Output: {SITE_DIR}")
    print(f"  Pages:  {total_pages}")
    print(f"  Size:   {site_size / 1024 / 1024:.1f} MB")
    print(f"{'=' * 60}\n")
    return 0


def serve(port: int = 8080):
    """Start a simple HTTP server for preview."""
    os.chdir(str(SITE_DIR))

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Suppress request logging noise

        def do_GET(self):
            # Serve 404.html for missing files
            path = self.translate_path(self.path)
            if not os.path.exists(path) and not path.endswith("/"):
                self.path = "/404.html"
            super().do_GET()

    server = http.server.HTTPServer(("", port), QuietHandler)
    print(f"  Serving wiki at http://localhost:{port}")
    print(f"  Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="ImpressionCore Wiki — Static Site Generator")
    parser.add_argument("--serve", action="store_true", help="Build and start local HTTP server")
    parser.add_argument("--port", type=int, default=8080, help="Server port (default: 8080)")
    parser.add_argument("--clean", action="store_true", help="Clean output directory before building")
    args = parser.parse_args()

    if args.clean and SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
        print("  Cleaned site/ directory")

    rc = build_wiki()

    if args.serve and rc == 0:
        serve(args.port)

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
