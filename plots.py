import git_parser
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import re
from wordcloud import WordCloud
from sklearn.tree import DecisionTreeClassifier
from datetime import datetime
import requests
from sklearn.tree import plot_tree

# --- 1. ACTIVITY HISTOGRAMS ---
def generate_histogram(username: str) -> plt.Figure:
    """Generates a combined figure with Time of Day and Day of Week histograms."""
    commits = git_parser.get_user_activity(username, pages=2)

    if not commits:
        raise ValueError(f"No recent activity found for user {username}.")
        
    df = pd.DataFrame([c.to_dict() for c in commits])
    df['date'] = pd.to_datetime(df['timestamp'])
    
    # Setup Figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    
    # Plot 1: Time of Day
    df['hour'] = df['date'].dt.hour
    bins = [0, 6, 12, 18, 24]
    labels = ['Late Night (0-6)', 'Morning (6-12)', 'Afternoon (12-18)', 'Evening (18-24)']
    df['time_block'] = pd.cut(df['hour'], bins=bins, labels=labels, right=False)
    
    sns.countplot(data=df, x='time_block', ax=ax1, palette='Blues_d', order=labels)
    ax1.set_title("Contributions by Time of Day")
    ax1.set_xlabel("Time Block")
    ax1.set_ylabel("Number of Commits")
    ax1.tick_params(axis='x', rotation=45)

    # Plot 2: Day of Week
    df['day'] = df['date'].dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    sns.countplot(data=df, x='day', ax=ax2, palette='viridis', order=day_order)
    ax2.set_title("Contributions by Day of the Week")
    ax2.set_xlabel("Day of Week")
    ax2.set_ylabel("Number of Commits")
    ax2.tick_params(axis='x', rotation=45)

    fig.tight_layout()
    return fig

# --- 2. WORD CLOUD ---
def generate_wordcloud(username: str) -> plt.Figure:
    """Generates a word cloud from a user's commit messages."""
    commits = git_parser.get_user_activity(username, pages=2)
    if not commits:
        raise ValueError(f"No recent activity found for user {username}.")

    # Extract all messages
    full_text = " ".join([c.message for c in commits])
    
    # Filter out non-alphabetic characters (per requirements)
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', full_text)

    if not cleaned_text.strip():
         raise ValueError("No valid English words found in commit messages.")

    # Generate Word Cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='tab20').generate(cleaned_text)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(f"Commit Message Word Cloud for {username}", fontsize=16)
    
    return fig

# --- 3. TOP USERS BAR CHART (REPO) ---
def generate_top_users_barchart(repo_url: str, top_n: int = 10) -> plt.Figure:
    """Generates a positive/negative bar chart of lines added and deleted."""
    try:
        url_type, owner, repo = git_parser.parse_github_url(repo_url)
        if url_type != "repo":
            raise ValueError("Please provide a valid repository URL.")
            
        df = git_parser.get_repo_contributor_stats(owner, repo)
    except Exception as e:
        raise ValueError(f"Error fetching repo stats: {e}")

    if df.empty:
        raise ValueError("No contributor data found for this repository.")

    # Sort by Additions and get top N
    df = df.sort_values(by='Additions', ascending=False).head(top_n)

    fig, ax = plt.subplots(figsize=(8, 4))

    # Plot Positive Y (Additions)
    ax.bar(df['Author'], df['Additions'], color='green', label='Lines Added')
    
    # Plot Negative Y (Deletions)
    ax.bar(df['Author'], -df['Deletions'], color='red', label='Lines Deleted')

    # Formatting
    ax.set_title(f"Top {top_n} Contributors for {repo}", fontsize=16)
    ax.set_xlabel("Top Users (Sorted by Additions)")
    ax.set_ylabel("Lines of Code")
    ax.axhline(0, color='black', linewidth=1) # Center line
    ax.legend()
    ax.tick_params(axis='x', rotation=45)
    
    fig.tight_layout()
    return fig

# --- 4. SENTIMENT SCATTER PLOT ---
def generate_sentiment_scatter(username: str) -> plt.Figure:
    """Shows Deleterious vs Contributory and Informal vs Formal sentiment."""
    commits = git_parser.get_user_activity(username, pages=2)
    if not commits:
        raise ValueError(f"No recent activity found for user {username}.")
        
    df = pd.DataFrame([c.to_dict() for c in commits])
    
    fig, ax = plt.subplots(figsize=(4, 4))
    
    # Polarity (Negative=Deleterious, Positive=Contributory)
    # Subjectivity (Low=Formal/Objective, High=Informal/Subjective)
    sns.scatterplot(data=df, x='polarity', y='subjectivity', ax=ax, alpha=0.7, color='purple')
    
    # Add quadrants
    ax.axhline(0.5, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(0, color='gray', linestyle='--', alpha=0.5)
    
    ax.set_title(f"Commit Message Sentiment for {username}")
    ax.set_xlabel("Polarity (Deleterious <---> Contributory)")
    ax.set_ylabel("Subjectivity (Formal <---> Informal)")
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    
    return fig

# --- 5. MACHINE LEARNING DECISION TREE ---
def generate_decision_tree(username: str) -> plt.Figure:
    """Trains a Decision Tree to predict if a commit is Contributory or Deleterious."""
    # We use 1 page here so we don't hit the API rate limit when doing deep-dives
    commits = git_parser.get_user_activity(username, pages=1)
    
    if not commits:
        raise ValueError(f"No recent activity found for user {username}.")

    data = []
    commits = commits[:30] # Limited to avoid time out
    
    # We need to fetch the exact additions/deletions for these commits to build our target label
    headers = git_parser.HEADERS
    for c in commits:
        url = f"https://api.github.com/repos/{c.repo}/commits/{c.sha}"
        res = requests.get(url, headers=headers)
        
        if res.status_code == 200:
            stats = res.json().get('stats', {})
            adds = stats.get('additions', 0)
            dels = stats.get('deletions', 0)
            
            # Target Label: 1 if Contributory (more additions), 0 if Deleterious (more deletions)
            label = 1 if adds > dels else 0
            
            hour = c.timestamp.hour
            polarity = c.polarity if c.polarity is not None else 0.0
            subjectivity = c.subjectivity if c.subjectivity is not None else 0.0
            msg_len = len(c.message)
            
            data.append([hour, polarity, subjectivity, msg_len, label])

    df = pd.DataFrame(data, columns=['Hour', 'Polarity', 'Subjectivity', 'MessageLength', 'Class'])

    # The Decision Tree requires at least two types of classes to learn how to split them
    if df.empty or len(df['Class'].unique()) < 2:
        raise ValueError("Not enough diverse commit data to train a model. (User must have BOTH additions and deletions recently).")

    # X = Features (What we use to predict), y = Target (What we are predicting)
    X = df[['Hour', 'Polarity', 'Subjectivity', 'MessageLength']]
    y = df['Class']

    # Train the Machine Learning Model! (Max depth 3 keeps the visual chart readable)
    clf = DecisionTreeClassifier(max_depth=3, random_state=42)
    clf.fit(X, y)

    # Draw the Decision Tree
    fig, ax = plt.subplots(figsize=(14, 8))
    plot_tree(
        clf, 
        feature_names=X.columns.tolist(), 
        class_names=['Deleterious', 'Contributory'], 
        filled=True, 
        rounded=True, 
        ax=ax, 
        fontsize=10
    )
    
    ax.set_title(f"Machine Learning: Predicting Commit Type for {username}", fontsize=16)
    
    fig.tight_layout()
    return fig

# --- 6. CONTRIBUTION LINE CHART (REPO) ---
def generate_line_chart(repo_url: str) -> plt.Figure:
    """Generates a line chart showing commits over the last 52 weeks for a repo."""
    try:
        url_type, owner, repo = git_parser.parse_github_url(repo_url)
        if url_type != "repo":
            raise ValueError("Please provide a valid repository URL.")
    except Exception as e:
        raise ValueError(f"Error parsing URL: {e}")

    # Hit the specific GitHub endpoint for repository commit activity
    url = f"https://api.github.com/repos/{owner}/{repo}/stats/commit_activity"
    response = requests.get(url, headers=git_parser.HEADERS)
    
    # GitHub returns 202 if it needs to calculate this data in the background
    if response.status_code == 202:
        raise Exception("GitHub is compiling these statistics. Please click 'Generate' again in a few seconds.")
    elif response.status_code != 200:
        raise Exception(f"Failed to fetch repo stats ({response.status_code}): {response.text}")

    data = response.json()
    if not data:
        raise ValueError("No commit activity found for this repository.")

    # Extract the weeks (Unix timestamps) and totals
    weeks = []
    totals = []
    for week_data in data:
        week_date = datetime.fromtimestamp(week_data['week'])
        weeks.append(week_date)
        totals.append(week_data['total'])

    # Draw the Line Chart
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(x=weeks, y=totals, ax=ax, marker="o", color="#238636", linewidth=2)
    
    # Add a nice shaded area under the line
    ax.fill_between(weeks, totals, color="#238636", alpha=0.2)

    # Formatting
    ax.set_title(f"Yearly Commit Activity for {repo}", fontsize=16)
    ax.set_xlabel("Date")
    ax.set_ylabel("Total Commits per Week")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.tick_params(axis='x', rotation=45)
    
    fig.tight_layout()
    return fig
