"""
GitHub Intelligence Module
Queries the GitHub REST API for public user profile data.
"""

import requests


def github_lookup(username):
    """
    Look up a GitHub user profile by username.

    Args:
        username (str): GitHub username to search.

    Returns:
        dict: Profile data or error information.
    """
    if not username or not username.strip():
        return {"error": "No username provided", "found": False}

    username = username.strip()
    url = f"https://api.github.com/users/{username}"

    try:
        response = requests.get(url, timeout=5, headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OSINT-Lite/1.0"
        })

        if response.status_code == 200:
            data = response.json()
            return {
                "found": True,
                "name": data.get("name", "N/A"),
                "bio": data.get("bio", "N/A"),
                "followers": data.get("followers", 0),
                "following": data.get("following", 0),
                "repos": data.get("public_repos", 0),
                "created_at": data.get("created_at", "N/A"),
                "profile_url": data.get("html_url", ""),
                "avatar_url": data.get("avatar_url", ""),
                "location": data.get("location", "N/A"),
                "company": data.get("company", "N/A"),
            }

        elif response.status_code == 404:
            return {"error": "GitHub user not found", "found": False}

        elif response.status_code == 403:
            return {"error": "GitHub API rate limit exceeded. Try again later.", "found": False}

        else:
            return {"error": f"GitHub API returned status {response.status_code}", "found": False}

    except requests.exceptions.Timeout:
        return {"error": "GitHub API request timed out", "found": False}

    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to GitHub API", "found": False}

    except requests.exceptions.RequestException as e:
        return {"error": f"GitHub API error: {str(e)}", "found": False}
