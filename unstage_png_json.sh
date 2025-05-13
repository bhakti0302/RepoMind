#!/bin/bash

# Unstage all PNG and JSON files
git reset HEAD -- "*.png" "*.json"

echo "All PNG and JSON files have been unstaged."
echo "The files still exist in your working directory."