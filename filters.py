import re

def load_preserve_list(preserve_path='config/preserve-projects.txt'):
    try:
        with open(preserve_path, 'r') as f:
            preserved = sorted(set(line.strip() for line in f if line.strip()))
    except FileNotFoundError:
        preserved = []
    return preserved

def is_preserved(repo_name, preserved):
    for pattern in preserved:
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