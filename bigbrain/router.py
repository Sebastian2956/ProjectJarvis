# bigbrain/router.py

from models import ask_deepseek_1_5


SYSTEM_PROMPT = """
You are Jarvis's router.

Choose exactly ONE route:

browser = user wants web/current info, search, browsing, URLs, websites
coding = user wants code help, debugging, scripts, apps, APIs, databases
interpreter = user wants local computer/terminal actions, files, folders, installs, commands
reasoning = normal chat, explanations, planning, advice, concepts

Rules:
- Reply with only one lowercase word.
- Valid replies: browser, coding, interpreter, reasoning
- No explanation, punctuation, or extra text.
- If unsure, choose reasoning.
"""

def route_request(user_input: str):

    prompt = f"""
        User request:
        {user_input}
    """

    response = ask_deepseek_1_5(
        SYSTEM_PROMPT + prompt
    )

    response = response.strip().lower()

    valid_routes = [
        "browser",
        "coding",
        "interpreter",
        "reasoning"
    ]

    for route in valid_routes:

        if route in response:

            return route

    return "reasoning"