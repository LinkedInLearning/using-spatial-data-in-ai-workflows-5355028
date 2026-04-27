"""
Database Connection and Setup

This module handles SedonaDB connection and Foursquare Open Places data loading.
SedonaDB is a high-performance spatial database built on Rust and Apache Arrow.
"""

import os
import sedona.db


def setup_database(fsq_release: str = "2025-02-06") -> tuple:
    """
    Set up SedonaDB connection and load Foursquare Open Places data.

    This function:
    1. Configures AWS environment for public S3 access
    2. Connects to SedonaDB
    3. Loads Foursquare OS Places data from S3
    4. Registers it as the 'places' view for fast queries

    The Foursquare category taxonomy is provided separately via
    categories.load_categories() (sourced from categories_taxonomy.py),
    since the source.coop release does not ship a categories file and
    deriving one from places at startup is prohibitively slow.

    Args:
        fsq_release: The Foursquare release date (default: "2025-02-06")

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
    os.environ["AWS_DEFAULT_REGION"] = "us-west-2"

    # Connect to SedonaDB
    sd = sedona.db.connect()
    print("SedonaDB connected successfully!")

    # Build the Foursquare S3 paths
    FSQ_BASE_PATH = f"s3://us-west-2.opendata.source.coop/fused/fsq-os-places/{fsq_release}"
    places_path = f"{FSQ_BASE_PATH}/places/"

    print(f"\nLoading Foursquare Open Places data from S3...")
    print(f"   Places: {places_path}")

    # Read the places parquet files and create a view
    places_df = sd.read_parquet(places_path)
    places_df.to_view("places")
    print("Places data loaded and registered as 'places' view")

    return sd, places_df, FSQ_BASE_PATH


def get_places_schema(places_df) -> None:
    """
    Display the schema of the places table.

    Args:
        places_df: SedonaDataFrame with places data
    """
    print("\nPlaces table schema:")
    print(places_df.schema)
