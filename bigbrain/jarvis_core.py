# bigbrain/jarvis_core.py

from router import route_request
from tools import TOOLS
from models import ask_deepseek, rewrite_search_query, rewrite_interpreter_command

from context import (
    add_message,
    build_context_prompt,
    build_tool_result_prompt,
    build_search_rewrite_prompt,
    build_interpreter_rewrite_prompt
)

from memory_client import save_long_term_memory
from memory_rules import should_save_memory, clean_memory_text


def handle_user_input(user_input: str):
    """
    Main Jarvis brain.
    Takes user text and returns Jarvis text response.
    This is shared by both terminal mode and voice mode.
    """

    if should_save_memory(user_input):
        memory_text = clean_memory_text(user_input)
        memory_result = save_long_term_memory(memory_text, memory_type="user_provided")

        final_prompt = f"""
The user asked you to remember something.

Original user message:
{user_input}

Memory saved:
{memory_text}

Memory system result:
{memory_result}

Respond naturally and conversationally.
Confirm that you saved the memory.
Do not mention internal routing.
Do not mention ChromaDB, vector memory, memory_venv, or technical internals.
Keep it short.
"""

        result = ask_deepseek(final_prompt)

        add_message("user", user_input)
        add_message("assistant", result)

        return result

    route = route_request(user_input)

    print(f"\n[ROUTER] → {route}\n")

    if route == "browser":

        rewrite_prompt = build_search_rewrite_prompt(user_input)
        browser_query = rewrite_search_query(rewrite_prompt)

        print(f"[SEARCH QUERY] → {browser_query}\n")

        tool_result = TOOLS["browser"](browser_query)

        final_prompt = build_tool_result_prompt(
            user_input=user_input,
            route=route,
            tool_result=tool_result
        )

        result = ask_deepseek(final_prompt)

    elif route == "interpreter":

        rewrite_prompt = build_interpreter_rewrite_prompt(user_input)
        command = rewrite_interpreter_command(rewrite_prompt)

        print(f"[COMMAND] → {command}\n")

        tool_result = TOOLS["interpreter"](command)

        final_prompt = build_tool_result_prompt(
            user_input=user_input,
            route=route,
            tool_result=tool_result
        )

        summary = ask_deepseek(final_prompt)

        result = f"""
COMMAND RUN:
{command}

RAW OUTPUT:
{tool_result}

SUMMARY:
{summary}
"""

    else:

        tool_input = build_context_prompt(
            user_input=user_input,
            route=route
        )

        tool = TOOLS[route]
        result = tool(tool_input)

    add_message("user", user_input)
    add_message("assistant", result)

    return result