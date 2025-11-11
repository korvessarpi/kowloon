#!/bin/bash

# Local Development Push Script
# Use this to push your local changes to GitHub

echo "=== Pushing Local Changes to GitHub ==="
echo "Time: $(date)"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "ERROR: Not in a git repository. Run this from your kowloon project directory."
    exit 1
fi

# Check for uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "You have uncommitted changes. Committing them now..."
    
    # Add all changes
    git add .
    
    # Ask for commit message
    echo "Enter a commit message (or press Enter for default):"
    read -r commit_message
    
    if [ -z "$commit_message" ]; then
        commit_message="Update game code - $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    git commit -m "$commit_message"
    echo "Changes committed with message: $commit_message"
else
    echo "No uncommitted changes found."
fi

# Push to GitHub
echo "Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "Next steps:"
    echo "1. SSH to your AWS server: ssh -i ~/.ssh/kowloonkey.pem ubuntu@18.221.126.196"
    echo "2. Navigate to game directory: cd /home/ubuntu/kowloon"
    echo "3. Run deployment: ./deploy.sh"
    echo ""
    echo "Or run this one-liner:"
    echo 'ssh -i ~/.ssh/kowloonkey.pem ubuntu@18.221.126.196 "cd /home/ubuntu/kowloon && ./deploy.sh"'
else
    echo "❌ Failed to push to GitHub. Check your connection and credentials."
    exit 1
fi