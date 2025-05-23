"""
Forumbee API Post Text Extraction Script

This script fetches post content from the Forumbee API and saves it to CSV files.
It uses the API token and domain from config.py.

Usage:
    python get-post-text.py
"""

import requests
import json
import csv
import os
from datetime import datetime
from io import StringIO
from config import API_TOKEN, DOMAIN

def ensure_output_directory():
    """
    Ensure the outputs directory exists in the current directory.
    """
    output_dir = "./outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

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
        "fields": "name,type,path,categoryKey",
        "output": "csv"  # Request CSV format
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

def get_posts_for_category(category_key):
    """
    Fetch all posts for a specific category using pagination.
    
    Args:
        category_key (str): The key of the category to fetch posts for
        
    Returns:
        list: List of post dictionaries
    """
    base_url = f"https://{DOMAIN}/api/2"
    url = f"{base_url}/posts"
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    all_posts = []
    offset = 0
    limit = 1000  # Maximum allowed per request
    
    while True:
        params = {
            "categoryLink": category_key,
            "fields": "postKey,title,textPlain,category.name,posted,author.name",
            "output": "csv",  # Request CSV format
            "limit": limit,
            "offset": offset,
            "sort": "posted",  # Sort by most recent first
            "textFormat": "plain-truncate-100"  # Get plain text, truncated to 100 chars
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            # Parse CSV response
            csv_data = StringIO(response.text)
            reader = csv.DictReader(csv_data)
            posts = list(reader)
            
            if not posts:
                break
                
            all_posts.extend(posts)
            print(f"Fetched {len(posts)} posts (offset: {offset})")
            
            if len(posts) < limit:
                break
                
            offset += limit
            
        except Exception as err:
            print(f"Error fetching posts for category {category_key} at offset {offset}: {err}")
            break
    
    print(f"Total posts fetched: {len(all_posts)}")
    return all_posts

def save_posts_to_csv(posts, category_name, output_dir):
    """
    Save posts to a CSV file with timestamp.
    
    Args:
        posts (list): List of post dictionaries
        category_name (str): Name of the category
        output_dir (str): Directory to save the CSV file
    """
    if not posts:
        return
    
    # Create a safe filename from the category name
    safe_category_name = "".join(c for c in category_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_category_name = safe_category_name.replace(' ', '_')
    
    # Create timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create filename
    filename = f"{timestamp}_{safe_category_name}_posts.csv"
    filepath = os.path.join(output_dir, filename)
    
    # Write to CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        if posts:
            writer = csv.DictWriter(csvfile, fieldnames=posts[0].keys())
            writer.writeheader()
            writer.writerows(posts)
            print(f"Saved {len(posts)} posts to {filename}")

if __name__ == "__main__":
    print("Starting category and post fetch...")
    
    # Ensure output directory exists
    output_dir = ensure_output_directory()
    
    categories = get_all_categories()
    
    if categories:
        for category in categories:
            category_name = category.get('name', 'N/A')
            category_key = category.get('categoryKey', '')
            category_path = category.get('path', 'N/A')
            
            print("\n" + "=" * 80)
            print(f"Category: {category_name}")
            print(f"Path: {category_path}")
            print("=" * 80)
            
            if category_key:
                posts = get_posts_for_category(category_key)
                if posts:
                    save_posts_to_csv(posts, category_name, output_dir)
                else:
                    print("No posts found in this category")
            else:
                print("No category key available")
    else:
        print("\nNo categories were returned.")
