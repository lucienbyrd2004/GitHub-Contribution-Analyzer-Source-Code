import requests
import os
import re
from datetime import datetime
from dataclasses import dataclass
from textblob import TextBlob
import pandas as pd
from dotenv import load_dotenv

# Load environment variables (for GitHub Token)
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Setup headers for authenticated API requests
HEADERS = {"Accept": "application/vnd.github.v3+json"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

@dataclass
class GitHubCommit:
    repo: str
    sha: str
    timestamp: datetime
    message: str
    polarity: float | None
    subjectivity: float | None
    additions: int = 0
    deletions: int = 0

    def set_sentiment_analysis(self) -> None:
        blob = TextBlob(self.message)
        sentiment = blob.sentiment
        self.polarity = sentiment.polarity # Range: [-1.0, 1.0]
        self.subjectivity = sentiment.subjectivity # Range: [0.0, 1.0]

    def to_dict(self) -> dict:
        return {
            'repo':         self.repo,
            'sha':          self.sha,
            'timestamp':    self.timestamp,
            'message':      self.message,
            'polarity':     self.polarity,
            'subjectivity': self.subjectivity,
            'additions':    self.additions,
            'deletions':    self.deletions
        }

# --- URL PARSING UTILITIES ---
def parse_github_url(url: str):
    """
    Takes a GitHub URL and determines if it's a profile or a repository.
    Returns a tuple: ('type', 'username', 'repo_name')
    """
    # Remove trailing slashes
    url = url.strip("/")
    
    # Extract the path part of the URL (e.g., 'Jabril/my-repo' or 'Jabril')
    match = re.search(r"github\.com/([^/]+)/?([^/]+)?", url)
    if not match:
        raise ValueError("Invalid GitHub URL provided.")
    
    owner = match.group(1)
    repo = match.group(2)
    
    if repo:
        return "repo", owner, repo
    else:
        return "user", owner, None

# --- API FETCHING FUNCTIONS ---
def get_user_activity(username: str, pages: int = 2) -> list[GitHubCommit]:
    """
    Fetches recent PushEvents for a user. Best for Histograms, Word Clouds, and Sentiment.
    """
    results = []
    
    for page in range(1, pages + 1):
        url = f"https://api.github.com/users/{username}/events/public?per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code != 200:
            print(f"Failed to fetch data for {username}: {response.text}")
            break
            
        events = response.json()
        if not events:
            break
            
        for event in events:
            if event['type'] == 'PushEvent':
                repo_name = event['repo']['name']
                # The event timestamp is when the push happened
                timestamp_str = event['created_at']
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
                
                for commit in event['payload'].get('commits', []):
                    # We grab the first line of the commit message
                    msg = commit['message'].splitlines()[0]
                    sha = commit['sha']
                    
                    new_commit = GitHubCommit(
                        repo=repo_name,
                        sha=sha,
                        timestamp=timestamp,
                        message=msg,
                        polarity=None,
                        subjectivity=None
                    )
                    new_commit.set_sentiment_analysis()
                    results.append(new_commit)
                    
    return results

def get_repo_contributor_stats(owner: str, repo: str) -> pd.DataFrame:
    """
    Fetches aggregate lines added/deleted per user for a specific repository.
    Perfect for the "Top Users Bar Chart".
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/stats/contributors"
    response = requests.get(url, headers=HEADERS)
    
    # GitHub often returns 202 Accepted while it compiles these stats in the background.
    if response.status_code == 202:
        raise Exception("GitHub is compiling these statistics. Please try again in a few seconds.")
    elif response.status_code != 200:
        raise Exception(f"Failed to fetch repo stats: {response.status_code}")
        
    stats = response.json()
    data = []
    
    for contributor in stats:
        author = contributor['author']['login']
        total_commits = contributor['total']
        
        # Tally up all additions and deletions across all weeks
        total_additions = sum(week['a'] for week in contributor['weeks'])
        total_deletions = sum(week['d'] for week in contributor['weeks'])
        
        data.append({
            "Author": author,
            "Total Commits": total_commits,
            "Additions": total_additions,
            "Deletions": total_deletions
        })
        
    return pd.DataFrame(data)

def get_user_commit_from_name(username: str) -> list[GitHubCommit]:
    """Compatibility wrapper for your original function calls."""
    return get_user_activity(username, pages=1)