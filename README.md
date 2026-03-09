# Using Spatial Data in AI Workflows
This is the repository for the LinkedIn Learning course `Using Spatial Data in AI Workflows`. The full course is available from [LinkedIn Learning][lil-course-url].

![lil-thumbnail-url]

## Course Description

Three demo projects showing different patterns for integrating AI with geospatial data — from interactive notebooks to web apps to Claude Desktop integrations.

Each project uses a different architecture but shares a common theme: **making location data accessible through natural language**.

## Projects

### 1. [Agentic](agentic/) — AI Agent with Human-in-the-Loop

A Jupyter notebook that demonstrates an AI agent querying 100M+ commercial POIs from Foursquare Open Places via SedonaDB. The agent reasons through spatial queries, asks for human approval before executing, and exports results as GeoJSON or CSV.

**Stack:** Python, LangChain, Groq, SedonaDB, Jupyter

**Key concepts:** Agent tool calling, human oversight, spatial SQL, bounding box queries, GeoParquet

```
"Find coffee shops in downtown Seattle" →
  Agent geocodes location → Asks for approval → Queries SedonaDB → Exports results
```

### 2. [App](app/) — Interactive Airport Explorer

A zero-dependency web app where an AI controls an interactive map through function calling. Ask questions in plain English and the AI pans the map, applies filters, and updates widgets in real time.

**Stack:** Vanilla JS, MapLibre GL JS, Groq (Llama 3.3 70B), Carto basemaps

**Key concepts:** LLM function calling, bidirectional UI sync, client-side spatial filtering

```
"Show me large airports in California" →
  AI calls move_map() + filter_airports() → Map flies to CA, filters update
```

### 3. [MCP](mcp/) — Foursquare Places Server for Claude Desktop

An MCP (Model Context Protocol) server that gives Claude Desktop the ability to search Foursquare Open Places data. Claude automatically detects when to query the server based on your questions.

**Stack:** Python, FastMCP, SedonaDB, uv

**Key concepts:** MCP protocol, server-based tool integration, lazy data loading, in-memory spatial database

```
"Find restaurants near Times Square" →
  Claude calls search_places() via MCP → SedonaDB queries S3 → Results returned
```

## Shared Technologies

| Technology | What it does | Used in |
|---|---|---|
| [SedonaDB](https://sedona.apache.org/sedonadb/) | High-performance spatial database (Rust, Apache Arrow) | Agentic, MCP |
| [Foursquare Open Places](https://docs.foursquare.com/data-products/docs/access-fsq-os-places) | Open dataset with millions of POIs on S3 | Agentic, MCP |
| [Groq](https://groq.com/) | Fast LLM inference | Agentic, App |
| [MapLibre GL JS](https://maplibre.org/) | Open-source map rendering | App |
| [LangChain](https://docs.langchain.com/) | AI agent framework | Agentic |
| [MCP](https://modelcontextprotocol.io/) | Standardized LLM tool protocol | MCP |

## Prerequisites

### Required for all projects
- **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)
- **Git** — to clone the repository

### API Keys (free)
- **Groq API key** — required for Agentic and App demos. Get a free key at [console.groq.com](https://console.groq.com)

### Per-project requirements

| Requirement | Agentic | App | MCP |
|---|:---:|:---:|:---:|
| Python 3.10+ | Yes | Yes (for local server) | Yes |
| [uv](https://docs.astral.sh/uv/) package manager | — | — | Yes |
| [Groq API key](https://console.groq.com) | Yes | Yes | — |
| [Claude Desktop](https://claude.ai/download) | — | — | Yes |
| Jupyter | Yes (installed via pip) | — | — |
| Internet connection | Yes (S3 data access) | Yes (Groq API) | Yes (S3 data access) |

### Python package highlights

**Agentic** (`pip install -r requirements.txt`):
- `apache-sedona[db]` — SedonaDB spatial database
- `langchain`, `langchain-groq`, `langgraph` — AI agent framework with Groq
- `geopandas`, `geopy` — geospatial data processing and geocoding
- `jupyter` — notebook runtime

**MCP** (`uv sync`):
- `mcp[cli]` — Model Context Protocol SDK
- `apache-sedona[db]` — SedonaDB spatial database

**App** — no install needed. Uses CDN links for MapLibre GL JS. Just serve the files with any HTTP server.

## Quick Start

Each project runs independently. Pick the one that interests you:

### Agentic (Jupyter notebook)

```bash
cd agentic
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
jupyter notebook geospatial_agent_demo.ipynb
```

Requires a Groq API key (entered in the notebook).

### App (Web app)

```bash
cd app
python3 -m http.server 8080
# Open http://localhost:8080
```

Requires a [Groq API key](https://console.groq.com) (entered in the browser).

### MCP (Claude Desktop server)

```bash
cd mcp
uv sync
```

Then add the server to your Claude Desktop config. See [mcp/README.md](mcp/README.md) for full setup instructions.

## Repository Structure

```
ai-geospatial-demos/
├── agentic/
│   ├── geospatial_agent_demo.ipynb   # Main notebook
│   ├── requirements.txt
│   └── src/
│       ├── database.py               # SedonaDB connection
│       ├── tools.py                   # LangChain agent tools
│       ├── approval.py               # Human-in-the-loop
│       ├── geocoding.py              # Location → coordinates
│       ├── categories.py             # Foursquare category taxonomy
│       └── logging.py                # Session logging
├── app/
│   ├── index.html                    # Page layout
│   ├── app.js                        # Map + Groq chat + filters
│   ├── airports.js                   # 150 US airports (GeoJSON)
│   └── style.css                     # Dark theme
└── mcp/
    ├── pyproject.toml
    └── src/fsq_places/
        └── server.py                 # MCP server implementation
```

## Instructions
This repository has branches for each of the videos in the course. You can use the branch pop up menu in github to switch to a specific branch and take a look at the course at that stage, or you can add `/tree/BRANCH_NAME` to the URL to go to the branch you want to access.

## Branches
The branches are structured to correspond to the videos in the course. The naming convention is `CHAPTER#_MOVIE#`. As an example, the branch named `02_03` corresponds to the second chapter and the third video in that chapter. 
Some branches will have a beginning and an end state. These are marked with the letters `b` for "beginning" and `e` for "end". The `b` branch contains the code as it is at the beginning of the movie. The `e` branch contains the code as it is at the end of the movie. The `main` branch holds the final state of the code when in the course.

When switching from one exercise files branch to the next after making changes to the files, you may get a message like this:

    error: Your local changes to the following files would be overwritten by checkout:        [files]
    Please commit your changes or stash them before you switch branches.
    Aborting

To resolve this issue:
	
    Add changes to git using this command: git add .
	Commit changes using this command: git commit -m "some message"

## Instructor

Matt Forrest

Instructor description

Check out my other courses on [LinkedIn Learning](https://www.linkedin.com/learning/instructors/).


[0]: # (Replace these placeholder URLs with actual course URLs)

[lil-course-url]: https://www.linkedin.com/learning/
[lil-thumbnail-url]: https://media.licdn.com/dms/image/v2/D4E0DAQG0eDHsyOSqTA/learning-public-crop_675_1200/B4EZVdqqdwHUAY-/0/1741033220778?e=2147483647&v=beta&t=FxUDo6FA8W8CiFROwqfZKL_mzQhYx9loYLfjN-LNjgA

