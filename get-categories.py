"""
Forumbee API Categories Fetch Script

This script fetches all categories from the Forumbee API and displays their details.
It uses the API token and domain from config.py.

Usage:
    python get-categories.py
"""

import requests
import csv
from io import StringIO
from config import API_TOKEN, DOMAIN

def get_all_categories():
    """
    Fetch all categories from the Forumbee API.
    
    Returns:
        list: List of category dictionaries containing name, type, and path
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
    
    # Define the fields we want to retrieve
    params = {
        "fields": "name,type,path",
        "output": "csv"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Response status code: {response.status_code}")
        
        response.raise_for_status()
        
        # Parse CSV response
        csv_data = StringIO(response.text)
        reader = csv.DictReader(csv_data)
        categories = list(reader)
        
        if not categories:
            print("\nWarning: No categories found in response")
            return []
            
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
            print(f"\nName: {category.get('name', 'N/A')}")
            print(f"Type: {category.get('type', 'N/A')}")
            print(f"Path: {category.get('path', 'N/A')}")
            print("-" * 50)
    else:
        print("\nNo categories were returned.")
