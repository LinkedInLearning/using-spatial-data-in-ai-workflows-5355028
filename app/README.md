# US Airport Explorer

An AI-powered interactive map that lets you explore 150 US airports using natural language. Built with MapLibre GL JS and Groq.

## Overview

A zero-dependency web app where an AI controls an interactive map through function calling:

- **Interactive Map** — 150 airports across 49 US states and territories on a dark Carto basemap, color-coded by type (red = large, orange = medium, teal = small)
- **Filter Widgets** — Airport type checkboxes, state code filter with autocomplete, and elevation range sliders
- **AI Chat** — Right panel powered by Groq (Llama 3.3 70B). Ask questions in plain English and the AI pans the map, applies filters, and updates widgets
- **Thought Log** — Every AI action is logged as an expandable "Thinking" block showing the raw tool calls
- **Bidirectional Sync** — Manual widget changes and AI commands both go through the same filter engine

## Tech Stack

- [MapLibre GL JS](https://maplibre.org/) — Open-source map rendering (loaded via CDN)
- [Groq](https://groq.com/) — Fast LLM inference (Llama 3.3 70B with tool use)
- [Carto](https://carto.com/basemaps/) — Dark Matter basemap tiles
- No build tools, no frameworks — plain HTML/CSS/JS

## Prerequisites

- Any modern web browser
- Python 3+ (just to run a local HTTP server)
- [Groq API key](https://console.groq.com) (free)

## Quick Start

```bash
cd app
python3 -m http.server 8080
```

1. Open **http://localhost:8080** in your browser
2. Paste your **Groq API key** into the input in the chat panel and click **Save**
3. Start chatting

## How It Works

The app defines three tools for Groq function calling:

- **`move_map`** — Flies the map to a latitude/longitude at a given zoom level
- **`filter_airports`** — Sets airport type, state, and elevation filters (also updates the sidebar widgets)
- **`reset_filters`** — Clears all filters and zooms back to the full US view

When the AI responds with tool calls, the app executes them, sends the results back to Groq, and then displays the final natural language summary. The chat loop supports up to 5 tool-call iterations per message.

## Example Usage

| Prompt | What happens |
|--------|-------------|
| "Show me large airports in California" | Map flies to CA, filters to large airports in CA |
| "Fly me to Alaska" | Map pans to Alaska, filters by state AK |
| "Which airports are above 5,000 ft?" | Sets elevation min slider to 5,000 ft |
| "Only show small airports" | Unchecks large and medium, checks small |
| "Show me airports in Hawaii" | Map flies to Hawaii, filters by state HI |
| "Reset all filters" | Clears everything back to defaults |

## Project Structure

```
app/
├── index.html    # Page layout (sidebar, map, chat panel)
├── style.css     # Dark theme styling with CSS grid
├── airports.js   # 150 curated US airports as GeoJSON
└── app.js        # Map setup, filter engine, Groq chat with function calling
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Map doesn't load | Make sure you're serving via HTTP (`python3 -m http.server`), not opening the file directly |
| Chat not responding | Check that your Groq API key is saved (top of chat panel) |
| "Failed to fetch" errors | Verify your internet connection and that the Groq API is reachable |

## License

MIT

## References

- [MapLibre GL JS](https://maplibre.org/)
- [Groq API](https://groq.com/)
- [Carto Basemaps](https://carto.com/basemaps/)

## Notes

- The Groq API key is stored in `sessionStorage` (cleared when you close the tab)
- No data is sent to any server other than Groq's API
- The airport dataset is static and embedded in `airports.js`
