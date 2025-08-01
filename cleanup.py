import argparse
import csv
import logging
import os
import re
from export import export_repos_csv
from github_api import (
    delete_repo, archive_repo, make_private_repo,
    get_authenticated_username, get_repos, get_readme_snippet
)
from filters import add_to_preserve_list, is_preserved, load_preserve_list, save_preserve_list

LOG_DIR = 'logs'
LOG_FILE = f'{LOG_DIR}/cleanup.log'

def cleanup_repos(archive=True, delete=False, make_private=False):
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    GITHUB_USERNAME = get_authenticated_username()
    preserve_path = 'config/preserve-projects.txt'
    preserved = load_preserve_list(preserve_path)
    save_preserve_list(preserved, preserve_path)  # Ensure sorted at start

    repos = get_repos(GITHUB_USERNAME)
    repo_count = len(repos)
    github_path = f"https://github.com/{GITHUB_USERNAME}"
    logging.info(f"GitHub path: {github_path}")
    logging.info(f"Total repositories found: {repo_count}")
    logging.info(f"Preserved patterns: {len(preserved)}")
    print(f"🧹 Found {repo_count} repositories for {GITHUB_USERNAME} at {github_path}.")
    print(f"Preserved patterns: {len(preserved)}")

    confirm_all = input("⚠️ This will allow you to archive, make private, or delete repositories. Continue? [y/N]: ").strip().lower()
    if confirm_all != 'y':
        logging.info("Aborted by user before operation.")
        print("Aborted.")
        return

    archived = []
    privatized = []
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

        print(f"❓ What do you want to do with '{repo_url}'?")
        print("   [a] Archive   [p] Make Private   [d] Delete   [s] Skip   [q] Quit")
        choice = input("Your choice [s]: ").strip().lower()

        if choice == 'a':
            if archive_repo(GITHUB_USERNAME, name):
                archived.append(name)
        elif choice == 'p':
            if make_private_repo(GITHUB_USERNAME, name):
                privatized.append(name)
        elif choice == 'd':
            if delete_repo(GITHUB_USERNAME, name):
                deleted.append(name)
        elif choice == 'q':
            print("Aborted by user.")
            break
        else:
            skipped.append(name)
            add_to_preserve_list(name, preserve_path)

    # Summary
    summary = (
        f"\n--- Cleanup Summary ---\n"
        f"Archived repositories: {len(archived)}\n"
        f"Made private: {len(privatized)}\n"
        f"Deleted repositories: {len(deleted)}\n"
        f"Skipped by user: {len(skipped)}\n"
        f"Skipped (preserved): {len(preserved_skipped)}\n"
        f"Total checked: {repo_count}\n"
        f"Log file: {LOG_FILE}\n"
    )
    print(summary)
    logging.info(summary)

def batch_process_from_csv(csv_path, archive=False, delete=False, make_private=False):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    GITHUB_USERNAME = get_authenticated_username()
    preserved = load_preserve_list()
    to_process = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            repo_name = row.get('name')
            if repo_name:
                to_process.append(repo_name)

    action = "archive" if archive else "make private" if make_private else "delete"
    print(f"⚠️  About to {action} {len(to_process)} repositories for {GITHUB_USERNAME}.")
    confirm = input(f"Are you sure? This cannot be undone! [y/N]: ").strip().lower()
    if confirm != 'y':
        print("Aborted.")
        logging.info(f"Batch {action} aborted by user.")
        return

    archived = []
    privatized = []
    deleted = []
    failed = []
    preserved_skipped = []
    for name in to_process:
        if is_preserved(name, preserved):
            print(f"⏩ Skipped {name} (preserved by pattern or name)")
            preserved_skipped.append(name)
            continue
        repo_url = f"https://github.com/{GITHUB_USERNAME}/{name}"
        print(f"{action.capitalize()}ing {repo_url} ...")
        if archive:
            if archive_repo(GITHUB_USERNAME, name):
                archived.append(name)
            else:
                failed.append(name)
        elif make_private:
            if make_private_repo(GITHUB_USERNAME, name):
                privatized.append(name)
            else:
                failed.append(name)
        elif delete:
            if delete_repo(GITHUB_USERNAME, name):
                deleted.append(name)
            else:
                failed.append(name)

    summary = (
        f"\n--- Batch {action.capitalize()} Summary ---\n"
        f"Archived: {len(archived)}\n"
        f"Made private: {len(privatized)}\n"
        f"Deleted: {len(deleted)}\n"
        f"Skipped (preserved): {len(preserved_skipped)}\n"
        f"Failed: {len(failed)}\n"
        f"Log file: {LOG_FILE}\n"
    )
    print(summary)
    logging.info(summary)

def process_repos_by_path(paths_or_patterns, archive=True, delete=False, make_private=False):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    GITHUB_USERNAME = get_authenticated_username()
    preserved = load_preserve_list()
    all_repos = get_repos(GITHUB_USERNAME)
    matched = set()
    for pattern in paths_or_patterns:
        if pattern.startswith('https://github.com/'):
            repo_name = pattern.rstrip('/').split('/')[-1]
            matched.update([repo for repo in all_repos if repo['name'] == repo_name])
        else:
            regex = re.compile(pattern)
            matched.update([repo for repo in all_repos if regex.fullmatch(repo['name'])])

    if not matched:
        print("No repositories matched.")
        return

    action = "archive" if archive else "make private" if make_private else "delete"
    print(f"⚠️  About to {action} {len(matched)} repositories.")
    confirm = input(f"Are you sure you want to {action} these repositories? [y/N]: ").strip().lower()
    if confirm != 'y':
        print("Aborted.")
        logging.info(f"{action.capitalize()} aborted by user.")
        return

    preserved_skipped = []
    for repo in matched:
        if is_preserved(repo['name'], preserved):
            print(f"⏩ Skipped {repo['name']} (preserved by pattern or name)")
            preserved_skipped.append(repo['name'])
            continue
        repo_url = repo['html_url']
        print(f"{action.capitalize()}ing {repo_url} ...")
        if archive:
            archive_repo(repo['owner']['login'], repo['name'])
        elif make_private:
            make_private_repo(repo['owner']['login'], repo['name'])
        elif delete:
            delete_repo(repo['owner']['login'], repo['name'])

def main():
    parser = argparse.ArgumentParser(description="GitHub Repositories Cleanup Tool")
    parser.add_argument('--cleanup', action='store_true', help='Archive repositories interactively (default)')
    parser.add_argument('--delete', action='store_true', help='Delete repositories instead of archiving')
    parser.add_argument('--archive', action='store_true', help='Force archiving (default behavior)')
    parser.add_argument('--private', action='store_true', help='Make repositories private')
    parser.add_argument('--export', metavar='CSV_PATH', help='Export repository list to CSV')
    parser.add_argument('--batch-archive', metavar='CSV_PATH', help='Archive repositories listed in a CSV file')
    parser.add_argument('--batch-private', metavar='CSV_PATH', help='Make repositories private from a CSV file')
    parser.add_argument('--batch-delete', metavar='CSV_PATH', help='Delete repositories listed in a CSV file')
    parser.add_argument('--repos', nargs='+', metavar='REPO_PATH_OR_PATTERN', help='Archive/delete/private repos by full path or regex pattern')
    args = parser.parse_args()

    if args.cleanup:
        cleanup_repos(
            archive=(not args.delete and not args.private) or args.archive,
            delete=args.delete,
            make_private=args.private
        )
    if args.export:
        export_repos_csv(args.export)
    if args.batch_archive:
        batch_process_from_csv(args.batch_archive, archive=True)
    if args.batch_private:
        batch_process_from_csv(args.batch_private, make_private=True)
    if args.batch_delete:
        batch_process_from_csv(args.batch_delete, delete=True)
    if args.repos:
        process_repos_by_path(
            args.repos,
            archive=(not args.delete and not args.private) or args.archive,
            delete=args.delete,
            make_private=args.private
        )
    if not (args.cleanup or args.export or args.batch_archive or args.batch_private or args.batch_delete or args.repos):
        parser.print_help()

if __name__ == '__main__':
    main()
