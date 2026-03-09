"""
Foursquare Category Utilities

This module provides functions for searching and browsing the Foursquare
place category taxonomy. The taxonomy is hierarchical with up to 6 levels.

Foursquare categories use human-readable labels like:
  "Dining and Drinking > Restaurant > Italian Restaurant"

The categories table has columns:
  - category_id: Unique BSON identifier
  - category_name: Most specific category name
  - category_label: Full hierarchy using " > " separators
  - category_level: Depth in hierarchy (1-6)
  - level1_category_id/name through level6_category_id/name
"""

import pandas as pd

# Module-level SedonaDB connection (set by load_categories)
_sd = None
_categories_df = None


def load_categories(sd=None) -> pd.DataFrame:
    """
    Load the Foursquare category taxonomy from the registered SedonaDB view.

    The categories are loaded from the 'categories' view that was registered
    by setup_database(). If no SedonaDB connection is provided, returns
    a DataFrame of popular categories as a fallback.

    Args:
        sd: SedonaDB connection object (optional, uses cached if available)

    Returns:
        DataFrame with category taxonomy

    Example:
        categories_df = load_categories(sd)
        print(f"Loaded {len(categories_df)} categories")
    """
    global _sd, _categories_df

    if _categories_df is not None:
        return _categories_df

    if sd is not None:
        _sd = sd

    if _sd is not None:
        try:
            result = _sd.sql("""
                SELECT category_id, category_name, category_label, category_level
                FROM categories
            """)
            _categories_df = result.to_pandas()
            print(f"Loaded {len(_categories_df)} categories from Foursquare taxonomy")
            return _categories_df
        except Exception as e:
            print(f"Warning: Could not load categories from SedonaDB: {e}")

    # Fallback: return empty DataFrame with expected columns
    print("Warning: Categories not loaded. Call setup_database() first.")
    _categories_df = pd.DataFrame(columns=['category_id', 'category_name', 'category_label', 'category_level'])
    return _categories_df


def search_categories(keyword: str, categories_df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Search for place categories containing a keyword.

    Searches both the category_name and category_label fields.

    Args:
        keyword: Search term (e.g., 'coffee', 'restaurant', 'bank')
        categories_df: DataFrame with categories (optional, auto-loads if not provided)

    Returns:
        DataFrame with matching categories

    Example:
        matches = search_categories('coffee')
        # Found 3 categories matching 'coffee':
        #   - Coffee Shop (Dining and Drinking > Cafe, Coffee, and Tea House > Coffee Shop)
    """
    if categories_df is None:
        categories_df = load_categories()

    if len(categories_df) == 0:
        print("No categories loaded. Run setup_database() first.")
        return categories_df

    matches = categories_df[
        categories_df['category_name'].str.contains(keyword, case=False, na=False) |
        categories_df['category_label'].str.contains(keyword, case=False, na=False)
    ]

    if len(matches) == 0:
        print(f"No categories found matching '{keyword}'")
        return matches

    print(f"Found {len(matches)} categories matching '{keyword}':\n")
    for _, row in matches.iterrows():
        label = row.get('category_label', '')
        print(f"  - {row['category_name']} ({label})")

    return matches


def browse_categories_by_prefix(
    prefix: str = 'Dining and Drinking',
    max_results: int = 50,
    categories_df: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Browse categories by top-level label prefix.

    Common prefixes:
    - Dining and Drinking: Restaurants, cafes, bars
    - Arts and Entertainment: Museums, theaters, venues
    - Retail: Stores, shops, markets
    - Health and Medicine: Hospitals, clinics, pharmacies
    - Education: Schools, universities, libraries
    - Travel and Transportation: Hotels, airports
    - Business and Professional Services: Banks, offices

    Args:
        prefix: Category label prefix to filter by
        max_results: Maximum number of results to display
        categories_df: DataFrame with categories (optional)

    Returns:
        DataFrame with matching categories

    Example:
        matches = browse_categories_by_prefix('Retail')
    """
    if categories_df is None:
        categories_df = load_categories()

    if len(categories_df) == 0:
        print("No categories loaded. Run setup_database() first.")
        return categories_df

    matches = categories_df[
        categories_df['category_label'].str.startswith(prefix, na=False)
    ]

    print(f"Found {len(matches)} categories in '{prefix}':\n")
    for _, row in matches.head(max_results).iterrows():
        print(f"  - {row['category_name']} ({row['category_label']})")

    if len(matches) > max_results:
        print(f"\n  ... and {len(matches) - max_results} more")

    return matches


def get_popular_categories() -> dict:
    """
    Get a dictionary of popular categories by theme.

    Returns:
        Dictionary mapping themes to lists of popular category names

    Example:
        popular = get_popular_categories()
        print(popular['food'])  # ['Restaurant', 'Coffee Shop', ...]
    """
    return {
        'food': ['Restaurant', 'Coffee Shop', 'Cafe', 'Bar', 'Fast Food Restaurant', 'Bakery', 'Pizza Place'],
        'retail': ['Grocery Store', 'Supermarket', 'Pharmacy', 'Clothing Store', 'Bookstore', 'Shopping Mall'],
        'services': ['Bank', 'ATM', 'Post Office', 'Gas Station', 'Laundromat'],
        'health': ['Hospital', 'Doctor', 'Dentist', 'Veterinarian', 'Urgent Care Center'],
        'education': ['School', 'University', 'Library'],
        'recreation': ['Park', 'Museum', 'Movie Theater', 'Gym', 'Stadium'],
        'lodging': ['Hotel', 'Hostel', 'Bed and Breakfast'],
    }


def reset_categories():
    """Reset the cached categories so they can be reloaded."""
    global _categories_df, _sd
    _categories_df = None
    _sd = None
