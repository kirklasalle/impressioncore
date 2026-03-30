-- ImpressionCore Copilot Persistent Memory Database
-- This schema is managed by copilot_memory_utils.py

CREATE TABLE IF NOT EXISTS memory (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated TIMESTAMP
);

CREATE TABLE IF NOT EXISTS session_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP,
    summary TEXT,
    outstanding_tasks TEXT,
    key_decisions TEXT
);
