import os
import requests
import logging

def check_email_breach(email: str) -> dict:
    """
    Check if an email has been breached using the Have I Been Pwned API.
    Returns:
        {
            "breached": bool,
            "count": int,
            "breaches": list[str]
        }
    """
    if not email:
        return {"breached": False, "count": 0, "breaches": []}

    api_key = os.environ.get("HIBP_API_KEY")
    if not api_key:
        logging.warning("HIBP_API_KEY not found in environment. Using mock data for portfolio demonstration.")
        # Mock data for demonstration when API key is missing
        if "test" in email.lower() or "admin" in email.lower():
            return {
                "breached": True,
                "count": 3,
                "breaches": ["LinkedIn", "Dropbox", "Canva"]
            }
        return {"breached": False, "count": 0, "breaches": []}

    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false"
    headers = {
        "hibp-api-key": api_key,
        "user-agent": "OSINT-Pro-App"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            breaches = [item.get("Name") for item in data if "Name" in item]
            return {
                "breached": len(breaches) > 0,
                "count": len(breaches),
                "breaches": breaches
            }
        elif response.status_code == 404:
            return {"breached": False, "count": 0, "breaches": []}
        else:
            logging.error(f"HIBP API error: {response.status_code} - {response.text}")
            return {"breached": False, "count": 0, "breaches": []}
    except Exception as e:
        logging.error(f"Exception during HIBP lookup: {str(e)}")
        return {"breached": False, "count": 0, "breaches": []}
