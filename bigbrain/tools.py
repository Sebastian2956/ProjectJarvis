import asyncio
import subprocess
from urllib.parse import quote_plus

from models import ask_deepseek, ask_qwen_coder

from config import OLLAMA_MODEL_BROWSER
from safety import is_safe_command

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


browser_llm = None


def get_browser_llm():
    global browser_llm

    if browser_llm is None:
        from browser_use.llm import ChatOllama

        browser_llm = ChatOllama(
            model=OLLAMA_MODEL_BROWSER,
        )

    return browser_llm


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
    from browser_use import Agent, Browser, BrowserProfile

    browser = Browser(
        browser_profile=BrowserProfile(
            headless=False
        )
    )

    agent = Agent(
        task=build_browser_task(user_request),
        llm=get_browser_llm(),
        browser=browser,
        use_vision=False,
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

    if not is_safe_command(command):
        return f"""[INTERPRETER BLOCKED]
            Reason: This command may be unsafe or needs confirmation.
            Command was not executed.
            Command:
            {command}
            """

    try:
        result = subprocess.check_output(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                command
            ],
            text=True,
            stderr=subprocess.STDOUT
        )

        if not result.strip():
            return "[INTERPRETER] Command ran successfully with no output."

        return result

    except Exception as e:
        return f"""[INTERPRETER ERROR]
            Command:
            {command}

            Error:
            {e}
            """


def reasoning_tool(prompt: str):

    return ask_deepseek(prompt)

TOOLS = {
    "browser": browser_tool,
    "coding": coding_tool,
    "interpreter": interpreter_tool,
    "reasoning": reasoning_tool
}
