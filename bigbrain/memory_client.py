# bigbrain/memory_client.py

import requests


MEMORY_SERVER_URL = "http://127.0.0.1:7010"


def save_long_term_memory(text: str, memory_type: str = "general"):
    try:
        response = requests.post(
            f"{MEMORY_SERVER_URL}/save",
            json={
                "text": text,
                "memory_type": memory_type
            },
            timeout=30
        )

        data = response.json()

        if not data.get("ok"):
            return f"Long-term memory save failed: {data.get('error')}"

        return data.get("result", "Memory saved.")

    except Exception as e:
        return f"Long-term memory save failed: {e}"


def search_long_term_memory(query: str, n_results: int = 5):
    try:
        response = requests.post(
            f"{MEMORY_SERVER_URL}/search",
            json={
                "query": query,
                "n_results": n_results
            },
            timeout=30
        )

        data = response.json()

        if not data.get("ok"):
            return f"Long-term memory search failed: {data.get('error')}"

        return data.get("result", "No relevant long-term memories.")

    except Exception as e:
        return f"Long-term memory search failed: {e}"