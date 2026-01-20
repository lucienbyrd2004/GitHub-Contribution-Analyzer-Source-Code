import requests # For getting info from github

# GitHub API needs a user agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# This can be any name, it needs to be sanitized later.
# The username "torvalds" (for Linus Torvalds) is a good first example
username = input("Input github username: ")

# The URL to get a user's github event info
user_event_str = f"https://api.github.com/users/{username}/events"

# Get the actual info from github
response = requests.get(user_event_str)
response.raise_for_status() # In case we get a bad request

events_data = response.json()