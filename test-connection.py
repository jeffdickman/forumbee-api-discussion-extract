"""
Forumbee API Connection Test Script

This script tests the connection to the Forumbee API by making a simple GET request
to fetch posts. It validates the API token and domain before making the request.

Usage:
    python test-connection.py --token "your-api-token" --domain "example.com"
    OR
    python test-connection.py (uses values from config.py)
"""

import requests
import argparse
import re
from config import API_TOKEN, DOMAIN

def validate_domain(domain):
    """
    Validates and cleans the domain string to ensure proper format.
    
    Args:
        domain (str): The domain to validate (e.g., 'example.com' or 'https://example.com')
    
    Returns:
        str: Cleaned domain string without protocol or trailing slashes
        
    Raises:
        ValueError: If the domain format is invalid
    """
    # Remove any protocol (http:// or https://)
    domain = re.sub(r'^https?://', '', domain)
    # Remove any trailing slashes
    domain = domain.rstrip('/')
    # Domain validation - allows subdomains and common TLDs
    if not re.match(
        r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]'
        r'(?:\.[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9])*'
        r'\.[a-zA-Z]{2,}$',
        domain
    ):
        raise ValueError(
            "Invalid domain format. Please provide a valid domain "
            "(e.g., 'example.com' or 'subdomain.example.com')"
        )
    return domain

def test_connection(api_token, domain):
    """
    Tests the connection to the Forumbee API by making a GET request to fetch posts.
    
    Args:
        api_token (str): Your Forumbee API token
        domain (str): Your Forumbee domain (e.g., 'example.com')
    
    The function will:
    1. Validate and clean the domain
    2. Construct the API URL
    3. Make a GET request to fetch one post
    4. Print the response or any errors that occur
    """
    # Validate and clean the domain
    clean_domain = validate_domain(domain)
    # Construct the base URL for the API v2 endpoint
    base_url = f"https://{clean_domain}/api/2"
    
    # Set up the request headers with authentication
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # Construct the full URL for the posts endpoint
    test_url = f"{base_url}/posts"
    try:
        # Make the API request with a limit of 1 post
        response = requests.get(test_url, headers=headers, params={"limit": 1})
        response.raise_for_status()  # Raise an exception for bad status codes
        print("API connection successful.")
        print("Sample response:", response.json())
    except requests.exceptions.HTTPError as http_err:
        # Handle HTTP-specific errors (e.g., 401 Unauthorized, 404 Not Found)
        print(f"HTTP error occurred: {http_err.response.status_code} - {http_err.response.text}")
    except Exception as err:
        # Handle other potential errors (e.g., network issues)
        print(f"Other error occurred: {err}")

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Test Forumbee API connection')
    parser.add_argument('--token', help='Your Forumbee API token (optional if using config.py)')
    parser.add_argument('--domain', help='Your Forumbee domain (optional if using config.py)')
    args = parser.parse_args()
    
    # Use command-line arguments if provided, otherwise use config values
    token = args.token if args.token else API_TOKEN
    domain = args.domain if args.domain else DOMAIN
    
    # Run the connection test with the determined values
    test_connection(token, domain)