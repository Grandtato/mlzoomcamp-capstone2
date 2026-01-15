import os
import requests
import time
import pandas as pd

# Configuration
INPUT_FILE = "repos_list.txt"
OUTPUT_FILE = "data/runs.csv"
MAX_PAGES = 3  # 3 pages * 100 runs = 300 runs per repo (Total ~43,000 rows)
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    print("ERROR: GITHUB_TOKEN is not set.")
    exit(1)

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"}


def fetch_repo_runs(repo_name):
    runs_data = []
    url = f"https://api.github.com/repos/{repo_name}/actions/runs"

    for page in range(1, MAX_PAGES + 1):
        params = {"per_page": 100, "page": page, "status": "completed"}
        try:
            r = requests.get(url, headers=HEADERS, params=params)

            # Handle Rate Limits
            if r.status_code == 403:
                print("  [!] Rate limit hit. Sleeping 60s...")
                time.sleep(60)
                continue

            if r.status_code != 200:
                break

            batch = r.json().get("workflow_runs", [])
            if not batch:
                break

            for run in batch:
                runs_data.append(
                    {
                        "repo": repo_name,
                        "id": run["id"],
                        "conclusion": run["conclusion"],  # Target: success/failure
                        "created_at": run["created_at"],
                        "updated_at": run["updated_at"],
                        "head_branch": run["head_branch"],
                        "author": (
                            run["triggering_actor"]["login"]
                            if run.get("triggering_actor")
                            else "unknown"
                        ),
                        "run_attempt": run["run_attempt"],
                    }
                )
        except Exception as e:
            print(f"  Error fetching {repo_name}: {e}")
            break

        time.sleep(0.2)  # Be polite

    return runs_data


def main():
    if not os.path.exists("data"):
        os.makedirs("data")

    with open(INPUT_FILE, "r") as f:
        repos = [line.strip() for line in f if line.strip()]

    all_runs = []
    print(f"Starting extraction for {len(repos)} repositories...")

    for i, repo in enumerate(repos):
        print(f"[{i+1}/{len(repos)}] Extracting: {repo}")
        repo_runs = fetch_repo_runs(repo)
        all_runs.extend(repo_runs)
        print(f"   -> Found {len(repo_runs)} runs")

    # Save
    df = pd.DataFrame(all_runs)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSUCCESS! Saved {len(df)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
