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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for page in range(1, pages + 1):
        url = f"https://api.github.com/users/{username}/events/public?per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        
        # --- NEW ERROR HANDLING ---
        if response.status_code != 200:
            error_msg = response.json().get('message', 'Unknown Error')
            # Instead of printing to terminal, we force the app to stop and show the error!
            raise Exception(f"GitHub API Error ({response.status_code}): {error_msg}")
        # --------------------------
            
        events = response.json()
        if not events:
            break
            
        for event in events:
            if event['type'] == 'PushEvent':
                created_at = datetime.strptime(event['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                repo_name = event['repo']['name']

                # Use 'head' as the commit SHA
                commit_sha = event['payload'].get('head')

                if commit_sha:
                    # Construct the URL using the repo name provided in the event
                    commit_url = f"https://api.github.com/repos/{repo_name}/commits/{commit_sha}"
                    commit_res = requests.get(commit_url, headers=headers)
                    if commit_res.status_code == 200:
                        commit_data = commit_res.json()

                        # commit.polarity = sentiment.polarity # Range: [-1.0, 1.0]
                        # commit.subjectivity = sentiment.subjectivity # Range: [0.0, 1.0]

                    results.append(GitHubCommit(
                        repo=repo_name,
                        sha=commit_sha,
                        timestamp=created_at,
                        message=commit_data['commit']['message'].splitlines()[0],
                        polarity=None,
                        subjectivity=None
                                            ))

                    # Assign polarity and subjectivity
                    results[-1].set_sentiment_analysis()

                else:
                    # TODO: Evaluate how to properly handle this
                    print(f"Could not fetch commit details for {repo_name}")

    print(results)
                    
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
        raise Exception("GitHub took too long to compile statistics. Please try again later.")
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