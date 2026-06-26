"""
Social Discovery Module
Discovers social-media profiles for a given username across multiple platforms.
Returns richer data than the basic username_search module (URL, status, follower hints).
"""

import requests

# Platform definitions: name → (url template, profile URL pattern)
PLATFORMS = {
    "GitHub": {
        "check_url": "https://api.github.com/users/{username}",
        "profile_url": "https://github.com/{username}",
        "api": True,
    },
    "Reddit": {
        "check_url": "https://www.reddit.com/user/{username}/about.json",
        "profile_url": "https://www.reddit.com/user/{username}",
        "api": True,
    },
    "GitLab": {
        "check_url": "https://gitlab.com/{username}",
        "profile_url": "https://gitlab.com/{username}",
        "api": False,
    },
    "Medium": {
        "check_url": "https://medium.com/@{username}",
        "profile_url": "https://medium.com/@{username}",
        "api": False,
    },
    "Pinterest": {
        "check_url": "https://www.pinterest.com/{username}/",
        "profile_url": "https://www.pinterest.com/{username}/",
        "api": False,
    },
    "Twitter / X": {
        "check_url": "https://x.com/{username}",
        "profile_url": "https://x.com/{username}",
        "api": False,
    },
}

HEADERS = {
    "User-Agent": "OSINT-Pro/2.0 (Due Diligence Investigation Platform)",
    "Accept": "application/json, text/html",
}


def discover_profiles(username):
    """
    Discover social-media profiles for *username*.

    Args:
        username (str): The handle / username to search.

    Returns:
        list[dict]: Each dict contains:
            - platform  (str)
            - found     (bool)
            - url       (str)   profile URL
            - followers (int|None)
    """
    if not username or not username.strip():
        return [
            {"platform": p, "found": False, "url": "", "followers": None}
            for p in PLATFORMS
        ]

    username = username.strip()
    results = []

    for platform, cfg in PLATFORMS.items():
        url = cfg["check_url"].format(username=username)
        profile_url = cfg["profile_url"].format(username=username)
        found = False
        followers = None

        try:
            resp = requests.get(url, timeout=6, headers=HEADERS, allow_redirects=True)

            if platform == "GitHub" and resp.status_code == 200:
                found = True
                try:
                    data = resp.json()
                    followers = data.get("followers")
                except (ValueError, KeyError):
                    pass

            elif platform == "Reddit" and resp.status_code == 200:
                found = True
                try:
                    data = resp.json()
                    karma = data.get("data", {}).get("total_karma")
                    followers = karma  # Reddit exposes karma, not follower count
                except (ValueError, KeyError):
                    pass

            elif resp.status_code == 200:
                found = True

        except requests.exceptions.RequestException:
            found = False

        results.append({
            "platform": platform,
            "found": found,
            "url": profile_url if found else "",
            "followers": followers,
        })

    return results
