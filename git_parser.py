import requests
from datetime import datetime
from dataclasses import dataclass
from textblob import TextBlob

# TODO: Turn this into a real class
@dataclass
class GitHubCommit:
    repo: str
    sha: str
    timestamp: datetime
    message: str
    polarity: float
    subjectivity: float

# TODO: Implement this!
class GitHubPull:
    pass

def get_commit_from_name(username: str, n: int) -> list[GitHubCommit]:
    """
    Retrieve the last `n` commits from a user's GitHub profile.
    
    This function fetches commit history from GitHub's API for the specified
    username and returns the most recent commits with their metadata.

    Args:
        username (str): GitHub username. Should be sanitized to remove any
            special characters or whitespace before processing.
        n (int): Number of most recent commits to retrieve. Must be positive
            and not exceed the maximum allowed limit (currently 20).

    Returns:
        list[GitHubCommit]: A list of commit objects ordered from most 
            recent to oldest. Each object contains 'repo', 'sha', 
            'timestamp', and 'message' attributes.

    Raises:
        TypeError: If `n` is not an integer.
        ValueError: If:
            - `n` is less than 1
            - `n` exceeds the maximum allowed limit (currently 20)
            - The username is invalid (empty, contains invalid characters)

    Example:
        >>> commits = get_commit_from_name("octocat", 3)
        >>> print(commits[0]['message'])
        'Fix README typo'
        >>> len(commits)
        3
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    user_event_str = f"https://api.github.com/users/{username}/events"
    results = []
    i: int = 0 # Integer to hold our iterations

    response = requests.get(user_event_str, headers=headers) # Added headers here just in case
    response.raise_for_status()

    events_data = response.json()

    for event in events_data[:n]: # Checking more than one in case the first isn't a push
        # TODO: Add Pull event types
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
                    set_sentiment_analysis(results[-1])

                else:
                    # TODO: Evaluate how to properly handle this
                    print(f"Could not fetch commit details for {repo_name}")

    return results

def set_sentiment_analysis(commit: GitHubCommit) -> None:
    blob = TextBlob(commit.message)

    # Get the sentiment scores
    sentiment = blob.sentiment

    commit.polarity = sentiment.polarity # Range: [-1.0, 1.0]
    commit.subjectivity = sentiment.subjectivity # Range: [0.0, 1.0]

def check_n(n: int) -> None:
    """
    Validate n
    """
    if not isinstance(n, int):
        raise TypeError(f"n must be an integer, got {type(n).__name__}")
    
    if n < 1:
        raise ValueError(f"n must be positive, got {n}")
    
    # At the moment, let's define the maximum number of commits to be 20
    if n > 20:
        raise ValueError(f"n cannot exceed {20}, got {n}")

def check_username(username: str) -> None:
    """
    Validate a given GitHub username
    """
    if not isinstance(username, str):
        raise TypeError(f"username must be a string, got {type(username).__name__}")
    
    if not all(c.isalnum() or c == '-' for c in s):
        raise ValueError(f"username is invalid")
