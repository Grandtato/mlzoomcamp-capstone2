import os
import requests
import time

# Configuration: We scan these owners for public CI data
OWNERS = ["DataTalksClub", "tiangolo", "huggingface", "psf"]
OUTPUT_FILE = "repos_list.txt"

# Get token from environment
TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    print("ERROR: GITHUB_TOKEN is not set in your terminal.")
    print("Run: export GITHUB_TOKEN='your_token_here'")
    exit(1)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
    "Accept": "application/vnd.github+json",
}


def get_active_repos(owner):
    """Finds repos that have >10 Action runs in history."""
    repos = []
    page = 1
    print(f"Scanning {owner}...")

    while True:
        # List repos (100 per page)
        url = f"https://api.github.com/users/{owner}/repos?per_page=100&page={page}"
        r = requests.get(url, headers=HEADERS)

        if r.status_code != 200:
            break

        data = r.json()
        if not data:
            break  # End of list

        for repo in data:
            full_name = repo["full_name"]

            # Check if it has Action runs
            run_url = (
                f"https://api.github.com/repos/{full_name}/actions/runs?per_page=1"
            )
            run_r = requests.get(run_url, headers=HEADERS)

            if run_r.status_code == 200:
                count = run_r.json().get("total_count", 0)
                # We want repos with actual history (>10 runs)
                if count > 10:
                    print(f"  [+] Found active: {full_name} ({count} runs)")
                    repos.append(full_name)

            time.sleep(0.1)  # Respect API limits

        page += 1
    return repos


def main():
    all_repos = []
    print("Starting discovery...")

    for owner in OWNERS:
        try:
            found = get_active_repos(owner)
            all_repos.extend(found)
        except Exception as e:
            print(f"Error scanning {owner}: {e}")

    # Save to file
    with open(OUTPUT_FILE, "w") as f:
        for r in all_repos:
            f.write(r + "\n")

    print(f"\nSaved {len(all_repos)} repos to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
