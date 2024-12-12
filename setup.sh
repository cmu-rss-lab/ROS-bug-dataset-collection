#!/bin/bash

# Define the .env file path
ENV_FILE=".env"

# Check if the .env file already exists
if [ ! -f "$ENV_FILE" ]; then
    echo "No .env file found. Creating a new one..."
else
    echo "The .env file already exists. Do you want to overwrite it? (yes/no)"
    read -r overwrite
    if [ "$overwrite" != "yes" ]; then
        echo "Setup aborted. Using the existing .env file."
        exit 0
    fi
fi

# Prompt the user for GitHub token
echo "Enter your GitHub Personal Access Token (GITHUB_TOKEN):"
read -r GITHUB_TOKEN

# Optionally validate the token (requires `curl` installed)
echo "Validating your GitHub token..."
response=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user)
if [ "$response" != "200" ]; then
    echo "Invalid GitHub token. Please ensure it's correct and has the necessary permissions."
    exit 1
fi

# Write the token to the .env file
echo "GITHUB_TOKEN=$GITHUB_TOKEN" > "$ENV_FILE"

echo "The GITHUB_TOKEN has been saved to $ENV_FILE."

# Secure the .env file
chmod 600 "$ENV_FILE"
echo "Permissions of $ENV_FILE have been restricted for security."

# Done
echo "Setup complete. You can now use the application."
