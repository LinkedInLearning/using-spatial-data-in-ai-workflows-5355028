"""
Geocoding Utilities

This module provides functions for converting location names to coordinates.
Uses the Nominatim geocoder (free, based on OpenStreetMap data).
"""

from geopy.geocoders import Nominatim


def get_bounding_box(location_name: str, buffer_km: float = 5) -> dict | None:
    """
    Convert a location name into a bounding box.

    A bounding box is a rectangular area defined by four coordinates:
    - Minimum longitude (west edge)
    - Minimum latitude (south edge)
    - Maximum longitude (east edge)
    - Maximum latitude (north edge)

    Args:
        location_name: City or place name (e.g., 'Seattle', 'Paris', 'Tokyo')
        buffer_km: How many kilometers to expand around the center point

    Returns:
        Dictionary with bounding box coordinates and center point, or None if not found

    Example:
        bbox = get_bounding_box("Seattle", buffer_km=5)
        # Returns: {
        #     'min_lon': -122.38...,
        #     'min_lat': 47.56...,
        #     'max_lon': -122.29...,
        #     'max_lat': 47.65...,
        #     'center_lon': -122.34...,
        #     'center_lat': 47.60...,
        #     'location_name': 'Seattle, King County, Washington, USA'
        # }
    """
    # Use Nominatim geocoder (free, based on OpenStreetMap data)
    geolocator = Nominatim(user_agent="geospatial_agent_demo")

    # Look up the location
    location = geolocator.geocode(location_name)

    if not location:
        return None

    # Get center coordinates
    center_lat = location.latitude
    center_lon = location.longitude

    # Calculate approximate buffer in degrees
    # At the equator, 1 degree ≈ 111 km
    # This is a rough calculation for simplicity
    buffer_deg = buffer_km / 111.0

    # Create bounding box
    bbox = {
        'min_lon': center_lon - buffer_deg,
        'min_lat': center_lat - buffer_deg,
        'max_lon': center_lon + buffer_deg,
        'max_lat': center_lat + buffer_deg,
        'center_lon': center_lon,
        'center_lat': center_lat,
        'location_name': location.address
    }

    return bbox
