"""
Foursquare Open Places MCP Server

This MCP server allows Claude to query Foursquare Open Source Places data
using SedonaDB as an in-memory spatial database.
"""

import json
import logging
import os
import sys

# Configure logging to stderr (NEVER use print() for STDIO servers)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("fsq-places-mcp")

# Configure AWS environment for anonymous S3 access to FSQ Open Places data
os.environ["AWS_SKIP_SIGNATURE"] = "true"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

import sedona.db
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("fsq-places")

# Global database connection (lazy initialization)
_db_connection = None
_data_loaded = False


def get_db():
    """Get or create SedonaDB connection."""
    global _db_connection
    if _db_connection is None:
        logger.info("Connecting to SedonaDB...")
        _db_connection = sedona.db.connect()
    return _db_connection


def ensure_data_loaded():
    """Load Foursquare Open Places data into memory table if not already loaded."""
    global _data_loaded
    if _data_loaded:
        return

    sd = get_db()
    logger.info("Loading Foursquare Open Places data from S3 (this may take a moment)...")

    # Read parquet data from Foursquare Open Places S3 bucket
    # Data is licensed under Apache 2.0 - Copyright 2024 Foursquare Labs, Inc.
    # Check releases at: https://docs.foursquare.com/data-products/docs/access-fsq-os-places
    df = sd.read_parquet(
        "s3://fsq-os-places-us-east-1/release/dt=2025-09-09/places/parquet/"
    )

    # Register as a named view for SQL queries
    df.to_view("places", overwrite=True)
    logger.info("Places data loaded and registered as view")
    _data_loaded = True


@mcp.tool()
def search_places(
    query: str,
    min_lat: float,
    min_lon: float,
    max_lat: float,
    max_lon: float,
    limit: int = 50,
) -> str:
    """
    Search for places by name or category within a geographic bounding box.

    Args:
        query: Search term to match against place names or categories
        min_lat: Minimum latitude (south boundary) of the search area
        min_lon: Minimum longitude (west boundary) of the search area
        max_lat: Maximum latitude (north boundary) of the search area
        max_lon: Maximum longitude (east boundary) of the search area
        limit: Maximum number of results to return (default 50)

    Returns:
        JSON string containing list of matching places with name, categories, address, and coordinates
    """
    ensure_data_loaded()
    sd = get_db()

    search_pattern = f"%{query}%"

    sql = f"""
    SELECT
        fsq_place_id,
        name,
        latitude,
        longitude,
        address,
        locality,
        region,
        country,
        fsq_category_labels
    FROM places
    WHERE latitude BETWEEN {min_lat} AND {max_lat}
      AND longitude BETWEEN {min_lon} AND {max_lon}
      AND date_closed IS NULL
      AND (
          name ILIKE '{search_pattern}'
          OR array_to_string(fsq_category_labels, '||') ILIKE '{search_pattern}'
      )
    LIMIT {limit}
    """

    logger.info(f"Executing search_places query for: {query}")
    logger.info(f"SQL: {sql}")

    try:
        result = sd.sql(sql)
        rows = result.to_pandas().to_dict(orient="records")

        if not rows:
            return f"No places found matching '{query}' in the specified area."

        # Convert category arrays to lists for clean JSON output
        for row in rows:
            if row.get("fsq_category_labels") is not None:
                row["fsq_category_labels"] = list(row["fsq_category_labels"])

        return json.dumps(rows, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error in search_places: {e}")
        return f"Error searching places: {str(e)}"


@mcp.tool()
def get_place_categories(
    min_lat: float,
    min_lon: float,
    max_lat: float,
    max_lon: float,
    limit: int = 100,
) -> str:
    """
    List all unique place categories within a geographic bounding box.

    Args:
        min_lat: Minimum latitude (south boundary) of the search area
        min_lon: Minimum longitude (west boundary) of the search area
        max_lat: Maximum latitude (north boundary) of the search area
        max_lon: Maximum longitude (east boundary) of the search area
        limit: Maximum number of categories to return (default 100)

    Returns:
        JSON string containing list of unique categories with counts
    """
    ensure_data_loaded()
    sd = get_db()

    sql = f"""
    SELECT
        category,
        COUNT(*) AS count
    FROM (
        SELECT UNNEST(fsq_category_labels) AS category
        FROM places
        WHERE latitude BETWEEN {min_lat} AND {max_lat}
          AND longitude BETWEEN {min_lon} AND {max_lon}
          AND date_closed IS NULL
          AND fsq_category_labels IS NOT NULL
    )
    GROUP BY category
    ORDER BY count DESC
    LIMIT {limit}
    """

    logger.info("Executing get_place_categories query")

    try:
        result = sd.sql(sql)
        rows = result.to_pandas().to_dict(orient="records")

        if not rows:
            return "No categories found in the specified area."

        return json.dumps(rows, indent=2)
    except Exception as e:
        logger.error(f"Error in get_place_categories: {e}")
        return f"Error getting categories: {str(e)}"


def main():
    """Run the MCP server."""
    logger.info("Starting Foursquare Open Places MCP Server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
