#!/usr/bin/env python3
"""
Fallback visualization script for the RepoMind extension.
This script is used when the main visualization scripts are missing.
It creates simple placeholder visualizations to ensure the UI flow works.
"""

import os
import sys
import json
import argparse
import datetime
from PIL import Image, ImageDraw, ImageFont
import shutil

def create_visualization(output_path, title, project_id, width=1200, height=800):
    """Create a simple visualization with text."""
    # Create a new image with white background
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to load a font, fall back to default if not available
    try:
        font_large = ImageFont.truetype("Arial", 40)
        font_medium = ImageFont.truetype("Arial", 30)
        font_small = ImageFont.truetype("Arial", 20)
    except IOError:
        # Use default font if Arial is not available
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw title
    draw.text((width//2, 100), title, fill='black', font=font_large, anchor='mm')
    
    # Draw project ID
    draw.text((width//2, 200), f"Project: {project_id}", fill='black', font=font_medium, anchor='mm')
    
    # Draw message
    draw.text((width//2, height//2), "This is a fallback visualization.", fill='black', font=font_medium, anchor='mm')
    draw.text((width//2, height//2 + 50), "The main visualization scripts could not be found.", fill='black', font=font_medium, anchor='mm')
    draw.text((width//2, height//2 + 100), "Please make sure the codebase is properly synced.", fill='black', font=font_medium, anchor='mm')
    
    # Draw timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((width//2, height - 100), f"Generated: {timestamp}", fill='black', font=font_small, anchor='mm')
    
    # Save the image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image.save(output_path)
    print(f"Created visualization: {output_path}")
    return output_path

def main():
    parser = argparse.ArgumentParser(description='Generate fallback visualizations')
    parser.add_argument('--project-id', required=True, help='Project ID')
    parser.add_argument('--output-dir', required=True, help='Output directory')
    parser.add_argument('--timestamp', help='Timestamp for the output files')
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate timestamp if not provided
    timestamp = args.timestamp or datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Create the visualizations
    multi_file_path = os.path.join(args.output_dir, f"{args.project_id}_multi_file_relationships.png")
    relationship_types_path = os.path.join(args.output_dir, f"{args.project_id}_relationship_types.png")
    
    # If timestamp is provided, also create timestamped versions
    if args.timestamp:
        multi_file_timestamped_path = os.path.join(args.output_dir, f"{args.project_id}_multi_file_relationships_{timestamp}.png")
        relationship_types_timestamped_path = os.path.join(args.output_dir, f"{args.project_id}_relationship_types_{timestamp}.png")
    else:
        multi_file_timestamped_path = None
        relationship_types_timestamped_path = None
    
    # Create the visualizations
    create_visualization(multi_file_path, "Multi-File Relationships", args.project_id)
    create_visualization(relationship_types_path, "Relationship Types", args.project_id)
    
    # Create timestamped versions if needed
    if multi_file_timestamped_path:
        shutil.copy(multi_file_path, multi_file_timestamped_path)
        print(f"Created timestamped copy: {multi_file_timestamped_path}")
    
    if relationship_types_timestamped_path:
        shutil.copy(relationship_types_path, relationship_types_timestamped_path)
        print(f"Created timestamped copy: {relationship_types_timestamped_path}")
    
    # Output JSON for the extension
    result = {
        "status": "success",
        "multi_file_relationships": multi_file_path,
        "relationship_types": relationship_types_path
    }
    
    print("JSON_OUTPUT_BEGINS")
    print(json.dumps(result, indent=2))
    print("JSON_OUTPUT_ENDS")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
