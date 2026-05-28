import asyncio
import subprocess
from urllib.parse import quote_plus

from models import ask_deepseek, ask_qwen_coder

from browser_use import Agent, Browser, BrowserProfile
from browser_use.llm import ChatOllama

BROWSER_SYSTEM_PROMPT = """
You are Jarvis's browser agent.

Rules:
1. Prefer direct URLs over typing into search boxes.
2. Use DuckDuckGo for search tasks unless the user explicitly asks for another site.
3. Do NOT use Google unless explicitly requested.
4. Do NOT use Bing unless explicitly requested.
5. Do NOT click autocomplete suggestions unless absolutely necessary.
6. If a page shows CAPTCHA, Cloudflare, 403 Forbidden, or an error page:
   - stop using that site immediately
   - do not repeatedly retry the same blocked site
7. As soon as you find the requested answer:
   - call done
   - return only the useful final answer
   - do not continue browsing
8. Keep simple factual answers short.
"""


browser_llm = ChatOllama(
    model="qwen2.5-coder:14b",
)


def build_browser_task(user_request: str):

    search_url = f"https://duckduckgo.com/?q={quote_plus(user_request)}"

    return f"""
{BROWSER_SYSTEM_PROMPT}

User request:
{user_request}

Start by navigating directly to:
{search_url}
"""


async def run_browser_agent(user_request: str):

    browser = Browser(
        browser_profile=BrowserProfile(
            headless=False
        )
    )

    agent = Agent(
        task=build_browser_task(user_request),
        llm=browser_llm,
        browser=browser,
        max_actions_per_step=1,
        max_failures=3,
    )

    result = await agent.run(max_steps=6)

    return result.final_result()


def browser_tool(query: str):

    try:
        return asyncio.run(run_browser_agent(query))

    except Exception as e:
        return f"[BROWSER TOOL ERROR] {e}"

def coding_tool(prompt: str):

    return ask_qwen_coder(prompt)


def interpreter_tool(command: str):

    try:

        result = subprocess.check_output(
            command,
            shell=True,
            text=True
        )

        return result

    except Exception as e:

        return str(e)


def reasoning_tool(prompt: str):

    return ask_deepseek(prompt)

TOOLS = {
    "browser": browser_tool,
    "coding": coding_tool,
    "interpreter": interpreter_tool,
    "reasoning": reasoning_tool
}
