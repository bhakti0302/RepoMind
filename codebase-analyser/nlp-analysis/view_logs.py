#!/usr/bin/env python3

"""
View the logs in the logs directory.

This script lists and allows viewing of the logs in the logs directory.
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime

def list_logs(logs_dir=None):
    """List the logs in the logs directory.
    
    Args:
        logs_dir: Directory containing logs (default: ../logs)
    
    Returns:
        List of log files with their timestamps and sizes
    """
    # Define the logs directory
    if logs_dir is None:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level and then to the logs directory
        logs_dir = os.path.join(os.path.dirname(script_dir), "logs")
    
    # Check if the logs directory exists
    if not os.path.exists(logs_dir):
        print(f"Logs directory not found: {logs_dir}")
        return []
    
    # Get all log files
    log_files = []
    for filename in os.listdir(logs_dir):
        if filename.startswith("run_") and filename.endswith(".log"):
            file_path = os.path.join(logs_dir, filename)
            file_size = os.path.getsize(file_path)
            file_time = os.path.getmtime(file_path)
            file_datetime = datetime.fromtimestamp(file_time)
            
            log_files.append({
                "filename": filename,
                "path": file_path,
                "size": file_size,
                "time": file_time,
                "datetime": file_datetime
            })
    
    # Sort by time (newest first)
    log_files.sort(key=lambda x: x["time"], reverse=True)
    
    return log_files

def view_log(log_file):
    """View a log file.
    
    Args:
        log_file: Path to the log file
    """
    # Check if the log file exists
    if not os.path.exists(log_file):
        print(f"Log file not found: {log_file}")
        return
    
    # Use the 'less' command to view the log file
    try:
        subprocess.run(["less", log_file])
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        pass

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="View the logs in the logs directory.")
    parser.add_argument("--logs-dir", help="Directory containing logs")
    parser.add_argument("--view", type=int, help="View the Nth log file (0 for newest)")
    args = parser.parse_args()
    
    # List the logs
    log_files = list_logs(args.logs_dir)
    
    if not log_files:
        print("No log files found.")
        return
    
    # View a specific log file if requested
    if args.view is not None:
        if args.view < 0 or args.view >= len(log_files):
            print(f"Invalid log file index: {args.view}")
            print(f"Valid range: 0-{len(log_files) - 1}")
            return
        
        view_log(log_files[args.view]["path"])
        return
    
    # Print the list of log files
    print(f"Found {len(log_files)} log files:")
    for i, log_file in enumerate(log_files):
        size_kb = log_file["size"] / 1024
        print(f"{i}: {log_file['filename']} - {log_file['datetime']} - {size_kb:.1f} KB")
    
    # Ask which log file to view
    try:
        choice = input("\nEnter the number of the log file to view (or 'q' to quit): ")
        if choice.lower() == 'q':
            return
        
        choice = int(choice)
        if choice < 0 or choice >= len(log_files):
            print(f"Invalid choice: {choice}")
            return
        
        view_log(log_files[choice]["path"])
    
    except (ValueError, KeyboardInterrupt):
        # Handle invalid input or Ctrl+C gracefully
        pass

if __name__ == "__main__":
    main()
