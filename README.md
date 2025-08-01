# GitHub Repositories Cleanup

A modular Python tool to **archive, make private, or delete repositories** from your GitHub account using the GitHub API.

---

## Features

- **Archive repositories** (recommended, safest)
- **Make repositories private** (recommended for sensitive code)
- **Delete repositories** (dangerous, irreversible—use with extreme caution)
- **Preserve list:** Exclude repositories by name or regex pattern
- **Export repository list to CSV**
- **Comprehensive logging** (to both console and `logs/cleanup.log`)
- **No secrets stored on disk:** Uses `GITHUB_TOKEN` environment variable

---

## Setup

1. **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/github-repositories-cleanup.git
    cd github-repositories-cleanup
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Set your GitHub token as an environment variable:**
    - On Windows (Command Prompt):
      ```sh
      set GITHUB_TOKEN=ghp_your_token_here
      ```
    - On Linux/macOS:
      ```sh
      export GITHUB_TOKEN=ghp_your_token_here
      ```
    - **Token must have `repo`, `delete_repo`, and `admin:repo_hook` permissions.**

4. **(Optional) Edit the preserve list:**
    - Add repository names or regex patterns (one per line) to `config/preserve-projects.txt` to prevent changes.

---

## Usage

### ⚠️ Safety First: Archive or Make Private Before Deleting

**Archiving** a repository makes it read-only and hides it from active development, but you can always unarchive it later.  
**Making a repository private** hides it from the public, but you retain full control.  
**Deleting** a repository is **irreversible**—all code, issues, and PRs are lost forever.

---

### 1. **Interactive Cleanup (Archive or Make Private Repositories)**

```sh
python main.py --cleanup
```
- Lists your repositories.
- For each repo, shows details and asks if you want to **archive**, **make private**, or **skip**.
- Skipped repos can be added to the preserve list.
- Type `q` at any prompt to abort.

**To force archiving only:**
```sh
python main.py --archive --cleanup
```

**To make repositories private:**
```sh
python main.py --private --cleanup
```

---

### 2. **Export Repository List to CSV**

```sh
python main.py --export repos.csv
```
- Exports your repository metadata to a CSV file.

---

### 3. **Batch Archive, Make Private, or Delete from CSV**

**Recommended workflow:**
1. Export all deletable repos:
    ```sh
    python main.py --export repos.csv
    ```
2. Edit `repos.csv` to keep only the rows you want to process.
3. Run batch operation:

    **Archive:**
    ```sh
    python main.py --batch-archive repos.csv
    ```

    **Make Private:**
    ```sh
    python main.py --batch-private repos.csv
    ```

    **Delete (dangerous!):**
    ```sh
    python main.py --batch-delete repos.csv
    ```

- You will be asked for confirmation before any batch operation starts.

---

### 4. **Archive, Make Private, or Delete by Full Path or Pattern**

```sh
python main.py --repos https://github.com/your-username/repo1 ^test-.*
```
- Archives (default) all matching repositories.
- You can specify full GitHub URLs and/or regex patterns.

**To make private:**
```sh
python main.py --private --repos https://github.com/your-username/repo1 ^test-.*
```

**To delete instead of archive (dangerous!):**
```sh
python main.py --delete --repos https://github.com/your-username/repo1 ^test-.*
```

---

## Why Archive or Make Private Instead of Delete?

- **Archiving** preserves your code and history, but prevents changes.
- **Making private** hides your repo from the public, but you keep full access.
- **Deleting** is permanent and cannot be undone.  
  **Always archive or make private unless you are absolutely sure you want to delete.**

---

## Configuration

- **Preserve List:**  
  `config/preserve-projects.txt`  
  Add repo names or regex patterns (one per line) to exclude from any operation.

- **Logging:**  
  All actions are logged to `logs/cleanup.log` with timestamps.

---

## Security

- **Never store your token in a file.**
- **Token is read from the `GITHUB_TOKEN` environment variable only.**
- **No sensitive information is logged.**

---

## Requirements

- Python 3.7+
- `requests`

---

## Example

```
🧹 Found 42 repositories for your-username at https://github.com/your-username.
Preserved patterns: 3

📦 https://github.com/your-username/my-repo (Public)
   ⭐ Stars: 5 | 🍴 Forks: 2
   📝 Description: My awesome project
   📄 README preview:
   -------------------
   # My Repo
   ...
   -------------------
❓ What do you want to do with 'https://github.com/your-username/my-repo'?
   [a] Archive   [p] Make Private   [d] Delete   [s] Skip   [q] Quit
```

---

## License

MIT
