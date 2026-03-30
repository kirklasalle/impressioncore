# Web Search MCP Server

This MCP (Model Context Protocol) server allows AI assistants to search the web for information and provides properly cited results.

## Features

- Web search functionality using DuckDuckGo
- Automatic citation generation
- Configurable search parameters
- Rate limiting to prevent abuse

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure the server in `config.json`

3. Run the server:

```bash
python server.py
```

## API Usage

Send a request with:

```json
{
  "query": "your search query",
  "num_results": 5,
  "require_citations": true
}
```

## Response Format

```json
{
  "results": [
    {
      "title": "Result title",
      "content": "Snippet of content",
      "url": "https://source-url.com",
      "citation": "Author Name. (Year). Title. Publisher. Retrieved from URL"
    }
  ],
  "metadata": {
    "query": "original query",
    "timestamp": "search timestamp",
    "result_count": 5
  }
}
```
