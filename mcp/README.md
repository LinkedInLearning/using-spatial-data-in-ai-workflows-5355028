# Foursquare Open Places MCP Server

An MCP (Model Context Protocol) server that enables Claude to query [Foursquare Open Source Places](https://docs.foursquare.com/data-products/docs/access-fsq-os-places) data using [SedonaDB](https://sedona.apache.org/sedonadb/) as an in-memory spatial database.

## Overview

This server connects Claude Desktop to external geospatial data. LLMs aren't good at processing large datasets or performing spatial queries — this MCP server handles that by:

1. Loading Foursquare Open Places data from S3 into SedonaDB
2. Exposing spatial query tools that Claude can call
3. Returning structured results that Claude can interpret and present

## Tech Stack

- [MCP](https://modelcontextprotocol.io/) — Model Context Protocol SDK (FastMCP)
- [SedonaDB](https://sedona.apache.org/sedonadb/) — Spatial database engine (Rust, Apache Arrow)
- [Foursquare Open Places](https://docs.foursquare.com/data-products/docs/access-fsq-os-places) — 100M+ commercial POIs on AWS S3 (Apache 2.0)
- [uv](https://docs.astral.sh/uv/) — Python package manager

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- [Claude Desktop](https://claude.ai/download)

## Quick Start

```bash
cd mcp
uv sync
```

Then add the server to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "fsq-places": {
      "command": "/ABSOLUTE/PATH/TO/mcp/.venv/bin/python",
      "args": ["-m", "fsq_places.server"],
      "env": {
        "AWS_SKIP_SIGNATURE": "true",
        "AWS_DEFAULT_REGION": "us-east-1"
      }
    }
  }
}
```

Replace `/ABSOLUTE/PATH/TO/mcp` with your actual project path. Then restart Claude Desktop (Cmd+Q on macOS, not just close the window).

Note: For Windows in the "command" line change the `bin` folder name to `Scripts` (ex. `"/ABSOLUTE/PATH/TO/mcp/.venv/Scripts/python"`)

Verify: click the "+" icon in Claude Desktop and look for "fsq-places" under **Connectors**.

## How It Works

The server exposes two tools via the MCP protocol:

### `search_places`

Search for places by name or category within a geographic bounding box.

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search term to match against place names or categories |
| `min_lat` | float | Minimum latitude (south boundary) |
| `min_lon` | float | Minimum longitude (west boundary) |
| `max_lat` | float | Maximum latitude (north boundary) |
| `max_lon` | float | Maximum longitude (east boundary) |
| `limit` | int | Maximum results to return (default: 50) |

Returns: JSON array of places with name, categories, address, and coordinates.

### `get_place_categories`

List unique place categories within a geographic bounding box.

| Parameter | Type | Description |
|-----------|------|-------------|
| `min_lat` | float | Minimum latitude (south boundary) |
| `min_lon` | float | Minimum longitude (west boundary) |
| `max_lat` | float | Maximum latitude (north boundary) |
| `max_lon` | float | Maximum longitude (east boundary) |
| `limit` | int | Maximum categories to return (default: 100) |

Returns: JSON array of categories with counts, sorted by frequency.

### Data flow

```
Claude Desktop question → Claude determines bounding box →
  MCP tool call → SedonaDB spatial SQL on S3 data → JSON results →
  Claude presents in natural language
```

On first query, the server loads Foursquare data from S3 into memory (30-60 seconds). Subsequent queries are fast.

## Example Usage

| Prompt | What happens |
|--------|-------------|
| "Find coffee shops in Manhattan" | Claude calls `search_places` with query="coffee" and Manhattan's bounding box |
| "What types of places are in downtown San Francisco?" | Claude calls `get_place_categories` with SF's bounding box |
| "Search for restaurants near Times Square, New York" | Claude calls `search_places` with query="restaurant" |
| "List all categories of businesses in the Las Vegas strip area" | Claude calls `get_place_categories` with Las Vegas coordinates |

**Tips:**
- Be specific about the location (city, neighborhood, or landmarks)
- You can ask follow-up questions like "Show me more" or "What about pizza places?"
- Only currently open places are returned (closed venues are filtered out)

## Project Structure

```
mcp/
├── pyproject.toml              # Project configuration
├── uv.lock                     # Dependency lock file
├── README.md
└── src/
    └── fsq_places/
        ├── __init__.py
        └── server.py           # MCP server implementation
```

### Data source

[Foursquare Open Source Places](https://docs.foursquare.com/data-products/docs/access-fsq-os-places) dataset, accessed from the public S3 bucket `s3://fsq-os-places-us-east-1/`. Includes place names, category labels, coordinates (WGS84), addresses, contact details, and activity status. Licensed under Apache 2.0.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Server not appearing in Claude Desktop | Check config JSON syntax, use absolute paths, restart Claude Desktop (Cmd+Q) |
| "Current directory does not exist" | Use the full Python path: `/path/to/mcp/.venv/bin/python` with args `["-m", "fsq_places.server"]` |
| Server connects then disconnects | Check `tail -f ~/Library/Logs/Claude/mcp-server-fsq-places.log` |
| Import errors | Run `cd mcp && uv sync` |
| First query slow (30-60s) | Normal — data loads from S3 on first use. Subsequent queries are fast |

### Checking logs

```bash
tail -f ~/Library/Logs/Claude/mcp.log                        # General MCP logs
tail -f ~/Library/Logs/Claude/mcp-server-fsq-places.log      # Server-specific logs
```

### Local testing (without Claude Desktop)

```bash
cd mcp
uv run fsq-places                          # Run server directly
uv run mcp dev src/fsq_places/server.py    # MCP Inspector web UI
```

## License

MIT

## References

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [SedonaDB Documentation](https://sedona.apache.org/sedonadb/)
- [Foursquare Open Source Places](https://docs.foursquare.com/data-products/docs/access-fsq-os-places)
