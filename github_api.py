import os
import requests
import base64

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    print("❌ GITHUB_TOKEN environment variable not set.")
    exit(1)

API_URL = 'https://api.github.com'
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

def get_authenticated_username():
    url = f"{API_URL}/user"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("login")
    else:
        print("❌ Failed to fetch authenticated username.")
        exit(1)

def get_repos(username):
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
        # Only include repos owned by the authenticated user
        repos.extend([repo for repo in data if repo['owner']['login'] == username])
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
        print(f"✅ Deleted {repo_url}")
        return True
    else:
        print(f"❌ Error deleting {repo_url}: {response.status_code} {response.text}")
        return False

def archive_repo(owner, repo):
    url = f'{API_URL}/repos/{owner}/{repo}'
    response = requests.patch(url, headers=HEADERS, json={'archived': True})
    repo_url = f'https://github.com/{owner}/{repo}'
    if response.status_code == 200:
        print(f"📦 Archived {repo_url}")
        return True
    else:
        print(f"❌ Error archiving {repo_url}: {response.status_code} {response.text}")
        return False

def make_private_repo(owner, repo):
    url = f'{API_URL}/repos/{owner}/{repo}'
    response = requests.patch(url, headers=HEADERS, json={'private': True})
    repo_url = f'https://github.com/{owner}/{repo}'
    if response.status_code == 200:
        print(f"🔒 Made private {repo_url}")
        return True
    else:
        print(f"❌ Error making {repo_url} private: {response.status_code} {response.text}")
        return False