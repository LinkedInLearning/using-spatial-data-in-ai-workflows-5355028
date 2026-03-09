"""
Database Connection and Setup

This module handles SedonaDB connection and Foursquare Open Places data loading.
SedonaDB is a high-performance spatial database built on Rust and Apache Arrow.
"""

import os
import sedona.db


def setup_database(fsq_release: str = "2025-09-09") -> tuple:
    """
    Set up SedonaDB connection and load Foursquare Open Places data.

    This function:
    1. Configures AWS environment for public S3 access
    2. Connects to SedonaDB
    3. Loads Foursquare OS Places data from S3
    4. Loads Foursquare categories from S3
    5. Registers both as views for fast queries

    Args:
        fsq_release: The Foursquare release date (default: "2025-09-09")

    Returns:
        tuple: (sd, places_df, FSQ_BASE_PATH)
            - sd: SedonaDB connection object
            - places_df: SedonaDataFrame with places data
            - FSQ_BASE_PATH: S3 path to Foursquare data

    Example:
        sd, places_df, base_path = setup_database()
        result = sd.sql("SELECT COUNT(*) FROM places").show()
    """
    # Configure AWS for public Foursquare data access
    # SKIP_SIGNATURE means no AWS credentials needed - data is public
    os.environ["AWS_SKIP_SIGNATURE"] = "true"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

    # Connect to SedonaDB
    sd = sedona.db.connect()
    print("SedonaDB connected successfully!")

    # Build the Foursquare S3 paths
    FSQ_BASE_PATH = f"s3://fsq-os-places-us-east-1/release/dt={fsq_release}"
    places_path = f"{FSQ_BASE_PATH}/places/parquet/"
    categories_path = f"{FSQ_BASE_PATH}/categories/parquet/"

    print(f"\nLoading Foursquare Open Places data from S3...")
    print(f"   Places: {places_path}")

    # Read the places parquet files and create a view
    places_df = sd.read_parquet(places_path)
    places_df.to_view("places")
    print("Places data loaded and registered as 'places' view")

    # Load the categories table
    print(f"   Categories: {categories_path}")
    categories_df = sd.read_parquet(categories_path)
    categories_df.to_view("categories")
    print("Categories data loaded and registered as 'categories' view")

    return sd, places_df, FSQ_BASE_PATH


def get_places_schema(places_df) -> None:
    """
    Display the schema of the places table.

    Args:
        places_df: SedonaDataFrame with places data
    """
    print("\nPlaces table schema:")
    print(places_df.schema)
