import logging
from datetime import datetime
import os
import requests
import base64
import re
from dotenv import load_dotenv

# Load token and username from config/delete-token.env
load_dotenv(dotenv_path='config/delete-token.env')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

if not GITHUB_TOKEN:
    print("❌ Missing credentials. Make sure config/delete-token.env is set.")
    exit(1)

API_URL = 'https://api.github.com'
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'cleanup.log')
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def get_authenticated_username():
    url = f"{API_URL}/user"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("login")
    else:
        print("❌ Failed to fetch authenticated username.")
        exit(1)

GITHUB_USERNAME = get_authenticated_username()

def get_repos():
    repos = []
    page = 1
    while True:
        url = f'{API_URL}/user/repos?per_page=100&page={page}'
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Failed to fetch repositories: {response.status_code}")
            break
        data = response.json()
        if not data:
            break
        # Only include repos owned by the authenticated user and not forks
        repos.extend([repo for repo in data if repo['owner']['login'] == GITHUB_USERNAME])
        page += 1
    return repos

def get_readme_snippet(owner, repo):
    url = f'{API_URL}/repos/{owner}/{repo}/readme'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        content = response.json().get('content', '')
        decoded = base64.b64decode(content).decode('utf-8', errors='ignore')
        return '\n'.join(decoded.strip().split('\n')[:10])
    return '(No README or unable to fetch)'

def delete_repo(owner, repo):
    url = f'{API_URL}/repos/{owner}/{repo}'
    repo_url = f'https://github.com/{owner}/{repo}'
    response = requests.delete(url, headers=HEADERS)
    if response.status_code == 204:
        logging.info(f"Deleted: {repo_url}")
        print(f"✅ Deleted {repo_url}")
        return True
    else:
        logging.error(f"Failed to delete: {repo_url} ({response.status_code}) {response.text}")
        print(f"❌ Error deleting {repo_url}: {response.status_code} {response.text}")
        return False

def load_preserve_list(preserve_path='config/preserve-projects.txt'):
    try:
        with open(preserve_path, 'r') as f:
            preserved = sorted(set(line.strip() for line in f if line.strip()))
    except FileNotFoundError:
        preserved = []
    return preserved

def is_preserved(repo_name, preserved):
    for pattern in preserved:
        # Exact match or regex match
        if pattern == repo_name or re.fullmatch(pattern, repo_name):
            return True
    return False

def save_preserve_list(preserved, preserve_path='config/preserve-projects.txt'):
    preserved_sorted = sorted(set(preserved))
    with open(preserve_path, 'w') as f:
        for repo in preserved_sorted:
            f.write(repo + '\n')

def add_to_preserve_list(repo_name, preserve_path='config/preserve-projects.txt'):
    preserved = load_preserve_list(preserve_path)
    if not is_preserved(repo_name, preserved):
        preserved.append(repo_name)
        save_preserve_list(preserved, preserve_path)

def main():
    preserve_path = 'config/preserve-projects.txt'
    preserved = load_preserve_list(preserve_path)
    save_preserve_list(preserved, preserve_path)  # Ensure sorted at start

    repos = get_repos()
    repo_count = len(repos)
    github_path = f"https://github.com/{GITHUB_USERNAME}"
    logging.info(f"GitHub path: {github_path}")
    logging.info(f"Total repositories found: {repo_count}")
    logging.info(f"Preserved patterns: {len(preserved)}")
    print(f"🧹 Found {repo_count} repositories for {GITHUB_USERNAME} at {github_path}.")
    print(f"Preserved patterns: {len(preserved)}")

    confirm_all = input("⚠️ This will allow you to delete repositories. Continue? [y/N]: ").strip().lower()
    if confirm_all != 'y':
        logging.info("Aborted by user before deletion.")
        print("Aborted.")
        return

    deleted = []
    skipped = []
    preserved_skipped = []

    for repo in repos:
        name = repo['name']
        repo_url = f"https://github.com/{GITHUB_USERNAME}/{name}"
        if is_preserved(name, preserved):
            logging.info(f"Skipped (preserved): {repo_url}")
            preserved_skipped.append(name)
            print(f"⏩ Skipped {repo_url} (preserved by pattern or name)")
            continue
        desc = repo.get('description', '')
        stars = repo['stargazers_count']
        forks = repo['forks_count']
        private = repo['private']
        print(f"\n📦 {repo_url} ({'Private' if private else 'Public'})")
        print(f"   ⭐ Stars: {stars} | 🍴 Forks: {forks}")
        print(f"   📝 Description: {desc or '(No description)'}")
        print("   📄 README preview:")
        print("   -------------------")
        print(get_readme_snippet(GITHUB_USERNAME, name))
        print("   -------------------")

        confirm = input(f"❓ Delete '{repo_url}'? [y/N/q]: ").strip().lower()
        if confirm == 'y':
            if delete_repo(GITHUB_USERNAME, name):
                deleted.append(name)
            else:
                skipped.append(name)
        elif confirm == 'q':
            logging.info("Aborted by user during deletion.")
            print("Aborted by user.")
            break
        else:
            logging.info(f"Skipped (user): {repo_url}")
            skipped.append(name)
            add_to_preserve_list(name, preserve_path)

    # Summary
    summary = (
        f"\n--- Cleanup Summary ---\n"
        f"Deleted repositories: {len(deleted)}\n"
        f"Skipped by user: {len(skipped)}\n"
        f"Skipped (preserved): {len(preserved_skipped)}\n"
        f"Total checked: {repo_count}\n"
        f"Log file: {LOG_FILE}\n"
    )
    print(summary)
    logging.info(summary)

if __name__ == '__main__':
    main()
