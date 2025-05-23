#!/usr/bin/env python3

"""
Run a command and log its output to a timestamped file in the logs directory.

This script runs a command and logs its output to a timestamped file in the logs directory.
It also displays the output in the terminal.
"""

import os
import sys
import subprocess
import datetime
import platform
import argparse

def run_with_logs(command, logs_dir=None):
    """Run a command and log its output to a timestamped file in the logs directory.
    
    Args:
        command: Command to run (list of strings)
        logs_dir: Directory to store logs (default: ../logs)
    
    Returns:
        Exit code of the command
    """
    # Define the logs directory
    if logs_dir is None:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level and then to the logs directory
        logs_dir = os.path.join(os.path.dirname(script_dir), "logs")
    
    # Create the logs directory if it doesn't exist
    os.makedirs(logs_dir, exist_ok=True)
    
    # Generate a timestamp for the log file
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(logs_dir, f"run_{timestamp}.log")
    
    # Print information about the run
    print(f"Running command: {' '.join(command)}")
    print(f"Logging output to: {log_file}")
    
    # Open the log file
    with open(log_file, "w") as f:
        # Write header information
        f.write(f"=== Command: {' '.join(command)} ===\n")
        f.write(f"=== Started at: {datetime.datetime.now()} ===\n")
        f.write(f"=== Working directory: {os.getcwd()} ===\n")
        f.write(f"=== System: {platform.system()} {platform.release()} ===\n")
        f.write(f"=== Python: {sys.version} ===\n")
        f.write("=== Environment: ===\n")
        for key, value in sorted(os.environ.items()):
            f.write(f"{key}={value}\n")
        f.write("=== Command output: ===\n\n")
        
        # Run the command and capture its output
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffered
        )
        
        # Read and write the output line by line
        for line in process.stdout:
            sys.stdout.write(line)  # Write to terminal
            f.write(line)  # Write to log file
            f.flush()  # Ensure the line is written immediately
        
        # Wait for the process to complete and get the exit code
        exit_code = process.wait()
        
        # Write footer information
        f.write(f"\n=== Command completed at: {datetime.datetime.now()} ===\n")
        f.write(f"=== Exit status: {exit_code} ===\n")
    
    return exit_code

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run a command and log its output.")
    parser.add_argument("command", nargs="+", help="Command to run")
    parser.add_argument("--logs-dir", help="Directory to store logs")
    args = parser.parse_args()
    
    # Run the command with logging
    exit_code = run_with_logs(args.command, args.logs_dir)
    
    # Exit with the same code as the command
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
