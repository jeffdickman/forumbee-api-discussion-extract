"""
Forumbee API Post Text Extraction Script

This script fetches post content from the Forumbee API and saves it to a single CSV file.
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
            "fields": "postKey,parentKey,title,textPlain,category.name,posted,author.name,url",
            "output": "csv",  # Request CSV format
            "limit": limit,
            "offset": offset,
            "sort": "posted"  # Sort by most recent first
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

def save_all_posts_to_csv(all_posts, output_dir):
    """
    Save all posts to a single CSV file with timestamp.
    Posts are grouped by parentKey to keep related posts together.
    
    Args:
        all_posts (list): List of all post dictionaries
        output_dir (str): Directory to save the CSV file
    """
    if not all_posts:
        return
    
    # Create timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create filename
    filename = f"{timestamp}_all_posts.csv"
    filepath = os.path.join(output_dir, filename)
    
    # Define the field order
    fieldnames = ['parentKey', 'category.name', 'author.name', 'title', 'textPlain', 'posted', 'postKey', 'url']
    
    # Process posts to ensure full URLs and group related posts
    processed_posts = []
    
    # Create a dictionary to store posts by their postKey for easy lookup
    posts_by_key = {post['postKey']: post for post in all_posts}
    
    # First, identify all parent posts (posts without a parentKey)
    parent_posts = [post for post in all_posts if not post.get('parentKey')]
    
    # Sort parent posts by posted date (newest first)
    parent_posts.sort(key=lambda x: x.get('posted', ''), reverse=True)
    
    # For each parent post, add it and all its replies
    for parent in parent_posts:
        # Add the parent post
        parent_copy = parent.copy()
        if parent_copy.get('url') and not parent_copy['url'].startswith('http'):
            parent_copy['url'] = f"https://{DOMAIN}{parent_copy['url']}"
        processed_posts.append(parent_copy)
        
        # Find all direct replies to this parent
        replies = [post for post in all_posts if post.get('parentKey') == parent.get('postKey')]
        
        # Sort replies by posted date (oldest first)
        replies.sort(key=lambda x: x.get('posted', ''))
        
        # Add each reply
        for reply in replies:
            reply_copy = reply.copy()
            if reply_copy.get('url') and not reply_copy['url'].startswith('http'):
                reply_copy['url'] = f"https://{DOMAIN}{reply_copy['url']}"
            processed_posts.append(reply_copy)
    
    # Write to CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        if processed_posts:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_posts)
            print(f"\nSaved {len(processed_posts)} total posts to {filename}")
            print(f"Number of parent posts: {len(parent_posts)}")
            print(f"Number of reply posts: {len(processed_posts) - len(parent_posts)}")

if __name__ == "__main__":
    print("Starting category and post fetch...")
    
    # Ensure output directory exists
    output_dir = ensure_output_directory()
    
    categories = get_all_categories()
    all_posts = []
    
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
                    all_posts.extend(posts)
                else:
                    print("No posts found in this category")
            else:
                print("No category key available")
        
        # Save all posts to a single CSV file
        save_all_posts_to_csv(all_posts, output_dir)
    else:
        print("\nNo categories were returned.")
