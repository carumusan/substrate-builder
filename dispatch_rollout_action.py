import os

import requests

GITHUB_USERNAME = os.environ["GHUB_USERNAME"]
GITHUB_ACCESS_TOKEN = os.environ["GHUB_ACCESS_TOKEN"]

def main():
    print("Triggering github action to rollout new container")
    headers = {
        "Accept": "application/vnd.github+json"
    }
    url = "https://api.github.com/repos/tsukistaking/polkadot-rollout/actions/workflows/polkadot_rollout.yml/dispatches"
    data = {
        "ref": "main"
    }
    response = requests.post(url, auth=(GITHUB_USERNAME, GITHUB_ACCESS_TOKEN), headers=headers, json=data)
    response.raise_for_status()
    
if __name__ == "__main__":
    main()