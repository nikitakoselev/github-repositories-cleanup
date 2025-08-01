import csv
from github_api import get_repos, get_authenticated_username

def export_repos_csv(filepath='repos.csv'):
    username = get_authenticated_username()
    repos = get_repos(username)
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'full_name', 'private', 'fork', 'stargazers_count', 'forks_count', 'description', 'html_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for repo in repos:
            writer.writerow({k: repo.get(k, '') for k in fieldnames})
    print(f"Exported {len(repos)} repositories to {filepath}")