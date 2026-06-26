"""
Username Enumeration Module
Checks for the existence of a username across multiple social platforms.
"""

import requests


# Platform URL templates — {username} is replaced at runtime
PLATFORMS = {
    "GitHub": "https://github.com/{username}",
    "GitLab": "https://gitlab.com/{username}",
    "Reddit": "https://www.reddit.com/user/{username}",
    "Medium": "https://medium.com/@{username}",
    "Pinterest": "https://www.pinterest.com/{username}/",
}


def enumerate_user(username):
    """
    Check whether a username exists on each platform.

    Args:
        username (str): The username to search.

    Returns:
        dict: {platform_name: bool} indicating presence on each platform.
    """
    if not username or not username.strip():
        return {platform: False for platform in PLATFORMS}

    username = username.strip()
    results = {}

    for platform, url_template in PLATFORMS.items():
        url = url_template.format(username=username)
        try:
            response = requests.get(
                url,
                timeout=5,
                headers={"User-Agent": "OSINT-Lite/1.0"},
                allow_redirects=True,
            )
            # 200 means the profile page exists
            results[platform] = response.status_code == 200
        except requests.exceptions.RequestException:
            # Network error — mark as not found rather than crashing
            results[platform] = False

    return results
