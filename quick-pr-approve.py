#!/usr/bin/env python3
import json
import os
import pyperclip
import requests

print("You should already have the URLs for PRs copied from Slack in your clipboard 🙏")

try:
    clipboard_contents = pyperclip.paste()
    if not clipboard_contents:
        raise ValueError("Clipboard is empty. Please copy the URLs from Slack.")
except Exception as e:
    print(f"Error reading clipboard contents: {e}")
    exit(1)

github_token = os.getenv("GITHUB_TOKEN")
if not github_token:
    print("Error: GITHUB_TOKEN environment variable is not set.")
    exit(1)

headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f'Bearer {github_token}',
    "Content-Type": "application/json",
}
payload = json.dumps({"event": "APPROVE"})

for url in clipboard_contents.split():
    if url.startswith("https://"):
        api_url = url.replace("github.com", "api.github.com")
        api_url = api_url.replace("ncino/", "repos/ncino/")
        api_url = api_url.replace("pull", "pulls")
        api_url += "/reviews"

        try:
            response = requests.request("POST", api_url, headers=headers, data=payload)
            response.raise_for_status()
            print(f"Successfully approved PR: {url}")
        except requests.exceptions.RequestException as e:
            print(f"Error approving PR {url}: {e}")