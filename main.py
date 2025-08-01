import argparse
from cleanup import (
    cleanup_repos, process_repos_by_path, batch_process_from_csv
)
from export import export_repos_csv

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