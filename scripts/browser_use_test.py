import asyncio

from browser_use import Agent, Browser, BrowserProfile
from browser_use.llm import ChatOllama


BROWSER_SYSTEM_PROMPT = """
You are Jarvis's browser agent.

You must follow these rules:

1. Prefer direct URLs over typing into search boxes.
2. For search tasks, use DuckDuckGo direct search URLs:
   https://duckduckgo.com/?q=<url_encoded_query>
3. Do NOT use Google unless explicitly requested.
5. Do NOT use Bing if Google/DuckDuckGo fail unless explicitly requested.
6. Do NOT click autocomplete suggestions unless absolutely necessary.
7. If a page shows CAPTCHA, Cloudflare, 403 Forbidden, or an error page:
   - stop using that site immediately
   - try a different allowed source
   - do not repeatedly retry the same blocked site
8. As soon as you find the requested answer:
   - call done
   - return only the useful final answer
   - do not continue browsing
9. If the task is a simple factual lookup, keep the answer short.
10. Never browse after the answer is visible.
"""


llm = ChatOllama(
    model="qwen2.5-coder:14b",
)


browser = Browser(
    browser_profile=BrowserProfile(
        headless=False
    )
)


async def main():

    user_request = """
    Find the release date of Spider-Man No Way Home.
    Return only the release date.
    """

    task = f"""
    {BROWSER_SYSTEM_PROMPT}

    User request:
    {user_request}
    """

    agent = Agent(

        task=task,

        llm=llm,

        browser=browser,

        max_actions_per_step=1,

        max_failures=3,
    )

    result = await agent.run(max_steps=6)

    print("\nFINAL ANSWER:\n")
    print(result.final_result())


asyncio.run(main())