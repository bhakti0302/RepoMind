# Install Git LFS
# For macOS
brew install git-lfs

# For Ubuntu/Debian
# sudo apt-get install git-lfs

# Initialize Git LFS
git lfs install

# Track large files (examples)
git lfs track "*.psd"
git lfs track "*.zip"
git lfs track "*.model"
git lfs track "*.h5"

# Add .gitattributes
git add .gitattributes

# Now add and commit your files again
git add .
git commit -m "Add large files with Git LFS"