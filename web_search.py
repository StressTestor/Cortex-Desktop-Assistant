import os
import requests

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")

def search_brave(query, count=3):
    if not BRAVE_API_KEY:
        return "Web search is not available: Brave API key missing."
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY}
    params = {"q": query, "count": count}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        results = resp.json()
        hits = results.get("web", {}).get("results", [])
        if hits:
            first = hits[0]
            title = first.get("title", "No title")
            desc = first.get("description", "No description")
            url = first.get("url", "")
            return f"{title}: {desc}\nSource: {url}"
        return "Sorry, I couldn't find any relevant results."
    except Exception as e:
        return f"Web search failed: {e}"
