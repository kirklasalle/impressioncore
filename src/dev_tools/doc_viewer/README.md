# ImpressionCore Documentation Viewer

A rich markdown viewer/editor for the ImpressionCore project, supporting project-wide doc browsing, tag-based navigation, and seamless editing.

## Features

- **Project-wide doc browser**: Browse and open any Markdown file in `docs/` and subdirectories
- **Navigation sidebar** showing document headings
- **Tag extraction and display**: View tags (from YAML frontmatter) for each doc
- **Tag filtering**: Filter project docs by tag using the filter bar
- **Toggle between edit and preview modes**
- **Syntax highlighting for markdown**
- **File open/save functionality**
- **Section navigation via the sidebar**
- **Keyboard shortcuts** for common actions

## Installation

1. Ensure Python 3.6+ is installed.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Troubleshooting

- If you see "ModuleNotFoundError: No module named 'PyQt5'", verify your virtual environment is activated and run:

   ```bash
   pip install -r requirements.txt
   ```

- If you encounter "No space left on device" errors when installing PyQt5:

   ```bash
   # Option 1: Change pip's temporary directory to a drive with more space
   pip install --cache-dir D:\temp --no-cache-dir -r requirements.txt
   
   # Option 2: Install just the markdown package and use the tkinter fallback
   pip install markdown
   ```

#### Disk Space Issues

PyQt5 requires approximately 200MB during installation. If disk space is limited:

1. Edit requirements.txt to comment out PyQt5 and uncomment a lighter alternative
2. Clean temporary directories to free up space:

   ```bash
   pip cache purge
   ```

3. Create a dedicated temp directory on a drive with sufficient space:

   ```bash
   mkdir D:\temp
   set TMPDIR=D:\temp
   pip install -r requirements.txt
   ```

## Usage

### Project-wide browsing

Run the application in project browsing mode:

```bash
python markdown_viewer.py --browse
```

- Browse all Markdown docs in the project (docs/ and subdirectories)
- Filter docs by tags (from YAML frontmatter)
- Click a doc to open, edit, and navigate its sections

### Single file mode

```bash
python markdown_viewer.py <path-to-markdown-file>
```

- Click "Open File" to load a markdown document
- Use the navigation tree on the left to jump to different sections
- Toggle between edit and preview modes using the button
- Make changes in the edit mode and save with "Save File"

## Keyboard Shortcuts

- **Ctrl+O**: Open file
- **Ctrl+S**: Save file
- **F5**: Toggle between edit and preview modes
- **Ctrl+F**: Find text in document
- **Ctrl+N**: New document
