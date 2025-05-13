# Create a new branch from your current state
git checkout -b tanya1.0-part1

# Reset to a previous commit (keep about half your changes)
git reset --soft HEAD~10  # Adjust the number as needed

# Commit this subset
git commit -m "First part of tanya1.0 changes"

# Push this smaller chunk
git push -u origin tanya1.0-part1

# Now go back to your original branch
git checkout tanya1.0

# Create another branch for the remaining changes
git checkout -b tanya1.0-part2

# Push this branch
git push -u origin tanya1.0-part2