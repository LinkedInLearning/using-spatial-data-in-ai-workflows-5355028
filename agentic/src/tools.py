"""
Agent Tools for Geospatial Queries

This module provides LangChain tools for querying and analyzing Foursquare
Open Places data via SedonaDB.

Foursquare schema (flat columns):
  - fsq_place_id: Unique place identifier
  - name: Place name
  - latitude / longitude: WGS84 coordinates
  - address, locality, region, postcode, country: Address fields
  - fsq_category_ids: Array of category IDs
  - fsq_category_labels: Array of category label strings
  - date_closed: NULL if still open
  - date_refreshed: Last update date
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime
from langchain.tools import tool

from .geocoding import get_bounding_box
from .approval import human_approval
from .categories import load_categories


# Global cache to store query results for other tools to access
query_results_cache = {}

# Module-level variables for database connection and categories
# These are set by create_agent_tools()
_sd = None
_categories_df = None


def create_agent_tools(sd, categories_df=None):
    """
    Create and configure the agent tools with database connection.

    This function initializes the tools with the required database connection
    and categories dataframe, then returns the list of tools for the agent.

    Args:
        sd: SedonaDB connection object
        categories_df: DataFrame with Foursquare categories (optional, auto-loads if not provided)

    Returns:
        List of configured LangChain tools

    Example:
        sd, places_df, base_path = setup_database()
        categories_df = load_categories(sd)
        tools = create_agent_tools(sd, categories_df)
    """
    global _sd, _categories_df

    _sd = sd
    _categories_df = categories_df if categories_df is not None else load_categories(sd)

    return [query_places_by_location, analyze_results, export_results]


@tool
def query_places_by_location(location_name: str, category: str) -> str:
    """
    Query Foursquare Open Places for points of interest in a specific location.

    Args:
        location_name: City or area name (e.g., 'Seattle', 'downtown Paris')
        category: Type of place to find (e.g., 'Coffee Shop', 'Restaurant', 'Bank')

    Returns:
        String summary of results with count and sample data
    """
    global _sd, _categories_df, query_results_cache

    if _sd is None:
        return "Error: Database not initialized. Call create_agent_tools() first."

    # Step 0: Check category against taxonomy
    print(f"\nSearching for category: '{category}'")

    if _categories_df is not None and len(_categories_df) > 0:
        matches = _categories_df[
            _categories_df['category_name'].str.contains(category, case=False, na=False)
        ]
        if len(matches) > 0:
            print(f"Found {len(matches)} matching categories in taxonomy")
            if len(matches) <= 5:
                for _, row in matches.iterrows():
                    print(f"   - {row['category_name']}")
        else:
            print(f"Warning: Category '{category}' not found in taxonomy - will search labels anyway")

    # Step 1: Convert location name to bounding box coordinates
    print(f"\nLooking up coordinates for '{location_name}'...")
    bbox = get_bounding_box(location_name)

    if not bbox:
        return f"Could not find location: {location_name}"

    print(f"Found: {bbox['location_name']}")
    print(f"Bounding box: [{bbox['min_lon']:.4f}, {bbox['min_lat']:.4f}, {bbox['max_lon']:.4f}, {bbox['max_lat']:.4f}]")

    # Step 2: Ask human for approval before querying
    approved = human_approval(
        f"Query Foursquare Open Places for '{category}' in {location_name}",
        f"Area: {bbox['location_name']}\nCategory: {category}\nBounding box: {bbox['min_lon']:.4f}, {bbox['min_lat']:.4f}, {bbox['max_lon']:.4f}, {bbox['max_lat']:.4f}"
    )

    if not approved:
        return "Query cancelled by user."

    # Step 3: Construct SQL query
    # Foursquare uses flat columns: latitude, longitude, name, fsq_category_labels (array)
    # Filter by bounding box on lat/lon and search category labels array
    print(f"\nExecuting query on Foursquare Open Places via SedonaDB...")

    query = f"""
SELECT DISTINCT
        fsq_place_id,
        name,
        latitude,
        longitude,
        address,
        locality,
        region,
        country,
        fsq_category_labels
    FROM (
        SELECT
            fsq_place_id,
            name,
            latitude,
            longitude,
            address,
            locality,
            region,
            country,
            fsq_category_labels,
            unnest(fsq_category_labels) AS category_label
        FROM places
        WHERE latitude BETWEEN {bbox['min_lat']} AND {bbox['max_lat']}
        AND longitude BETWEEN {bbox['min_lon']} AND {bbox['max_lon']}
        AND date_closed IS NULL
    )
    WHERE category_label ILIKE '%{category}%'
    LIMIT 500
    """

    # Log the actual SQL query
    print("\nSQL Query:")
    print("=" * 70)
    print(query)
    print("=" * 70)

    try:
        # Execute query via SedonaDB
        result = _sd.sql(query)
        df = result.to_pandas()

        # Store results for other tools to use
        query_results_cache['latest'] = df
        query_results_cache['location'] = location_name
        query_results_cache['category'] = category

        count = len(df)
        print(f"\nQuery complete! Found {count} places.")

        if count == 0:
            return f"No '{category}' places found in {location_name}. Try search_categories('{category}') to find the right category name."

        # Create summary with sample data
        summary = f"Found {count} '{category}' places in {location_name}.\n\n"
        summary += "Sample results:\n"

        for idx, row in df.head(5).iterrows():
            name = row['name'] if pd.notna(row['name']) else 'Unnamed'
            addr = row['address'] if pd.notna(row['address']) else ''
            locality = row['locality'] if pd.notna(row['locality']) else ''
            loc_str = f", {locality}" if locality else ""
            addr_str = f" - {addr}{loc_str}" if addr else ""
            summary += f"  - {name}{addr_str}\n"

        if count > 5:
            summary += f"\n  ... and {count - 5} more places."

        return summary

    except Exception as e:
        error_msg = f"Error querying Foursquare Open Places: {str(e)}"
        print(f"Error: {error_msg}")
        return error_msg


@tool
def analyze_results(analysis_type: str = "summary") -> str:
    """
    Analyze the results from the most recent query.

    Args:
        analysis_type: Type of analysis - 'summary', 'count', or 'distribution'

    Returns:
        String with analysis results
    """
    global query_results_cache

    # Check if we have results to analyze
    if 'latest' not in query_results_cache:
        return "No query results available to analyze. Please run a query first."

    df = query_results_cache['latest']
    location = query_results_cache.get('location', 'unknown location')
    category = query_results_cache.get('category', 'unknown category')

    print(f"\nAnalyzing {len(df)} results...")

    if analysis_type == "count":
        result = f"Total '{category}' places found in {location}: {len(df)}"

    elif analysis_type == "distribution":
        result = f"Analysis of {len(df)} '{category}' places in {location}:\n\n"

        named_count = df['name'].notna().sum()
        result += f"  - Places with names: {named_count} ({named_count/len(df)*100:.1f}%)\n"

        if 'address' in df.columns:
            addr_count = df['address'].notna().sum()
            result += f"  - Places with addresses: {addr_count} ({addr_count/len(df)*100:.1f}%)\n"

        if 'locality' in df.columns:
            localities = df['locality'].dropna().value_counts().head(5)
            if len(localities) > 0:
                result += "\n  Top localities:\n"
                for loc, count in localities.items():
                    result += f"    - {loc}: {count} places\n"

    else:  # summary
        result = f"Summary of '{category}' places in {location}:\n\n"
        result += f"  Total found: {len(df)}\n"

        named = df['name'].notna().sum()
        result += f"  With names: {named} ({named/len(df)*100:.1f}%)\n"

        if 'address' in df.columns:
            addressed = df['address'].notna().sum()
            result += f"  With addresses: {addressed} ({addressed/len(df)*100:.1f}%)\n"

        result += "\n  Most common names:\n"
        name_counts = df['name'].value_counts().head(3)
        for name, count in name_counts.items():
            result += f"    - {name}: {count} location(s)\n"

        if 'country' in df.columns:
            countries = df['country'].dropna().unique()
            if len(countries) > 0:
                result += f"\n  Countries: {', '.join(str(c) for c in countries[:5])}\n"

    print("Analysis complete!")
    return result


@tool
def export_results(format_type: str = "geojson", filename: str = "") -> str:
    """
    Export the most recent query results to a file.

    Args:
        format_type: Output format - 'geojson' or 'csv'
        filename: Optional custom filename (auto-generated if not provided)

    Returns:
        Success message with filename
    """
    global query_results_cache

    if 'latest' not in query_results_cache:
        return "No query results available to export. Please run a query first."

    df = query_results_cache['latest'].copy()
    location = query_results_cache.get('location', 'unknown')
    category = query_results_cache.get('category', 'places')

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_location = location.replace(" ", "_").replace(",", "")[:20]
        safe_category = category.replace(" ", "_")[:20]
        filename = f"{safe_category}_{safe_location}_{timestamp}"

    print(f"\nExporting {len(df)} results to {format_type.upper()}...")

    try:
        if format_type.lower() == "geojson":
            # Foursquare has latitude/longitude columns - create Point geometries
            geometry = [
                Point(row['longitude'], row['latitude'])
                if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude'))
                else None
                for _, row in df.iterrows()
            ]

            # Convert fsq_category_labels array to string for GeoJSON compatibility
            if 'fsq_category_labels' in df.columns:
                df['fsq_category_labels'] = df['fsq_category_labels'].apply(
                    lambda x: ', '.join(x) if isinstance(x, (list, tuple)) else str(x) if x is not None else ''
                )

            # Drop lat/lon since they're in the geometry now
            export_df = df.drop(['latitude', 'longitude'], axis=1, errors='ignore')

            gdf = gpd.GeoDataFrame(export_df, geometry=geometry, crs='EPSG:4326')
            gdf = gdf[gdf.geometry.notna()]

            output_path = f"{filename}.geojson"
            gdf.to_file(output_path, driver='GeoJSON')

            print(f"GeoJSON saved: {output_path}")
            return f"Successfully exported {len(gdf)} places to {output_path}. You can open this file in QGIS, ArcGIS, or at geojson.io"

        elif format_type.lower() == "csv":
            # Convert fsq_category_labels array to string for CSV
            if 'fsq_category_labels' in df.columns:
                df['fsq_category_labels'] = df['fsq_category_labels'].apply(
                    lambda x: ', '.join(x) if isinstance(x, (list, tuple)) else str(x) if x is not None else ''
                )

            output_path = f"{filename}.csv"
            df.to_csv(output_path, index=False)

            print(f"CSV saved: {output_path}")
            return f"Successfully exported {len(df)} places to {output_path}. You can open this in Excel or Google Sheets."

        else:
            return f"Unsupported format: {format_type}. Use 'geojson' or 'csv'."

    except Exception as e:
        error_msg = f"Error exporting data: {str(e)}"
        print(f"Error: {error_msg}")
        import traceback
        print(traceback.format_exc())
        return error_msg


def get_cached_results():
    """Get the cached query results."""
    return query_results_cache.copy()


def clear_cache():
    """Clear the query results cache."""
    global query_results_cache
    query_results_cache = {}
    print("Query cache cleared")
