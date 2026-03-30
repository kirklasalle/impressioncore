#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #command_line #memory_management #python #source_code #src/core/utils/copilot_memory_cache_utils.py #testing
**Category:** Core Implementation
**Status:** Active
"""








# Copilot Memory Cache Utils

"""
copilot_memory_cache_utils.py

Utility functions for persistent Copilot memory cache management.
Handles both markdown baton pass log and SQLite database for ImpressionCore project continuity.

Memory optimizations: uses context managers, avoids loading large logs into memory, and supports incremental updates.
"""

import os
import sqlite3
from datetime import datetime
from typing import Any

MEMORY_DB_PATH = os.path.join(os.path.dirname(__file__), '../../memlog/copilot_memory.sqlite')
MEMORY_MD_PATH = os.path.join(os.path.dirname(__file__), '../../memlog/copilot_memory.md')


def init_memory_db(db_path: str = MEMORY_DB_PATH) -> None:
    """
    Initialize the persistent memory SQLite database if it does not exist.
    Args:
        db_path: Path to the SQLite database file.
    Returns:
        None
    """
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS session_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                summary TEXT,
                outstanding_tasks TEXT,
                key_decisions TEXT
            )
        ''')
        conn.commit()


def write_memory(key: str, value: str, db_path: str = MEMORY_DB_PATH) -> None:
    """
    Write a key-value pair to the persistent memory database.
    Args:
        key: The key to store.
        value: The value to store.
        db_path: Path to the SQLite database file.
    Returns:
        None
    """
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO memory (key, value, updated) VALUES (?, ?, ?)
        ''', (key, value, datetime.utcnow()))
        conn.commit()


def read_memory(key: str, db_path: str = MEMORY_DB_PATH) -> str | None:
    """
    Read a value from the persistent memory database by key.
    Args:
        key: The key to retrieve.
        db_path: Path to the SQLite database file.
    Returns:
        The value if found, else None.
    """
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('SELECT value FROM memory WHERE key = ?', (key,))
        row = c.fetchone()
        return row[0] if row else None


def log_session(summary: str, outstanding_tasks: str, key_decisions: str, db_path: str = MEMORY_DB_PATH) -> None:
    """
    Log a session summary to the session_log table.
    Args:
        summary: Session summary text.
        outstanding_tasks: Outstanding tasks text.
        key_decisions: Key decisions text.
        db_path: Path to the SQLite database file.
    Returns:
        None
    """
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO session_log (timestamp, summary, outstanding_tasks, key_decisions)
            VALUES (?, ?, ?, ?)
        ''', (datetime.utcnow(), summary, outstanding_tasks, key_decisions))
        conn.commit()


def read_latest_session(db_path: str = MEMORY_DB_PATH) -> dict[str, Any] | None:
    """
    Read the latest session log entry.
    Args:
        db_path: Path to the SQLite database file.
    Returns:
        Dict with keys: timestamp, summary, outstanding_tasks, key_decisions, or None if not found.
    """
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''
            SELECT timestamp, summary, outstanding_tasks, key_decisions
            FROM session_log
            ORDER BY timestamp DESC
            LIMIT 1
        ''')
        row = c.fetchone()
        if row:
            return {
                'timestamp': row[0],
                'summary': row[1],
                'outstanding_tasks': row[2],
                'key_decisions': row[3],
            }
        return None


def append_to_markdown_log(entry: str, md_path: str = MEMORY_MD_PATH) -> None:
    """
    Append a new entry to the persistent memory markdown log.
    Args:
        entry: Markdown-formatted log entry.
        md_path: Path to the markdown log file.
    Returns:
        None
    """
    with open(md_path, 'a', encoding='utf-8') as f:
        f.write(f"\n{entry}\n")


def get_markdown_log(md_path: str = MEMORY_MD_PATH) -> str:
    """
    Read the entire persistent memory markdown log.
    Args:
        md_path: Path to the markdown log file.
    Returns:
        The full log as a string.
    """
    with open(md_path, encoding='utf-8') as f:
        return f.read()


# --- Logic Concept Cache Integration ---
import re

LOGIC_CACHE_MD_PATH = os.path.join(os.path.dirname(__file__), '../../../docs/logic_concept_cache.md')

def parse_logic_concept_cache(md_path: str = LOGIC_CACHE_MD_PATH):
    """Parse logic_concept_cache.md into a list of concept dicts."""
    if not os.path.exists(md_path):
        return []
    with open(md_path, encoding='utf-8') as f:
        content = f.read()
    # Each concept block starts with '### '
    blocks = re.split(r'(?m)^###?\s+', content)
    concepts = []
    for block in blocks:
        if not block.strip() or 'Concept Cache' in block:
            continue
        lines = block.strip().splitlines()
        title = lines[0] if lines else 'Untitled'
        body = '\n'.join(lines[1:]).strip()
        concepts.append({'key': title.strip(), 'value': body})
    return concepts

def sync_logic_cache_to_db(db_path: str = MEMORY_DB_PATH, md_path: str = LOGIC_CACHE_MD_PATH):
    """Sync logic_concept_cache.md to the memory table."""
    concepts = parse_logic_concept_cache(md_path)
    for c in concepts:
        write_memory(c['key'], c['value'], db_path)

def sync_db_to_logic_cache(db_path: str = MEMORY_DB_PATH, md_path: str = LOGIC_CACHE_MD_PATH):
    """Sync memory table to logic_concept_cache.md (overwrite)."""
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('SELECT key, value FROM memory ORDER BY updated DESC')
        rows = c.fetchall()
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('# ImpressionCore Logic & Concept Cache\n\n')
        for key, value in rows:
            f.write(f'### {key}\n{value}\n\n')

# --- RAG/Context Retrieval API ---
def search_memory(query: str, db_path: str = MEMORY_DB_PATH, top_k: int = 3):
    """Search memory table for relevant concepts."""
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('SELECT key, value, updated FROM memory WHERE value LIKE ? ORDER BY updated DESC', (f'%{query}%',))
        results = c.fetchall()
    return [{'key': r[0], 'value': r[1], 'updated': r[2]} for r in results[:top_k]]

# --- CLI & API Endpoints ---
def main():
    import argparse
    parser = argparse.ArgumentParser(description='ImpressionCore Copilot Memory Cache Utility')
    parser.add_argument('--init', action='store_true', help='Initialize memory DB')
    parser.add_argument('--sync-cache', action='store_true', help='Sync logic_concept_cache.md to DB')
    parser.add_argument('--sync-db', action='store_true', help='Sync DB to logic_concept_cache.md')
    parser.add_argument('--query', type=str, help='Query memory for context')
    parser.add_argument('--topk', type=int, default=3, help='Number of top results to return')
    parser.add_argument('--log-session', nargs=3, metavar=('SUMMARY','TASKS','DECISIONS'), help='Log a session (summary, outstanding_tasks, key_decisions)')
    parser.add_argument('--api', action='store_true', help='Run as HTTP API (Flask)')
    args = parser.parse_args()

    if args.init:
        init_memory_db()
        print('Memory DB initialized.')
    if args.sync_cache:
        sync_logic_cache_to_db()
        print('Logic concept cache synced to DB.')
    if args.sync_db:
        sync_db_to_logic_cache()
        print('DB synced to logic concept cache.')
    if args.query:
        results = search_memory(args.query, top_k=args.topk)
        for r in results:
            print(f"Key: {r['key']}\nUpdated: {r['updated']}\nValue:\n{r['value']}\n{'-'*40}")
    if args.log_session:
        summary, tasks, decisions = args.log_session
        log_session(summary, tasks, decisions)
        print('Session logged.')
    if args.api:
        run_api()

# --- Simple HTTP API for MCP/Agentic Integration ---
def run_api(host='127.0.0.1', port=5055):
    from flask import Flask, jsonify, request
    app = Flask(__name__)

    @app.route('/query', methods=['GET'])
    def api_query():
        q = request.args.get('q', '')
        top_k = int(request.args.get('topk', 3))
        results = search_memory(q, top_k=top_k)
        return jsonify(results)

    @app.route('/sync-cache', methods=['POST'])
    def api_sync_cache():
        sync_logic_cache_to_db()
        return jsonify({'status': 'cache synced'})

    @app.route('/sync-db', methods=['POST'])
    def api_sync_db():
        sync_db_to_logic_cache()
        return jsonify({'status': 'db synced'})

    app.run(host=host, port=port)

# --- Entry Point ---
if __name__ == '__main__':
    main()
