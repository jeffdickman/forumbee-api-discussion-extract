"""
Forumbee API Categories Fetch Script

This script fetches all categories from the Forumbee API and displays their details.
It uses the API token and domain from config.py.

Usage:
    python get-categories.py
"""

import requests
from config import API_TOKEN, DOMAIN

def get_all_categories():
    """
    Fetch all categories from the Forumbee API.
    
    Returns:
        list: List of category dictionaries containing category details
    """
    # Construct the base URL for the API v2 endpoint
    base_url = f"https://{DOMAIN}/api/2"
    url = f"{base_url}/categories"
    
    print(f"Making request to: {url}")
    
    # Set up the request headers with authentication
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    params = {
        "output": "json",  # Ensure response is in JSON format
        "limit": 1000      # Maximum allowed by API
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Response status code: {response.status_code}")
        
        # Print response headers for debugging
        print("\nResponse headers:")
        for key, value in response.headers.items():
            print(f"{key}: {value}")
        
        response.raise_for_status()
        
        # Print raw response for debugging
        print("\nRaw response:")
        print(response.text)
        
        data = response.json()
        print("\nParsed JSON response:")
        print(data)
        
        categories = data.get("categories", [])
        if not categories:
            print("\nWarning: No categories found in response")
            print("Available keys in response:", list(data.keys()))
        
        return categories
    except requests.exceptions.HTTPError as http_err:
        print(f"\nHTTP error occurred: {http_err.response.status_code}")
        print(f"Error response: {http_err.response.text}")
        return []
    except requests.exceptions.RequestException as req_err:
        print(f"\nRequest error occurred: {req_err}")
        return []
    except Exception as err:
        print(f"\nUnexpected error occurred: {err}")
        return []

if __name__ == "__main__":
    print("Starting category fetch...")
    categories = get_all_categories()
    
    if categories:
        print("\nFound categories:")
        for category in categories:
            print(f"Name: {category.get('name')}, Type: {category.get('type')}, Key: {category.get('categoryKey')}")
    else:
        print("\nNo categories were returned.")
