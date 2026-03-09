# Geospatial AI Agent Demo

An AI agent that queries 100M+ commercial POIs from Foursquare Open Places using natural language, with human-in-the-loop approval and automatic data export.

## Overview

This Jupyter notebook demonstrates how AI agents can power enterprise retail site selection and competitive analysis using real-world geospatial data:

- **Natural Language Queries** — Ask business questions in plain English about locations
- **Intelligent Data Retrieval** — Agent queries Foursquare Open Places via SedonaDB
- **Human-in-the-Loop** — Approve agent actions before they execute
- **Transparent Reasoning** — See exactly how the AI makes decisions
- **Practical Outputs** — Export data as GeoJSON or CSV for further analysis

## Tech Stack

- [SedonaDB](https://sedona.apache.org/sedonadb/) — Spatial database engine (Rust, Apache Arrow)
- [Foursquare Open Places](https://docs.foursquare.com/data-products/docs/access-fsq-os-places) — 100M+ commercial POIs on AWS S3 (Apache 2.0)
- [LangChain](https://docs.langchain.com/) + [LangGraph](https://langchain-ai.github.io/langgraph/) — AI agent framework
- [Groq](https://groq.com/) — Fast LLM inference (Llama 3.3 70B)
- [GeoParquet](https://geoparquet.org/) — Cloud-native spatial data format

## Prerequisites

- Python 3.10+
- [Groq API key](https://console.groq.com) (free)
- Internet connection (for S3 data access)

## Quick Start

```bash
cd agentic
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
jupyter notebook geospatial_agent_demo.ipynb
```

You'll be prompted for your Groq API key in the notebook.

## How It Works

The agent has three tools defined in `src/tools.py`:

1. **`query_places_by_location`** — Geocodes a location name to a bounding box, requests human approval, then queries Foursquare Open Places via SedonaDB
2. **`analyze_results`** — Performs statistical analysis (summary, count, distribution) on cached query results
3. **`export_results`** — Exports results to GeoJSON or CSV format

The workflow:
```
User question → Agent reasoning → Geocode location → Human approval →
  SedonaDB spatial SQL → Results cached → Analysis / Export
```

Supporting modules:
- `src/database.py` — SedonaDB connection and S3 data loading
- `src/geocoding.py` — Location name to bounding box (via Nominatim)
- `src/approval.py` — Human-in-the-loop approval prompts
- `src/categories.py` — Foursquare category taxonomy search
- `src/logging.py` — Session logging for audit trails

## Example Usage

**Query**: *"Find all grocery stores in Portland, Oregon and analyze the market density"*

```
Agent geocodes "Portland, Oregon" → bounding box [-122.72, 45.48, -122.63, 45.57]
Agent requests approval → user types "yes"
Agent queries SedonaDB → finds 126 grocery stores
Agent analyzes distribution → summarizes market density
Agent exports → portland_grocery_stores.geojson
```

### Example prompts to try

| Prompt | What happens |
|--------|-------------|
| "Find all Coffee Shops in Portland, Oregon" | Queries Foursquare for coffee shops in Portland's bounding box |
| "Find Pharmacies in downtown Portland and analyze the distribution" | Queries + runs distribution analysis |
| "Find Grocery Stores in Seattle and export to CSV" | Queries Seattle + exports CSV file |
| "Find Banks in Portland, Oregon and analyze the market" | Financial services competitive analysis |

### Foursquare categories

Use human-readable labels like `Grocery Store`, `Coffee Shop`, `Bank`. Explore with:
```python
search_categories('grocery')
browse_categories_by_prefix('Retail')
```

Common categories: `Grocery Store`, `Supermarket`, `Pharmacy`, `Coffee Shop`, `Restaurant`, `Fast Food Restaurant`, `Bank`, `Gas Station`, `Hospital`, `Shopping Mall`

## Project Structure

```
agentic/
├── geospatial_agent_demo.ipynb   # Main notebook
├── requirements.txt              # Python dependencies
├── logs/                         # Agent session logs (JSON)
└── src/
    ├── __init__.py
    ├── database.py               # SedonaDB connection + S3 data loading
    ├── tools.py                  # LangChain agent tools
    ├── approval.py               # Human-in-the-loop approval
    ├── geocoding.py              # Location name → bounding box
    ├── categories.py             # Foursquare category taxonomy
    └── logging.py                # Session logging
```

### Output files

- `*.geojson` — Open in QGIS, ArcGIS, or [geojson.io](https://geojson.io)
- `*.csv` — Open in Excel or Google Sheets
- `logs/*.json` — Complete agent reasoning audit trail

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'sedona'` | Run `pip install -r requirements.txt` and activate your venv |
| Groq API error | Verify your key at [console.groq.com](https://console.groq.com). Model used: `llama-3.3-70b-versatile` |
| AWS Access Denied | Setup auto-sets `AWS_SKIP_SIGNATURE=true`. No AWS account needed |
| No data returned | Check bounding box coordinates. Use `search_categories()` to find the right category name |
| Agent doesn't ask for approval | Verify `human_approval()` in `src/approval.py` is being called |
| First query takes 30-60 seconds | Normal — SedonaDB loads data from S3 on first query. Subsequent queries are fast |

## License

- Foursquare Open Places data: Apache License 2.0
- Apache Sedona: Apache License 2.0
- LangChain: MIT License

## References

- [Foursquare Open Places Documentation](https://docs.foursquare.com/data-products/docs/access-fsq-os-places)
- [Foursquare Open Places on HuggingFace](https://huggingface.co/datasets/foursquare/fsq-os-places)
- [SedonaDB Documentation](https://sedona.apache.org/sedonadb/)
- [LangChain Docs](https://docs.langchain.com/)
- [GeoJSON Specification](https://geojson.org/)
