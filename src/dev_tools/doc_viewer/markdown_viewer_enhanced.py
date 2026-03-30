#!/usr/bin/env python3
"""
ImpressionCore: Enhanced Markdown Viewer

Module for enhanced markdown viewer functionality in the ImpressionCore framework.

File: tools\doc_viewer\markdown_viewer_enhanced.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-01-27
Modified: 2025-01-27
Version: 2.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [production, object-oriented, 2025, enhanced]
Dependencies: [typing, PyQt5, markdown]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements enhanced markdown viewer functionality for the
ImpressionCore brain-inspired multimodal AI framework. Features include
advanced search, syntax highlighting, multiple document tabs, auto-save,
and improved user experience.

Features:
- Multi-tab document editing
- Advanced search with background threading
- Syntax highlighting for markdown
- Auto-save functionality
- Recent files tracking
- Document outline navigation
- Tag-based filtering
- Export capabilities (HTML)
- Memory-efficient implementation
- Rich status bar with document statistics

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem
"""

import os
import sys
import os
import re
import json
import logging # Added
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add the project root to Python path to enable imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from doc_utils import find_markdown_files, extract_yaml_tags, build_doc_tree
from src.core.utils.rich_logging import setup_rich_logging
from src.core.utils.rich_status_animation import StatusAnimation

# Configure logging
logger = setup_rich_logging(__name__, level=logging.INFO)

# Try to import PyQt5, fall back to alternatives if not available
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QSplitter, QTreeWidget, QTreeWidgetItem, 
        QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QFileDialog, 
        QMessageBox, QShortcut, QAction, QLineEdit, QLabel, QComboBox, QCheckBox, 
        QProgressBar, QTabWidget, QMenuBar, QStatusBar, QSizePolicy, QScrollArea,
        QInputDialog, QDialog, QProgressDialog # Added QProgressDialog
    )
    from PyQt5.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal
    from PyQt5.QtGui import (
        QFont, QColor, QTextCharFormat, QTextCursor, QKeySequence, 
        QSyntaxHighlighter
    )
    from PyQt5.QtWebEngineWidgets import QWebEngineView  # Add at the top with other PyQt5 imports
    GUI_LIBRARY = "PyQt5"
except ImportError:
    try:
        # Try PySide2 as alternative
        from PySide2.QtWidgets import (
            QApplication, QMainWindow, QSplitter, QTreeWidget, QTreeWidgetItem,
            QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QFileDialog,
            QMessageBox, QShortcut, QAction, QLineEdit, QLabel, QComboBox, QCheckBox,
            QProgressBar, QTabWidget, QMenuBar, QStatusBar, QSizePolicy, QScrollArea,
            QInputDialog, QDialog, QProgressDialog # Added QProgressDialog
        )
        from PySide2.QtCore import Qt, QSize, QTimer, QThread, Signal as pyqtSignal
        from PySide2.QtGui import (
            QFont, QColor, QTextCharFormat, QTextCursor, QKeySequence, 
            QSyntaxHighlighter
        )
        GUI_LIBRARY = "PySide2"
    except ImportError:
        print("Error: Neither PyQt5 nor PySide2 is installed.")
        print("Please install one of these packages or use the tkinter fallback.")
        print("For installation help, see the README.md troubleshooting section.")
        sys.exit(1)

import markdown
from markdown.extensions.toc import TocExtension


class MarkdownSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for markdown text editor."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Header formats
        header_format = QTextCharFormat()
        header_format.setForeground(QColor("#2c3e50"))
        header_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((re.compile(r'^#{1,6}.*'), header_format))
        
        # Bold text
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((re.compile(r'\*\*(.*?)\*\*'), bold_format))
        
        # Italic text
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'\*(.*?)\*'), italic_format))
        
        # Code blocks
        code_format = QTextCharFormat()
        code_format.setForeground(QColor("#d73a49"))
        code_format.setFontFamily("Courier New")
        self.highlighting_rules.append((re.compile(r'`(.*?)`'), code_format))
        
        # Links
        link_format = QTextCharFormat()
        link_format.setForeground(QColor("#0366d6"))
        self.highlighting_rules.append((re.compile(r'\[([^\]]+)\]\([^)]+\)'), link_format))
    
    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)


class SearchThread(QThread):
    """Background thread for searching documents."""
    
    search_finished = pyqtSignal(list)
    search_progress = pyqtSignal(int, str) # Added for progress reporting

    def __init__(self, search_term: str, file_paths: List[str]):
        super().__init__()
        self.search_term = search_term.lower()
        self.file_paths = file_paths
        self.status_animation = None # Added

    def run(self):
        results = []
        total_files = len(self.file_paths)
        # Initialize StatusAnimation
        # Emitting a signal to the main thread to create/update StatusAnimation
        # is complex due to Rich's direct terminal interaction.
        # For now, we'll log progress and consider direct Rich integration later if feasible.
        logger.info(f"Starting search for '{self.search_term}' in {total_files} files.")

        for i, file_path in enumerate(self.file_paths):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        if self.search_term in line.lower():
                            results.append({
                                'file': file_path,
                                'line': line_num,
                                'text': line.strip(),
                                'context': self._get_context(lines, line_num - 1)
                            })
                # Emit progress
                self.search_progress.emit(int(((i + 1) / total_files) * 100), f"Searched {i+1}/{total_files} files")
            except Exception as e:
                logger.warning(f"Failed to search in {file_path}: {e}")
        
        logger.info(f"Search completed. Found {len(results)} results.")
        self.search_finished.emit(results)
    
    def _get_context(self, lines: List[str], line_index: int, context_size: int = 2) -> List[str]:
        """Get surrounding lines for context."""
        start = max(0, line_index - context_size)
        end = min(len(lines), line_index + context_size + 1)
        return lines[start:end]


class EnhancedMarkdownViewer(QMainWindow):
    """
    Enhanced MarkdownViewer class for ImpressionCore framework.
    
    This class implements advanced markdown viewer functionality optimized for
    memory-constrained environments like the GTX 1050 Ti.
    
    Features:
    - Advanced search with background threading
    - Syntax highlighting for markdown
    - Auto-save functionality
    - Recent files tracking
    - Document outline navigation
    - Tag-based filtering
    - Export capabilities
    - Memory-efficient implementation
    - Multi-tab document editing
    - Rich status bar with statistics
    
    Memory Considerations:
        - Implements memory-efficient algorithms
        - Lazy loading of documents
        - Cached search results
        - Optimized rendering
    """
    
    dark_editor_style = """
        QTextEdit {
            background-color: #232629;
            color: #e0e0e0;
            selection-background-color: #44475a;
            font-family: Consolas, 'Fira Mono', 'Menlo', monospace;
        }
    """
    light_editor_style = """
        QTextEdit {
            background-color: #fdfdfd;
            color: #232629;
            selection-background-color: #d0e6fa;
            font-family: Consolas, 'Fira Mono', 'Menlo', monospace;
        }
    """
    dark_html_css = """
        <style>
            body { background-color: #232629; color: #e0e0e0; }
            a { color: #8ab4f8; }
            code { background-color: #2d2d2d; color: #f8f8f2; }
            pre { background-color: #181a1b; color: #f8f8f2; }
            table { background-color: #232629; color: #e0e0e0; }
        </style>
    """
    light_html_css = """
        <style>
            body { background-color: #fdfdfd; color: #232629; }
            a { color: #3498db; }
            code { background-color: #ecf0f1; color: #e74c3c; }
            pre { background-color: #2d2d2d; color: #f8f8f2; }
            table { background-color: #fdfdfd; color: #232629; }
        </style>
    """
    
    def __init__(self, project_docs_root=None):
        """Initialize the enhanced markdown viewer.
        
        Args:
            project_docs_root: Optional path to project documentation root
        """
        super().__init__()
        self.theme = 'light'  # Ensure theme is set before any UI is built
        self.project_docs_root = project_docs_root
        self.doc_index = []
        self.doc_tree = {}
        self.current_file = None
        self.recent_files = self._load_recent_files()
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.search_thread = None
        self.settings_file = os.path.join(os.path.dirname(__file__), 'viewer_settings.json')
        
        # Initialize UI components
        self.init_ui()
        self.setup_menus()
        self.setup_shortcuts()
        self.setup_status_bar()
        
        # Load settings
        self._load_settings()
        
        # Set window properties
        self.setWindowTitle("ImpressionCore Enhanced Documentation Viewer")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Load project docs if specified
        if self.project_docs_root:
            self.load_project_docs()
        
        # Start auto-save timer (5 minutes)
        self.auto_save_timer.start(300000)
    
    def _load_recent_files(self) -> List[str]:
        """Load recent files from settings."""
        try:
            settings_file = os.path.join(os.path.dirname(__file__), 'recent_files.json')
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    return json.load(f).get('recent_files', [])
        except Exception as e:
            logger.warning(f"Failed to load recent files: {e}")
        return []
    
    def _save_recent_files(self):
        """Save recent files to settings."""
        try:
            settings_file = os.path.join(os.path.dirname(__file__), 'recent_files.json')
            with open(settings_file, 'w') as f:
                json.dump({'recent_files': self.recent_files}, f)
        except Exception as e:
            logger.warning(f"Failed to save recent files: {e}")
    
    def _add_recent_file(self, file_path: str):
        """Add file to recent files list."""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]  # Keep only 10 recent files
        self._save_recent_files()
        self._update_recent_files_menu()
    
    def _load_settings(self):
        """Load application settings."""
        try:
            import base64
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Apply settings
                    if 'window_geometry' in settings:
                        from PyQt5.QtCore import QByteArray
                        geometry = QByteArray.fromBase64(settings['window_geometry'].encode('utf-8'))
                        self.restoreGeometry(geometry)
                    if 'splitter_state' in settings:
                        from PyQt5.QtCore import QByteArray
                        splitter_state = QByteArray.fromBase64(settings['splitter_state'].encode('utf-8'))
                        self.splitter.restoreState(splitter_state)
                    if 'theme' in settings:
                        self.theme = settings['theme']
                        self.apply_theme()
        except Exception as e:
            logger.warning(f"Failed to load settings: {e}")
    
    def _save_settings(self):
        """Save application settings."""
        try:
            import base64
            settings = {
                'window_geometry': base64.b64encode(self.saveGeometry().data()).decode('utf-8'),
                'splitter_state': base64.b64encode(self.splitter.saveState().data()).decode('utf-8'),
                'last_directory': getattr(self, 'last_directory', ''),
                'theme': getattr(self, 'theme', 'light'),
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            logger.warning(f"Failed to save settings: {e}")
    
    def _auto_save(self):
        """Auto-save current document if modified."""
        current_tab = self.get_current_tab_data()
        if (current_tab and 
            current_tab.is_modified and 
            current_tab.file_path and 
            os.path.exists(current_tab.file_path)):
            try:
                with open(current_tab.file_path, 'w', encoding='utf-8') as f:
                    f.write(current_tab.editor.toPlainText())
                self.status_bar.showMessage("Auto-saved", 2000)
                logger.info(f"Auto-saved: {current_tab.file_path}")
            except Exception as e:
                logger.error(f"Auto-save failed: {e}")

    def init_ui(self):
        """Initialize the enhanced user interface."""
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Main splitter for resizable panels
        self.splitter = QSplitter(Qt.Horizontal)

        # Left panel - Project doc browser with search and filtering
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Search and filter controls
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files...")
        self.search_input.textChanged.connect(self.filter_project_docs)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        
        # Tag filter
        self.tag_filter = QComboBox()
        self.tag_filter.addItem("All Tags")
        self.tag_filter.currentTextChanged.connect(self.filter_by_tag)
        search_layout.addWidget(QLabel("Tag:"))
        search_layout.addWidget(self.tag_filter)
        
        left_layout.addLayout(search_layout)
        
        # Project doc tree
        self.doc_list = QTreeWidget()
        self.doc_list.setHeaderLabel("Project Docs")
        self.doc_list.setMinimumWidth(300)
        self.doc_list.itemClicked.connect(self.open_project_doc)
        self.doc_list.itemDoubleClicked.connect(self.open_project_doc)
        left_layout.addWidget(self.doc_list)

        # Middle panel - Tabbed navigation: Outline and Directory Tree
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)

        self.nav_tabs = QTabWidget()
        # Tab 1: Document Outline
        outline_widget = QWidget()
        outline_layout = QVBoxLayout(outline_widget)
        outline_layout.addWidget(QLabel("Document Outline"))
        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderLabel("Sections")
        self.nav_tree.setMinimumWidth(250)
        self.nav_tree.itemClicked.connect(self.navigate_to_section)
        outline_layout.addWidget(self.nav_tree)
        self.nav_tabs.addTab(outline_widget, "Outline")
        # Tab 2: Directory Tree & File List
        dir_widget = QWidget()
        dir_layout = QVBoxLayout(dir_widget)
        dir_layout.addWidget(QLabel("Project Docs"))
        self.dir_tree = QTreeWidget()
        self.dir_tree.setHeaderLabel("Project Docs")
        self.dir_tree.setMinimumWidth(250)
        self.dir_tree.itemClicked.connect(self.open_project_doc)
        self.dir_tree.itemDoubleClicked.connect(self.open_project_doc)
        dir_layout.addWidget(self.dir_tree)
        self.nav_tabs.addTab(dir_widget, "Files")
        middle_layout.addWidget(self.nav_tabs)

        # Right panel - Content area with tabs for multiple documents
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Toolbar for file operations
        toolbar_layout = QHBoxLayout()
        
        # File operations
        new_button = QPushButton("New")
        open_button = QPushButton("Open")
        save_button = QPushButton("Save")
        toggle_button = QPushButton("Edit/Preview")
        
        new_button.clicked.connect(self.new_document)
        open_button.clicked.connect(self.open_file)
        save_button.clicked.connect(self.save_file)
        toggle_button.clicked.connect(self.toggle_view)

        toolbar_layout.addWidget(new_button)
        toolbar_layout.addWidget(open_button)
        toolbar_layout.addWidget(save_button)
        toolbar_layout.addWidget(toggle_button)
        toolbar_layout.addStretch()

        # Document info
        self.doc_info_layout = QHBoxLayout()
        self.tag_label = QLabel("Tags: (none)")
        self.modified_label = QLabel("")
        self.doc_info_layout.addWidget(self.tag_label)
        self.doc_info_layout.addWidget(self.modified_label)
        self.doc_info_layout.addStretch()
        
        toolbar_layout.addLayout(self.doc_info_layout)

        # Tab widget for multiple documents
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # Create initial tab
        self.create_new_tab("Untitled")

        # Add widgets to layout
        right_layout.addLayout(toolbar_layout)
        right_layout.addWidget(self.tab_widget)

        # Add panels to splitter
        if self.project_docs_root:
            self.splitter.addWidget(left_panel)
        self.splitter.addWidget(middle_panel)
        self.splitter.addWidget(right_panel)

        # Set stretch factors for proper proportions
        if self.project_docs_root:
            self.splitter.setStretchFactor(0, 1)  # Project panel
            self.splitter.setStretchFactor(1, 1)  # Navigation panel
            self.splitter.setStretchFactor(2, 3)  # Content panel
        else:
            self.splitter.setStretchFactor(0, 1)  # Navigation panel
            self.splitter.setStretchFactor(1, 3)  # Content panel

        # Add splitter to main layout
        main_layout.addWidget(self.splitter)

        # Set main widget
        self.setCentralWidget(main_widget)

        # Initialize edit mode
        self.edit_mode = True

        # Populate doc list if in project mode
        if self.project_docs_root:
            self.populate_doc_list()
            self.populate_dir_tree()
    
    def create_new_tab(self, title: str, content: str = "") -> int:
        """
        Create a new tab with editor and preview. Adds a toggle for raw/rendered preview.
        """
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        
        # Formatting toolbar (NEW)
        formatting_toolbar = QHBoxLayout()
        bold_btn = QPushButton("Bold")
        italic_btn = QPushButton("Italic")
        code_btn = QPushButton("Code")
        link_btn = QPushButton("Link")
        heading_btn = QPushButton("Heading")
        
        formatting_toolbar.addWidget(bold_btn)
        formatting_toolbar.addWidget(italic_btn)
        formatting_toolbar.addWidget(code_btn)
        formatting_toolbar.addWidget(link_btn)
        formatting_toolbar.addWidget(heading_btn)
        formatting_toolbar.addStretch()
        
        # Preview toggle buttons
        preview_toggle_layout = QHBoxLayout()
        raw_btn = QPushButton("Raw Preview")
        rendered_btn = QPushButton("Rendered Preview")
        preview_toggle_layout.addWidget(raw_btn)
        preview_toggle_layout.addWidget(rendered_btn)
        preview_toggle_layout.addStretch()
        tab_layout.addLayout(preview_toggle_layout)
        
        # Content splitter for edit/preview
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Text editor with syntax highlighting
        editor = QTextEdit()
        editor.setFont(QFont("Consolas", 11))
        editor.setText(content)
        
        # Setup syntax highlighting
        highlighter = MarkdownSyntaxHighlighter(editor.document())
        
        # Connect events
        editor.textChanged.connect(self.on_text_changed)
        editor.cursorPositionChanged.connect(self.update_cursor_position)
        
        # Formatting actions
        def surround_selection(start, end):
            cursor = editor.textCursor()
            if not cursor.hasSelection():
                return
            selected = cursor.selectedText()
            cursor.insertText(f"{start}{selected}{end}")
        bold_btn.clicked.connect(lambda: surround_selection("**", "**"))
        italic_btn.clicked.connect(lambda: surround_selection("*", "*"))
        code_btn.clicked.connect(lambda: surround_selection("`", "`"))
        link_btn.clicked.connect(lambda: surround_selection("[", "](url)"))
        heading_btn.clicked.connect(lambda: surround_selection("# ", ""))
        
        # Raw preview (QTextEdit)
        raw_preview = QTextEdit()
        raw_preview.setReadOnly(True)
        
        # Rendered preview (QWebEngineView)
        rendered_preview = QWebEngineView()
        
        # Synchronized scrolling logic
        def sync_scroll(src, dst):
            src_scroll = src.verticalScrollBar()
            dst_scroll = dst.verticalScrollBar()
            ratio = src_scroll.value() / max(1, src_scroll.maximum())
            dst_scroll.setValue(int(ratio * dst_scroll.maximum()))
        # Prevent feedback loop
        self._syncing_scroll = False
        def on_editor_scroll():
            if self._syncing_scroll:
                return
            self._syncing_scroll = True
            sync_scroll(editor, rendered_preview)
            self._syncing_scroll = False
        def on_preview_scroll():
            if self._syncing_scroll:
                return
            self._syncing_scroll = True
            sync_scroll(rendered_preview, editor)
            self._syncing_scroll = False
        editor.verticalScrollBar().valueChanged.connect(lambda _: on_editor_scroll())
        rendered_preview.verticalScrollBar().valueChanged.connect(lambda _: on_preview_scroll())
        
        # Add to splitter
        content_splitter.addWidget(editor)
        content_splitter.addWidget(rendered_preview)
        content_splitter.setStretchFactor(0, 1)
        content_splitter.setStretchFactor(1, 1)
        
        # Initially show only editor + rendered preview
        raw_preview.hide()
        
        # Add formatting toolbar and splitter to layout
        tab_layout.addLayout(formatting_toolbar)
        tab_layout.addWidget(content_splitter)
        
        # Add tab
        tab_index = self.tab_widget.addTab(tab_widget, title)
        
        # Store references for easy access
        tab_widget.editor = editor
        tab_widget.raw_preview = raw_preview
        tab_widget.rendered_preview = rendered_preview
        tab_widget.content_splitter = content_splitter
        tab_widget.file_path = None
        tab_widget.is_modified = False
        tab_widget.preview_mode = 'rendered'  # default
        
        # Preview toggle logic
        def show_raw():
            tab_widget.content_splitter.replaceWidget(1, raw_preview)
            raw_preview.show()
            rendered_preview.hide()
            tab_widget.preview_mode = 'raw'
            self.update_preview()
        def show_rendered():
            tab_widget.content_splitter.replaceWidget(1, rendered_preview)
            rendered_preview.show()
            raw_preview.hide()
            tab_widget.preview_mode = 'rendered'
            self.update_preview()
        raw_btn.clicked.connect(show_raw)
        rendered_btn.clicked.connect(show_rendered)
        
        tab_widget.editor.setStyleSheet(self.dark_editor_style if getattr(self, 'theme', 'light') == 'dark' else self.light_editor_style)

        self.apply_theme() # Ensure theme is applied to new tab
        
        return tab_index

    def setup_menus(self):
        """Setup application menus."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_document)
        file_menu.addAction(new_action)
        
        open_action = QAction('Open...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        # Recent files submenu
        self.recent_menu = file_menu.addMenu('Recent Files')
        self._update_recent_files_menu()
        
        file_menu.addSeparator()
        
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction('Save As...', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_action = QAction('Export as HTML...', self)
        export_action.triggered.connect(self.export_html)
        file_menu.addAction(export_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        
        find_action = QAction('Find...', self)
        find_action.setShortcut('Ctrl+F')
        find_action.triggered.connect(self.find_text)
        edit_menu.addAction(find_action)
        
        find_in_files_action = QAction('Find in Files...', self)
        find_in_files_action.setShortcut('Ctrl+Shift+F')
        find_in_files_action.triggered.connect(self.find_in_files)
        edit_menu.addAction(find_in_files_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        toggle_action = QAction('Toggle Edit/Preview', self)
        toggle_action.setShortcut('F5')
        toggle_action.triggered.connect(self.toggle_view)
        view_menu.addAction(toggle_action)
        
        view_menu.addSeparator()
        
        toggle_project_action = QAction('Toggle Project Panel', self)
        toggle_project_action.setShortcut('Ctrl+1')
        toggle_project_action.triggered.connect(self.toggle_project_panel)
        view_menu.addAction(toggle_project_action)
        
        toggle_nav_action = QAction('Toggle Navigation Panel', self)
        toggle_nav_action.setShortcut('Ctrl+2')
        toggle_nav_action.triggered.connect(self.toggle_nav_panel)
        view_menu.addAction(toggle_nav_action)
        
        # Theme toggle
        self.theme = 'light' # Default theme
        theme_toggle_action = QAction('Toggle Light/Dark Theme', self)
        theme_toggle_action.setShortcut('Ctrl+T')
        theme_toggle_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_toggle_action)

        # Diagram rendering toggle
        self.render_diagrams = True
        diagram_toggle_action = QAction('Toggle Diagram Rendering', self)
        diagram_toggle_action.setShortcut('Ctrl+D')
        diagram_toggle_action.setCheckable(True)
        diagram_toggle_action.setChecked(self.render_diagrams)
        diagram_toggle_action.triggered.connect(self.toggle_diagram_rendering)
        view_menu.addAction(diagram_toggle_action)
    
    def _update_recent_files_menu(self):
        """Update the recent files menu."""
        self.recent_menu.clear()
        for file_path in self.recent_files:
            if os.path.exists(file_path):
                action = QAction(os.path.basename(file_path), self)
                action.setToolTip(file_path)
                action.triggered.connect(lambda checked, path=file_path: self.open_recent_file(path))
                self.recent_menu.addAction(action)
    
    def setup_status_bar(self):
        """Setup status bar with useful information."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Word count label
        self.word_count_label = QLabel("Words: 0")
        self.status_bar.addPermanentWidget(self.word_count_label)
        
        # Line/column label
        self.position_label = QLabel("Line: 1, Col: 1")
        self.status_bar.addPermanentWidget(self.position_label)
        
        # File encoding label
        self.encoding_label = QLabel("UTF-8")
        self.status_bar.addPermanentWidget(self.encoding_label)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Additional shortcuts beyond menu items
        close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        close_tab_shortcut.activated.connect(lambda: self.close_tab(self.tab_widget.currentIndex()))
        
        next_tab_shortcut = QShortcut(QKeySequence("Ctrl+Tab"), self)
        next_tab_shortcut.activated.connect(self.next_tab)
        
        prev_tab_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        prev_tab_shortcut.activated.connect(self.prev_tab)

    def load_project_docs(self):
        """Load and index project documentation."""
        try:
            # Initialize StatusAnimation for loading project docs
            # This operation runs on the main thread, so direct use of StatusAnimation is okay.
            # However, Rich's Status/Progress often works best when it takes over the console.
            # For GUI apps, it's often better to use GUI-native progress indicators.
            # Here, we'll log and use the status bar, as StatusAnimation might conflict with GUI.
            
            logger.info("Starting to load and index project documentation...")
            self.status_bar.showMessage("Loading project documents...") # GUI feedback

            self.doc_index = find_markdown_files(self.project_docs_root)
            self.doc_tree = build_doc_tree(self.doc_index)
            
            # Collect all tags for filter dropdown
            all_tags = set()
            total_files = len(self.doc_index)
            
            # If we were to use StatusAnimation here (assuming it doesn't break the GUI):
            # status_loader = StatusAnimation(total_steps=total_files, description="Processing document tags")
            
            for i, (_, file_path) in enumerate(self.doc_index):
                tags = extract_yaml_tags(file_path)
                all_tags.update(tags)
                # status_loader.update(step=i+1, message=f"Processing tags for {os.path.basename(file_path)}")

            # status_loader.complete("Tag processing complete.")

            # Update tag filter dropdown
            self.tag_filter.clear()
            self.tag_filter.addItem("All Tags")
            for tag in sorted(all_tags):
                self.tag_filter.addItem(tag)
                
            logger.info(f"Loaded {len(self.doc_index)} documents with {len(all_tags)} unique tags")
            self.status_bar.showMessage(f"Loaded {len(self.doc_index)} documents.", 5000) # GUI feedback
            
        except Exception as e:
            logger.error(f"Failed to load project docs: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load project documentation: {str(e)}")
            self.status_bar.showMessage("Error loading project documents.", 5000) # GUI feedback

    def populate_doc_list(self):
        """Populate the document list tree."""
        self.doc_list.clear()
        
        def add_nodes(parent, subtree, prefix=""):
            """Recursively add nodes to the tree."""
            for key, val in subtree.items():
                if key == "__files__":
                    for fname, abspath in val:
                        item = QTreeWidgetItem([fname])
                        item.setData(0, Qt.UserRole, abspath)
                        parent.addChild(item)
                else:
                    folder_item = QTreeWidgetItem([key])
                    parent.addChild(folder_item)
                    add_nodes(folder_item, val, prefix + key + "/")
        
        add_nodes(self.doc_list.invisibleRootItem(), self.doc_tree)
        self.doc_list.expandAll()
        # Also update the directory tree
        if hasattr(self, 'dir_tree'):
            self.populate_dir_tree()

    def populate_dir_tree(self):
        """
        Populate the directory tree tab with project docs.
        Directories are expandable nodes; files are selectable leaves.
        """
        self.dir_tree.clear()
        def add_nodes(parent, subtree, prefix=""):
            for key, val in subtree.items():
                if key == "__files__":
                    for fname, abspath in val:
                        file_item = QTreeWidgetItem([fname])
                        file_item.setData(0, Qt.UserRole, abspath)
                        file_item.setChildIndicatorPolicy(QTreeWidgetItem.DontShowIndicator)
                        parent.addChild(file_item)
                else:
                    folder_item = QTreeWidgetItem([key])
                    folder_item.setData(0, Qt.UserRole, None)  # None for directories
                    folder_item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                    parent.addChild(folder_item)
                    add_nodes(folder_item, val, prefix + key + "/")
        add_nodes(self.dir_tree.invisibleRootItem(), self.doc_tree)
        self.dir_tree.expandAll()
        # Connect click event to open files only
        self.dir_tree.itemDoubleClicked.connect(self._on_dir_tree_double_click)

    def _on_dir_tree_double_click(self, item, column):
        """
        Open file if a file node is double-clicked in the directory tree.
        """
        abspath = item.data(0, Qt.UserRole)
        if abspath:
            self._open_file_in_tab(abspath)

    # Continue with the rest of the methods...
    def get_current_tab_data(self):
        """Get the current tab's editor and preview widgets."""
        current_widget = self.tab_widget.currentWidget()
        if current_widget and hasattr(current_widget, 'editor'):
            return current_widget
        return None
    
    def close_tab(self, index: int):
        """Close a tab after checking for unsaved changes."""
        if index < 0 or index >= self.tab_widget.count():
            return
            
        tab_widget = self.tab_widget.widget(index)
        if tab_widget and hasattr(tab_widget, 'is_modified') and tab_widget.is_modified:
            reply = QMessageBox.question(
                self, 'Unsaved Changes',
                f'Tab "{self.tab_widget.tabText(index)}" has unsaved changes. Save before closing?',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                # Save the tab's content
                if hasattr(tab_widget, 'file_path') and tab_widget.file_path:
                    try:
                        with open(tab_widget.file_path, 'w', encoding='utf-8') as f:
                            f.write(tab_widget.editor.toPlainText())
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
                        return
            elif reply == QMessageBox.Cancel:
                return
        
        self.tab_widget.removeTab(index)
        
        # Create new untitled tab if all tabs are closed
        if self.tab_widget.count() == 0:
            self.create_new_tab("Untitled")

    def next_tab(self):
        """Switch to next tab."""
        current = self.tab_widget.currentIndex()
        next_index = (current + 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(next_index)

    def prev_tab(self):
        """Switch to previous tab."""
        current = self.tab_widget.currentIndex()
        prev_index = (current - 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(prev_index)
    
    def on_text_changed(self):
        """Handle text changes in the editor."""
        current_tab = self.get_current_tab_data()
        if current_tab:
            current_tab.is_modified = True
            
            # Update tab title to show modification
            current_index = self.tab_widget.currentIndex()
            current_title = self.tab_widget.tabText(current_index)
            if not current_title.endswith('*'):
                self.tab_widget.setTabText(current_index, current_title + '*')
            
            # Update preview if in preview mode
            if not self.edit_mode:
                self.update_preview()
            
            # Update word count and navigation
            self.update_word_count()
            self.build_navigation_tree(current_tab.editor.toPlainText())
    
    def update_cursor_position(self):
        """Update cursor position in status bar."""
        current_tab = self.get_current_tab_data()
        if current_tab:
            cursor = current_tab.editor.textCursor()
            line = cursor.blockNumber() + 1
            col = cursor.columnNumber() + 1
            self.position_label.setText(f"Line: {line}, Col: {col}")
    
    def update_word_count(self):
        """Update word count in status bar."""
        current_tab = self.get_current_tab_data()
        if current_tab:
            text = current_tab.editor.toPlainText()
            words = len(text.split()) if text.strip() else 0
            chars = len(text)
            self.word_count_label.setText(f"Words: {words}, Chars: {chars}")

    def new_document(self):
        """Create a new document tab."""
        tab_index = self.create_new_tab("Untitled")
        self.tab_widget.setCurrentIndex(tab_index)

    def open_file(self):
        """Open a file in a new tab."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Markdown File", "", "Markdown Files (*.md);;All Files (*)",
            options=options
        )
        
        if file_name:
            self._open_file_in_tab(file_name)

    def _open_file_in_tab(self, file_path: str):
        """Open file in a new tab or switch to existing tab."""
        # Check if file is already open
        existing_tab = self.find_tab_by_file(file_path)
        if existing_tab != -1:
            self.tab_widget.setCurrentIndex(existing_tab)
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create new tab
            tab_index = self.create_new_tab(os.path.basename(file_path), content)
            tab_widget = self.tab_widget.widget(tab_index)
            tab_widget.file_path = file_path
            tab_widget.is_modified = False
            
            # Switch to new tab
            self.tab_widget.setCurrentIndex(tab_index)
            
            # Update current file reference
            self.current_file = file_path
            
            # Add to recent files
            self._add_recent_file(file_path)
            
            # Update navigation and tags
            self.build_navigation_tree(content)
            tags = extract_yaml_tags(file_path)
            self.tag_label.setText(f"Tags: {', '.join(tags) if tags else '(none)'}")
            
            # Update preview if in preview mode
            if not self.edit_mode:
                self.update_preview()
            
            logger.info(f"Opened file: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
            logger.error(f"Failed to open file {file_path}: {e}")

    def find_tab_by_file(self, file_path: str) -> int:
        """Find tab index by file path."""
        for i in range(self.tab_widget.count()):
            tab_widget = self.tab_widget.widget(i)
            if hasattr(tab_widget, 'file_path') and tab_widget.file_path == file_path:
                return i
        return -1

    def save_file(self):
        """Save current document."""
        current_tab = self.get_current_tab_data()
        if not current_tab:
            return
        
        if current_tab.file_path:
            try:
                with open(current_tab.file_path, 'w', encoding='utf-8') as f:
                    f.write(current_tab.editor.toPlainText())
                
                current_tab.is_modified = False
                
                # Update tab title (remove asterisk)
                current_index = self.tab_widget.currentIndex()
                title = self.tab_widget.tabText(current_index).rstrip('*')
                self.tab_widget.setTabText(current_index, title)
                
                self.status_bar.showMessage(f"Saved {current_tab.file_path}", 3000)
                logger.info(f"Saved file: {current_tab.file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
                logger.error(f"Failed to save file: {e}")
        else:
            # No file path, use save as
            self.save_file_as()

    def save_file_as(self):
        """Save current document with new name."""
        current_tab = self.get_current_tab_data()
        if not current_tab:
            return
        
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Markdown File", "", "Markdown Files (*.md);;All Files (*)",
            options=options
        )
        
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(current_tab.editor.toPlainText())
                
                # Update tab properties
                current_tab.file_path = file_name
                current_tab.is_modified = False
                
                # Update tab title
                current_index = self.tab_widget.currentIndex()
                self.tab_widget.setTabText(current_index, os.path.basename(file_name))
                
                # Add to recent files
                self._add_recent_file(file_name)
                
                self.status_bar.showMessage(f"Saved as {file_name}", 3000)
                logger.info(f"Saved file as: {file_name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")

    def toggle_view(self):
        """Toggle between edit and preview modes."""
        current_tab = self.get_current_tab_data()
        if not current_tab:
            return
        
        if self.edit_mode:
            # Switch to preview mode
            self.update_preview()
            current_tab.editor.hide()
            current_tab.rendered_preview.show()
            self.edit_mode = False
        else:
            # Switch to edit mode
            current_tab.editor.show()
            current_tab.rendered_preview.hide()
            self.edit_mode = True

    def update_preview(self):
        """
        Update the preview pane with rendered markdown, including diagram support.
        Uses QWebEngineView for full HTML+JS rendering (Mermaid, PlantUML, etc), or QTextEdit for raw HTML.
        """
        current_tab = self.get_current_tab_data()
        if not current_tab:
            return
        content = current_tab.editor.toPlainText()
        try:
            html = markdown.markdown(
                content, 
                extensions=[
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.tables',
                    'markdown.extensions.toc',
                    'markdown.extensions.codehilite'
                ]
            )
            css = self.dark_html_css if self.theme == 'dark' else self.light_html_css
            if current_tab.preview_mode == 'raw':
                # Show raw HTML in QTextEdit
                current_tab.raw_preview.setPlainText(html)
            else:
                # Mermaid/diagram support
                if self.render_diagrams:
                    import re
                    def mermaid_replacer(match):
                        code = match.group(1)
                        return f'<div class="mermaid">{code}</div>'
                    html = re.sub(r'<pre><code class="language-mermaid">([\s\S]*?)</code></pre>', mermaid_replacer, html)
                    mermaid_js = """
                    <script type="module">
                    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10.9.0/dist/mermaid.esm.min.mjs';
                    mermaid.initialize({ startOnLoad: true });
                    </script>
                    """
                else:
                    mermaid_js = ""
                styled_html = f"""
                <html>
                <head>
                    {css}
                    {mermaid_js}
                </head>
                <body>{html}</body>
                </html>
                """
                current_tab.rendered_preview.setHtml(styled_html)
        except Exception as e:
            if current_tab.preview_mode == 'raw':
                current_tab.raw_preview.setPlainText(f"Error rendering preview: {e}")
            else:
                current_tab.rendered_preview.setHtml(f"<pre>Error rendering preview: {e}</pre>")
            logger.error(f"Failed to render preview: {e}")

    def build_navigation_tree(self, content: str):
        """Build navigation tree from markdown headers."""
        self.nav_tree.clear()
        
        lines = content.split('\n')
        header_pattern = re.compile(r'^(#{1,6})\s+(.*)')
        
        stack = []  # Stack to track header hierarchy
        
        for line_num, line in enumerate(lines):
            match = header_pattern.match(line)
            if match:
                level = len(match.group(1))  # Number of # characters
                title = match.group(2).strip()
                
                # Create tree item
                item = QTreeWidgetItem([title])
                item.setData(0, Qt.UserRole, line_num)  # Store line number
                
                # Determine parent based on header level
                while stack and stack[-1][0] >= level:
                    stack.pop()
                
                if stack:
                    parent_item = stack[-1][1]
                    parent_item.addChild(item)
                else:
                    self.nav_tree.addTopLevelItem(item)
                
                stack.append((level, item))
        
        self.nav_tree.expandAll()

    def navigate_to_section(self, item):
        """Navigate to selected section in the editor."""
        line_num = item.data(0, Qt.UserRole)
        if line_num is not None:
            current_tab = self.get_current_tab_data()
            if current_tab:
                cursor = current_tab.editor.textCursor()
                cursor.movePosition(QTextCursor.Start)
                for _ in range(line_num):
                    cursor.movePosition(QTextCursor.Down)
                current_tab.editor.setTextCursor(cursor)
                current_tab.editor.setFocus()

    def open_project_doc(self, item):
        """Open project document from tree."""
        abspath = item.data(0, Qt.UserRole)
        if abspath and os.path.isfile(abspath):
            self._open_file_in_tab(abspath)

    def find_text(self):
        """Find text in current document."""
        current_tab = self.get_current_tab_data()
        if not current_tab:
            return
        
        search_text, ok = QInputDialog.getText(self, "Find Text", "Search for:")
        if ok and search_text:
            if self.edit_mode:
                current_tab.editor.find(search_text)
            else:
                current_tab.rendered_preview.find(search_text)

    def filter_project_docs(self, text: str):
        """Filter project documents by search text."""
        if not hasattr(self, 'doc_list'):
            return
            
        def filter_item(item):
            # Check if item text contains search term
            item_text = item.text(0).lower()
            search_text = text.lower()
            
            # If item has children, check them recursively
            has_matching_child = False
            for i in range(item.childCount()):
                child = item.child(i)
                if filter_item(child):
                    has_matching_child = True
            
            # Show item if it matches or has matching children
            matches = search_text in item_text or has_matching_child
            item.setHidden(not matches and text.strip())
            
            return matches
        
        # Apply filter to all root items
        root = self.doc_list.invisibleRootItem()
        for i in range(root.childCount()):
            filter_item(root.child(i))
    
    def filter_by_tag(self, tag: str):
        """Filter project documents by tag."""
        if tag == "All Tags" or not hasattr(self, 'doc_list'):
            # Show all items
            def show_all(item):
                item.setHidden(False)
                for i in range(item.childCount()):
                    show_all(item.child(i))
            
            root = self.doc_list.invisibleRootItem()
            for i in range(root.childCount()):
                show_all(root.child(i))
            return
        
        # Filter by specific tag
        def filter_by_tag_recursive(item):
            if item.data(0, Qt.UserRole):  # This is a file
                file_path = item.data(0, Qt.UserRole)
                tags = extract_yaml_tags(file_path)
                item.setHidden(tag not in tags)
            else:  # This is a folder
                has_visible_child = False
                for i in range(item.childCount()):
                    filter_by_tag_recursive(item.child(i))
                    if not item.child(i).isHidden():
                        has_visible_child = True
                item.setHidden(not has_visible_child)
        
        root = self.doc_list.invisibleRootItem()
        for i in range(root.childCount()):
            filter_by_tag_recursive(root.child(i))
    
    def find_in_files(self):
        """Find text in all project files using background thread."""
        if not self.project_docs_root:
            QMessageBox.information(self, "Information", "No project loaded to search in.")
            return

        search_term, ok = QInputDialog.getText(self, "Find in Files", "Enter text to search:")
        if not (ok and search_term):
            return

        if self.search_thread and self.search_thread.isRunning():
            QMessageBox.warning(self, "Search in Progress", "A search is already running.")
            return

        all_files = [path for _, path in self.doc_index]
        self.search_thread = SearchThread(search_term, all_files)
        
        # Create a progress dialog for GUI feedback
        self.search_progress_dialog = QProgressDialog("Searching files...", "Cancel", 0, 100, self)
        self.search_progress_dialog.setWindowTitle("Search in Progress")
        self.search_progress_dialog.setWindowModality(Qt.WindowModal)
        self.search_progress_dialog.setAutoClose(True)
        self.search_progress_dialog.setAutoReset(True)
        self.search_progress_dialog.setValue(0)

        # Connect signals from search thread to GUI updates
        self.search_thread.search_progress.connect(self.update_search_progress_dialog)
        self.search_thread.search_finished.connect(self.show_search_results)
        self.search_thread.finished.connect(self.search_progress_dialog.reset) # Reset dialog when thread finishes
        self.search_progress_dialog.canceled.connect(self.search_thread.terminate) # Terminate thread if dialog is canceled

        self.search_thread.start()
        self.search_progress_dialog.show()

    def update_search_progress_dialog(self, value: int, message: str):
        """Update the search progress dialog."""
        if self.search_progress_dialog:
            self.search_progress_dialog.setValue(value)
            self.search_progress_dialog.setLabelText(message)

    def show_search_results(self, results: List[Dict]):
        """Display search results in a new dialog or panel."""
        if self.search_progress_dialog:
            self.search_progress_dialog.close() # Close progress dialog

        if not results:
            QMessageBox.information(self, "Search Results", "No results found.")
            return

        # For now, log results. A dedicated results viewer would be better.
        logger.info(f"Search Results ({len(results)} found):")
        for res in results:
            logger.info(f"  File: {res['file']}, Line: {res['line']}, Text: {res['text']}")
        
        # Simple dialog to show results (can be improved)
        results_text = ""
        for res in results:
            results_text += f"File: {os.path.basename(res['file'])}\nLine {res['line']}: {res['text']}\nContext:\n" 
            results_text += "\n".join([f"  {ctx_line}" for ctx_line in res['context']]) + "\n---\n"
        
        # Create a dialog to display results
        dialog = QDialog(self)
        dialog.setWindowTitle("Search Results")
        layout = QVBoxLayout(dialog)
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setText(results_text)
        layout.addWidget(text_area)
        dialog.setMinimumSize(700, 500)
        dialog.exec_()

    def toggle_project_panel(self):
        """Toggle visibility of project panel."""
        if hasattr(self, 'doc_list'):
            self.doc_list.parent().setVisible(not self.doc_list.parent().isVisible())
    
    def toggle_nav_panel(self):
        """Toggle visibility of navigation panel."""
        self.nav_tree.parent().setVisible(not self.nav_tree.parent().isVisible())
    
    def export_html(self):
        """Export current document as HTML."""
        current_tab = self.get_current_tab_data()
        if not current_tab:
            return
        
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export as HTML", "", "HTML Files (*.html);;All Files (*)",
            options=options
        )
        
        if file_name:
            try:
                content = current_tab.editor.toPlainText()
                html = markdown.markdown(
                    content, 
                    extensions=[
                        'markdown.extensions.fenced_code',
                        'markdown.extensions.tables',
                        'markdown.extensions.toc',
                        'markdown.extensions.codehilite'
                    ]
                )
                
                # Add comprehensive CSS styling
                styled_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <title>{os.path.basename(file_name)}</title>
                    <style>
                        body {{ 
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                            line-height: 1.7; 
                            color: #333;
                            background-color: #fdfdfd;
                            margin: 0 auto; /* Center content */
                            padding: 25px;
                            max-width: 900px; /* Readable width */
                        }}
                        h1, h2, h3, h4, h5, h6 {{ 
                            color: #2c3e50; 
                            margin-top: 1.5em;
                            margin-bottom: 0.8em;
                            line-height: 1.3;
                        }}
                        h1 {{ font-size: 2.2em; border-bottom: 2px solid #ecf0f1; padding-bottom: 0.3em; }}
                        h2 {{ font-size: 1.8em; border-bottom: 1px solid #ecf0f1; padding-bottom: 0.2em; }}
                        h3 {{ font-size: 1.5em; }}
                        h4 {{ font-size: 1.2em; }}
                        p {{ margin-bottom: 1.2em; }}
                        a {{ color: #3498db; text-decoration: none; }}
                        a:hover {{ text-decoration: underline; color: #2980b9; }}
                        code {{ 
                            background-color: #ecf0f1; 
                            padding: 0.2em 0.4em; 
                            margin: 0 0.1em;
                            border-radius: 3px; 
                            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
                            font-size: 0.9em;
                            color: #e74c3c;
                        }}
                        pre {{ 
                            background-color: #2d2d2d; /* Darker background for code blocks */
                            color: #f8f8f2; /* Light text for contrast */
                            padding: 1em; 
                            border-radius: 5px; 
                            overflow-x: auto;
                            margin: 1.5em 0;
                            border: 1px solid #3d3d3d; /* Subtle border */
                        }}
                        pre code {{
                            background-color: transparent;
                            color: inherit; /* Inherit from pre for consistent styling */
                            padding: 0;
                            margin: 0;
                            border-radius: 0;
                            font-size: 0.95em; /* Slightly larger for readability in blocks */
                        }}
                        blockquote {{ 
                            border-left: 5px solid #3498db; 
                            margin: 1.5em 0; 
                            padding: 0.5em 1.5em; 
                            color: #555; 
                            background-color: #f9f9f9;
                        }}
                        table {{ 
                            border-collapse: collapse; 
                            width: 100%; 
                            margin: 1.5em 0;
                            box-shadow: 0 0 5px rgba(0,0,0,0.1);
                        }}
                        th, td {{ 
                            border: 1px solid #dfe2e5; 
                            padding: 0.8em 1em; 
                            text-align: left; 
                        }}
                        th {{ 
                            background-color: #f6f8fa; 
                            font-weight: 600;
                            color: #24292e;
                        }}
                        tr:nth-child(even) {{ background-color: #fdfdfd; }}
                        img {{ 
                            max-width: 100%; 
                            height: auto; 
                            border-radius: 4px;
                            margin: 1em 0;
                            display: block; /* Center images */
                            margin-left: auto;
                            margin-right: auto;
                        }}
                        ul, ol {{
                            padding-left: 2em;
                            margin-bottom: 1.2em;
                        }}
                        li {{ margin-bottom: 0.5em; }}
                        hr {{
                            border: none;
                            border-top: 1px solid #ecf0f1;
                            margin: 2em 0;
                        }}
                        .toc {{
                            background: #f8f9fa;
                            border: 1px solid #dee2e6;
                            border-radius: 5px;
                            padding: 15px;
                            margin: 20px 0;
                            font-size: 0.95em;
                        }}
                        .toc ul {{
                            margin: 0;
                            padding-left: 1.5em;
                        }}
                        .toc li {{
                            margin-bottom: 0.3em;
                        }}
                        @media (max-width: 768px) {{
                            body {{
                                padding: 15px;
                                font-size: 15px;
                            }}
                            h1 {{ font-size: 1.8em; }}
                            h2 {{ font-size: 1.5em; }}
                            h3 {{ font-size: 1.3em; }}
                            table {{
                                font-size: 0.9em;
                            }}
                            th, td {{
                                padding: 0.6em 0.5em;
                            }}
                        }}
                        /* CodeHilite styles (basic example, can be expanded) */
                        .codehilite .k {{ color: #6ab0f3; font-weight: bold; }} /* Keyword */
                        .codehilite .s, .codehilite .s1, .codehilite .s2 {{ color: #a6e22e; }} /* String */
                        .codehilite .c, .codehilite .c1, .codehilite .cm, .codehilite .cs {{ color: #75715e; font-style: italic; }} /* Comment */
                        .codehilite .o, .codehilite .p {{ color: #f8f8f2; }} /* Operator, Punctuation */
                        .codehilite .n, .codehilite .nb, .codehilite .nc, .codehilite .no, .codehilite .nv, .codehilite .nn, .codehilite .ne, .codehilite .nf, .codehilite .nl, .codehilite .nx {{ color: #f8f8f2; }} /* Names */
                        .codehilite .m, .codehilite .mf, .codehilite .mh, .codehilite .mi, .codehilite .mo, .codehilite .il {{ color: #ae81ff; }} /* Number */
                        .codehilite .gd {{ color: #f92672; }} /* Generic.Deleted */
                        .codehilite .ge {{ font-style: italic; }} /* Generic.Emph */
                        .codehilite .gh {{ color: #f8f8f2; font-weight: bold; }} /* Generic.Heading */
                        .codehilite .gi {{ color: #a6e22e; }} /* Generic.Inserted */
                        .codehilite .gs {{ font-weight: bold; }} /* Generic.Strong */
                        .codehilite .gu {{ color: #75715e; font-weight: bold; }} /* Generic.Subheading */
                        .codehilite .kc {{ color: #6ab0f3; font-weight: bold; }} /* Keyword.Constant */
                        .codehilite .kd {{ color: #6ab0f3; font-weight: bold; }} /* Keyword.Declaration */
                        .codehilite .kn {{ color: #f92672; font-weight: bold; }} /* Keyword.Namespace */
                        .codehilite .kp {{ color: #6ab0f3; font-weight: bold; }} /* Keyword.Pseudo */
                        .codehilite .kr {{ color: #6ab0f3; font-weight: bold; }} /* Keyword.Reserved */
                        .codehilite .kt {{ color: #66d9ef; }} /* Keyword.Type */
                    </style>
                </head>
                <body>
                {html}
                <footer style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #777; font-size: 0.9em;">
                    Generated by ImpressionCore Enhanced Markdown Viewer on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </footer>
                </body>
                </html>
                """
                
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(styled_html)
                
                self.status_bar.showMessage(f"Exported to {file_name}", 3000)
                logger.info(f"Exported to HTML: {file_name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not export file: {str(e)}")
                logger.error(f"Failed to export HTML: {e}")
    
    def open_recent_file(self, file_path: str):
        """Open a file from recent files list."""
        if os.path.exists(file_path):
            self._open_file_in_tab(file_path)
        else:
            # Remove from recent files if it doesn't exist
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)
                self._save_recent_files()
                self._update_recent_files_menu()
                QMessageBox.information(self, "File Not Found", 
                                      f"File no longer exists and has been removed from recent files:\n{file_path}")
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Check for unsaved changes in all tabs
        unsaved_tabs = []
        for i in range(self.tab_widget.count()):
            tab_widget = self.tab_widget.widget(i)
            if hasattr(tab_widget, 'is_modified') and tab_widget.is_modified:
                unsaved_tabs.append((i, self.tab_widget.tabText(i).rstrip('*')))
        
        if unsaved_tabs:
            tab_names = ', '.join([name for _, name in unsaved_tabs])
            reply = QMessageBox.question(
                self, 'Unsaved Changes',
                f'The following tabs have unsaved changes:\n{tab_names}\n\nSave all before closing?',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.Save:
                # Save all modified tabs
                for tab_index, _ in unsaved_tabs:
                    tab = self.tab_widget.widget(tab_index)
                    if hasattr(tab, 'file_path') and tab.file_path:
                        try:
                            with open(tab.file_path, 'w', encoding='utf-8') as f:
                                f.write(tab.editor.toPlainText())
                            logger.info(f"Saved on exit: {tab.file_path}")
                        except Exception as e:
                            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
                            logger.error(f"Failed to save on exit: {e}")
        
        # Save application settings
        self._save_settings()
        
        # Stop auto-save timer
        if hasattr(self, 'auto_save_timer'):
            self.auto_save_timer.stop()
        
        # Stop search thread if running
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.quit()
            self.search_thread.wait()
        
        logger.info("Application closed")
        event.accept()

    def update_search_progress(self, progress: int, message: str):
        """Update search progress (stub for future Rich integration)."""
        logger.info(f"Search progress: {progress}%, {message}")

    def update_search_progress_dialog(self, value: int, message: str):
        """Update the search progress dialog."""
        if self.search_progress_dialog:
            self.search_progress_dialog.setValue(value)
            self.search_progress_dialog.setLabelText(message)

    def toggle_theme(self):
        """Toggle between light and dark themes for editor and preview."""
        self.theme = 'dark' if self.theme == 'light' else 'light'
        self.apply_theme()
        # Save theme preference
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
            else:
                settings = {}
            settings['theme'] = self.theme
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            logger.warning(f"Failed to save theme preference: {e}")

    def apply_theme(self):
        """
        Apply the current theme to all open tabs and the entire application.
        Uses QApplication.setStyleSheet for global theming.
        """
        from PyQt5.QtWidgets import QApplication
        # Global stylesheet for dark/light mode
        dark_app_style = """
            QWidget { background-color: #232629; color: #e0e0e0; }
            QTabWidget::pane, QTabBar::tab { background: #232629; color: #e0e0e0; }
            QMenuBar, QMenu, QMenuBar::item { background: #232629; color: #e0e0e0; }
            QPushButton { background-color: #2d2d2d; color: #e0e0e0; border: 1px solid #444; }
            QLineEdit, QTextEdit { background-color: #232629; color: #e0e0e0; }
            QTreeWidget, QTreeWidget::item { background: #232629; color: #e0e0e0; }
            QStatusBar { background: #232629; color: #e0e0e0; }
        """
        light_app_style = """
            QWidget { background-color: #fdfdfd; color: #232629; }
            QTabWidget::pane, QTabBar::tab { background: #fdfdfd; color: #232629; }
            QMenuBar, QMenu, QMenuBar::item { background: #fdfdfd; color: #232629; }
            QPushButton { background-color: #f6f8fa; color: #232629; border: 1px solid #ccc; }
            QLineEdit, QTextEdit { background-color: #fdfdfd; color: #232629; }
            QTreeWidget, QTreeWidget::item { background: #fdfdfd; color: #232629; }
            QStatusBar { background: #fdfdfd; color: #232629; }
        """
        app = QApplication.instance()
        if app:
            app.setStyleSheet(dark_app_style if self.theme == 'dark' else light_app_style)
        # Editor/preview theme for all tabs
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if hasattr(tab, 'editor'):
                tab.editor.setStyleSheet(self.dark_editor_style if self.theme == 'dark' else self.light_editor_style)
            # Preview handled by HTML/CSS
        self.update()

    def toggle_diagram_rendering(self):
        """Toggle diagram (Mermaid, PlantUML) rendering in preview."""
        self.render_diagrams = not self.render_diagrams
        self.update_preview()

def main():
    """Main function to run the enhanced markdown viewer."""
    import argparse
    
    parser = argparse.ArgumentParser(description='ImpressionCore Enhanced Documentation Viewer')
    parser.add_argument('file', nargs='?', help='Markdown file to open')
    parser.add_argument('--browse', action='store_true', 
                       help='Browse project documentation')
    parser.add_argument('--project-root', type=str, 
                       help='Project documentation root directory')
    
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    app.setApplicationName("ImpressionCore Documentation Viewer")
    app.setApplicationVersion("2.0.0")
    
    # Determine project root
    project_root = None
    if args.browse or args.project_root:
        project_root = args.project_root or os.path.join(os.getcwd(), 'docs')
        if not os.path.exists(project_root):
            print(f"Warning: Project root '{project_root}' does not exist")
            project_root = None
    
    # Create and show viewer
    viewer = EnhancedMarkdownViewer(project_root)
    
    # Open file if specified
    if args.file and os.path.exists(args.file):
        viewer._open_file_in_tab(args.file)
    
    viewer.show()
    
    # Start the application
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
