import os
import requests
from datetime import datetime
import json

def post_update(content):
    # GitHub repository details
    owner = "NoCoMozi"
    repo = "MayDayMovement"
    
    # Your personal access token (different from bot token)
    github_token = input("Enter your GitHub personal access token: ")
    
    # Prepare the dispatch event data
    event_type = "telegram-update"
    client_payload = {
        "content": content,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    # GitHub API endpoint for repository dispatch
    url = f"https://api.github.com/repos/{owner}/{repo}/dispatches"
    
    # Headers for authentication
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {github_token}",
        "Content-Type": "application/json"
    }
    
    # Make the request
    response = requests.post(url, headers=headers, data=json.dumps({
        "event_type": event_type,
        "client_payload": client_payload
    }))
    
    if response.status_code == 204:
        print("Update posted successfully!")
    else:
        print(f"Error posting update: {response.status_code}")
        print(response.text)

def main():
    print("May Day Movement Update Poster")
    print("-----------------------------")
    print("Type your update message (press Enter twice to submit):")
    
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    
    content = "\n".join(lines)
    
    if content.strip():
        post_update(content)
    else:
        print("No content provided. Update cancelled.")

if __name__ == "__main__":
    main()
