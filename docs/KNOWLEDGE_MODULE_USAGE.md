# Unified Knowledge Store (UKS) – Scalable Workflow & API

## Overview

The Unified Knowledge Store (UKS) enables persistent, queryable memory for ImpressionCore-b1. It supports efficient storage and retrieval of subject-predicate-object facts, even at large scale.

---

## User Guide

### Adding Knowledge

- Navigate to the “Knowledge Store (UKS)” step in the sidebar.
- Fill in the Subject, Predicate, and Object fields.
- Click “Add Fact” to store the fact in the UKS.
- Success and error messages will be shown for each operation.

### Querying Knowledge

- Enter a subject in the “Query Subject” field.
- Click “Query Knowledge” to retrieve all facts matching the subject.
- Results are displayed as a list of facts, or a message if no match is found.

### Performance Notes

- The UKS is optimized for large-scale use. Queries use streaming to avoid loading the entire store into memory.
- For very large stores, only matching facts are loaded, ensuring responsiveness even with tens of thousands of entries.

---

## Developer Guide

### Endpoints

- `POST /uks_introduction/add_fact`
  - Adds a new fact to the UKS.
  - Parameters: `subject`, `predicate`, `object`
  - Returns: Success or error message.

- `GET /uks_introduction/query`
  - Streams and returns all facts matching a given subject.
  - Parameter: `querySubject`
  - Returns: List of matching facts or a not-found message.

### Implementation Details

- Facts are stored in a JSON file at `uploads/uks_store.json`.
- The backend uses a generator (`stream_uks_query`) to stream matching facts for queries, minimizing memory usage.
- For compact JSON or in case of streaming failure, the backend falls back to loading all facts and filtering in memory.
- All endpoints include input validation, error handling, and user feedback.

### Testing

- Unit and integration tests are provided in `tests/brainsim/test_uks.py` and `tests/brainsim/test_uks_streaming.py`.
- Tests cover adding, querying, error handling, and scalability for large stores.

### Memory & Performance

- Streaming queries are used for large files to avoid OOM errors.
- For extremely large stores, consider further enhancements (e.g., indexing, database backend).

---

## Example Usage

```bash
# Add Fact
curl -X POST -F "subject=Mars" -F "predicate=has_moons" -F "object=2" http://localhost:5000/uks_introduction/add_fact

# Query Fact
curl "http://localhost:5000/uks_introduction/query?querySubject=Mars"
```
