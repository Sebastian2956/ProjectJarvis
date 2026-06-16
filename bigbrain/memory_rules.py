# bigbrain/memory_rules.py

def should_save_memory(user_input: str) -> bool:
    """
    Simple rule-based detector for explicit memory requests.
    This avoids saving every random message.
    """

    text = user_input.lower().strip()

    memory_phrases = [
        "remember that",
        "remember this",
        "save this",
        "save that",
        "memorize this",
        "memorize that",
        "keep in mind",
        "note that",
        "for future reference",
        "from now on",
        "going forward"
    ]

    return any(phrase in text for phrase in memory_phrases)


def clean_memory_text(user_input: str) -> str:
    """
    Removes common memory command phrases so the stored memory is cleaner.
    """

    cleaned = user_input.strip()

    replacements = [
        "remember that",
        "remember this",
        "save this",
        "save that",
        "memorize this",
        "memorize that",
        "keep in mind",
        "note that",
        "for future reference",
        "from now on",
        "going forward"
    ]

    lower_cleaned = cleaned.lower()

    for phrase in replacements:
        if lower_cleaned.startswith(phrase):
            cleaned = cleaned[len(phrase):].strip(" .:-")
            break

    return cleaned