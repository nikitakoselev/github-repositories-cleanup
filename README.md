# GitHub Repositories Cleanup

A small interactive Python script to **safely and quickly delete repositories** from your GitHub account using a personal access token.

## 🚀 Features

- Lists all repositories in your account
- Shows repository details (stars, forks, description, README preview)
- Prompts for confirmation before deleting each repository
- Deletes repositories using the GitHub API and your supplied token

## ⚙️ Setup

1. Clone the repo
2. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

3. Create a file `tokens/delete-token.env`:

    ```env
    GITHUB_USERNAME=your-username
    GITHUB_TOKEN=ghp_your-token-here
    ```

4. Run the script:

    ```
    python cleanup.py
    ```

⚠️ **Warning:** This script **permanently deletes repositories** from your GitHub account. Use with caution.
