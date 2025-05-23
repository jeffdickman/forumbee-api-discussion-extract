"""
Forumbee API Categories and Posts Fetch Script

This script fetches all categories from the Forumbee API and their associated posts.
It uses the API token and domain from config.py.

Usage:
    python get-categories-post-list.py
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
        "fields": "name,type,path,categoryKey",
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

def get_posts_for_category(category_key):
    """
    Fetch all posts for a given category.
    
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
    
    # Request all available fields
    params = {
        "categoryLink": category_key,
        "fields": "postKey,parentKey,typeLabel,posted,active,title,postStatus,author.userKey,author.name,author.handle,author.role,author.label,category.name,replyCount,likeCount,viewCount,followCount,url",
        "output": "csv",
        "limit": 1000,  # Maximum allowed by API
        "sort": "posted",  # Sort by most recent first
        "textFormat": "plain-truncate-100",  # Get plain text, truncated to 100 chars
        "includeUnlistedCategories": "false",
        "includeClosedCategories": "false"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        # Parse CSV response
        csv_data = StringIO(response.text)
        reader = csv.DictReader(csv_data)
        posts = list(reader)
        
        return posts
    except Exception as err:
        print(f"Error fetching posts for category {category_key}: {err}")
        return []

def print_post_details(post):
    """
    Print all available fields for a post in a formatted way.
    
    Args:
        post (dict): Dictionary containing post data
    """
    # Group fields by category for better organization
    basic_info = {
        "Title": post.get('title', 'N/A'),
        "Type": post.get('typeLabel', 'N/A'),
        "Status": post.get('postStatus', 'N/A'),
        "URL": post.get('url', 'N/A')
    }
    
    author_info = {
        "Name": post.get('author.name', 'N/A'),
        "Handle": post.get('author.handle', 'N/A'),
        "Role": post.get('author.role', 'N/A'),
        "Label": post.get('author.label', 'N/A'),
        "User Key": post.get('author.userKey', 'N/A')
    }
    
    dates = {
        "Posted": post.get('posted', 'N/A'),
        "Last Active": post.get('active', 'N/A')
    }
    
    stats = {
        "Replies": post.get('replyCount', '0'),
        "Likes": post.get('likeCount', '0'),
        "Views": post.get('viewCount', '0'),
        "Followers": post.get('followCount', '0')
    }
    
    keys = {
        "Post Key": post.get('postKey', 'N/A'),
        "Parent Key": post.get('parentKey', 'N/A')
    }
    
    # Print all information in organized sections
    print("\nBasic Information:")
    for key, value in basic_info.items():
        print(f"{key}: {value}")
    
    print("\nAuthor Information:")
    for key, value in author_info.items():
        print(f"{key}: {value}")
    
    print("\nDates:")
    for key, value in dates.items():
        print(f"{key}: {value}")
    
    print("\nStatistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\nKeys:")
    for key, value in keys.items():
        print(f"{key}: {value}")
    
    print("-" * 50)

if __name__ == "__main__":
    print("Starting category and post fetch...")
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
                    for post in posts:
                        print_post_details(post)
                else:
                    print("No posts found in this category")
            else:
                print("No category key available")
    else:
        print("\nNo categories were returned.")
