#!/bin/bash

# This script splits your branch into smaller chunks and pushes them separately

# Get the current branch name
current_branch=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $current_branch"

# Get all commits in the current branch
commit_count=$(git rev-list --count HEAD)
echo "Number of commits in branch: $commit_count"

if [ $commit_count -eq 0 ]; then
    echo "No commits to push."
    exit 0
fi

# Calculate how many chunks to create (aim for 3-5 commits per chunk)
commits_per_chunk=3
chunk_count=$(( (commit_count + commits_per_chunk - 1) / commits_per_chunk ))
echo "Will split into $chunk_count chunks of approximately $commits_per_chunk commits each"

# Create a temporary branch to work from
git checkout -b temp-branch-for-splitting

# Process each chunk
for (( i=1; i<=$chunk_count; i++ )); do
    # Calculate how many commits to include in this chunk
    if [ $i -eq $chunk_count ]; then
        # Last chunk might have fewer commits
        chunk_commits=$(( commit_count - (i-1)*commits_per_chunk ))
    else
        chunk_commits=$commits_per_chunk
    fi
    
    echo "Creating chunk $i with $chunk_commits commits"
    
    # Create a new branch for this chunk
    chunk_branch="${current_branch}-chunk-${i}"
    git checkout -b $chunk_branch
    
    # Reset to the appropriate commit
    reset_point="HEAD~$(( commit_count - (i-1)*commits_per_chunk ))"
    git reset --soft $reset_point
    
    # Commit and push
    git commit -m "Chunk $i of $chunk_count for $current_branch"
    
    echo "Pushing chunk $i to $chunk_branch..."
    git push origin $chunk_branch
    
    # Go back to the temporary branch
    git checkout temp-branch-for-splitting
done

# Go back to the original branch
git checkout $current_branch

# Clean up the temporary branch
git branch -D temp-branch-for-splitting

echo "All chunks have been pushed to separate branches."
echo "You can now create pull requests for each chunk branch."