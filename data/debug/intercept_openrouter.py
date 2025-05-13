#!/usr/bin/env python3
"""
Script to directly intercept OpenRouter API calls.
"""

import os
import sys
import json
import logging
import requests
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Path to save the intercepted requests
OUTPUT_FILE = os.path.join("data", "debug", "openrouter_request.json")

# Original requests.post function
original_post = requests.post

@wraps(original_post)
def post_wrapper(url, *args, **kwargs):
    """Wrapper for requests.post to intercept OpenRouter API calls."""
    # Check if this is an OpenRouter API call
    if "openrouter.ai" in url or "api.openai.com" in url:
        logger.info(f"Intercepted API call to: {url}")
        
        # Save the request data
        request_data = {
            "url": url,
            "args": args,
            "kwargs": kwargs
        }
        
        # Extract the payload if available
        if "json" in kwargs:
            request_data["payload"] = kwargs["json"]
        elif "data" in kwargs:
            request_data["payload"] = kwargs["data"]
        
        # Create the debug directory if it doesn't exist
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        # Save to file
        logger.info(f"Saving request data to: {OUTPUT_FILE}")
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(request_data, f, indent=2)
        
        print(f"Intercepted OpenRouter API call saved to: {OUTPUT_FILE}")
    
    # Call the original function
    return original_post(url, *args, **kwargs)

# Replace the original function
requests.post = post_wrapper

print("OpenRouter API interceptor installed.")
print(f"Requests will be saved to: {OUTPUT_FILE}")
