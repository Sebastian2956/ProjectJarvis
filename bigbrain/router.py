# bigbrain/router.py

from models import ask_deepseek_light

SYSTEM_PROMPT = """
You are Jarvis's router.

Return exactly ONE route:
browser
coding
interpreter
reasoning

Definitions:
browser = any request that asks to search, look up, find online/current/recent/latest info, open a URL, browse a site, check a release date, reviews, prices, versions, news, drivers, documentation, or anything that may have changed over time
coding = writing/debugging/explaining/refactoring code, apps, APIs, databases, scripts, architecture
interpreter = local computer actions: terminal commands, files/folders, installs, launching apps, checking versions, running scripts
reasoning = normal chat, conceptual explanations, opinions, planning, advice, comparisons that do NOT require current web info or local execution

Priority rules:
1. If the user says search, look up, find, browse, website, URL, latest, current, recent, online, release date, price, reviews, news, version, or driver → browser
2. If the user wants a local command/action → interpreter
3. If the user wants code help → coding
4. Otherwise → reasoning

Only output one lowercase route word.
No explanation.
"""

def route_request(user_input: str):

    prompt = f"""
        User request:
        {user_input}
    """

    response = ask_deepseek_light(
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