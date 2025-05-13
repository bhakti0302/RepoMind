#!/bin/bash

# Add PNG and JSON files to .gitignore
echo "# Ignore PNG and JSON files" >> .gitignore
echo "*.png" >> .gitignore
echo "*.json" >> .gitignore

# Add .gitignore to Git
git add .gitignore
git commit -m "Add PNG and JSON files to .gitignore"

echo "PNG and JSON files have been added to .gitignore."
echo "They will be ignored in future commits."