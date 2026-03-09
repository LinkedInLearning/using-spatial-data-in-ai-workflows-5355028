"""
Geospatial AI Agent - Source Package

This package contains the core functionality for the Geospatial AI Agent demo
using Foursquare Open Places data and SedonaDB.

Example:
    from src import setup_database, create_agent_tools, AgentLogger

Modules:
    - database: SedonaDB connection and Foursquare Open Places data loading
    - tools: LangChain tools for querying and analyzing geospatial data
    - geocoding: Convert location names to coordinates using Nominatim
    - categories: Foursquare category taxonomy utilities
    - logging: Agent logging system for tracking actions and reasoning
    - approval: Human-in-the-loop approval for agent actions
"""

from .database import setup_database, get_places_schema
from .tools import create_agent_tools, get_cached_results, clear_cache
from .geocoding import get_bounding_box
from .categories import (
    load_categories,
    search_categories,
    browse_categories_by_prefix,
    get_popular_categories,
    reset_categories
)
from .logging import AgentLogger
from .approval import human_approval

__all__ = [
    # Database
    'setup_database',
    'get_places_schema',
    # Tools
    'create_agent_tools',
    'get_cached_results',
    'clear_cache',
    # Geocoding
    'get_bounding_box',
    # Categories
    'load_categories',
    'search_categories',
    'browse_categories_by_prefix',
    'get_popular_categories',
    'reset_categories',
    # Logging
    'AgentLogger',
    # Approval
    'human_approval',
]
