# bigbrain/jarvis_core.py

import time

from router import route_request
from tools import TOOLS
from models import (
    ask_deepseek,
    rewrite_search_query,
    rewrite_interpreter_command,
    stream_deepseek,
    stream_qwen_coder,
)

from context import (
    add_message,
    build_context_prompt,
    build_tool_result_prompt,
    build_search_rewrite_prompt,
    build_interpreter_rewrite_prompt,
)

from memory_client import save_long_term_memory
from memory_rules import should_save_memory, clean_memory_text


def _timed(timings: dict, name: str, func):
    start = time.perf_counter()
    result = func()
    timings[name] = time.perf_counter() - start
    return result


def _stream_prompt(stream_factory, prompt: str, timings: dict):
    final_text = ""

    for event in stream_factory(prompt):
        if event["type"] == "sentence":
            yield event

        if event["type"] == "done":
            final_text = event.get("text", "")
            timings.update(event.get("timings", {}))

    return final_text


def handle_user_input(user_input: str):
    """
    Main Jarvis brain.
    Takes user text and returns Jarvis text response.
    This remains the blocking path for terminal/text mode.
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

    print(f"\n[ROUTER] -> {route}\n")

    if route == "browser":

        rewrite_prompt = build_search_rewrite_prompt(user_input)
        browser_query = rewrite_search_query(rewrite_prompt)

        print(f"[SEARCH QUERY] -> {browser_query}\n")

        tool_result = TOOLS["browser"](browser_query)

        final_prompt = build_tool_result_prompt(
            user_input=user_input,
            route=route,
            tool_result=tool_result,
        )

        result = ask_deepseek(final_prompt)

    elif route == "interpreter":

        rewrite_prompt = build_interpreter_rewrite_prompt(user_input)
        command = rewrite_interpreter_command(rewrite_prompt)

        print(f"[COMMAND] -> {command}\n")

        tool_result = TOOLS["interpreter"](command)

        final_prompt = build_tool_result_prompt(
            user_input=user_input,
            route=route,
            tool_result=tool_result,
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
            route=route,
        )

        tool = TOOLS[route]
        result = tool(tool_input)

    add_message("user", user_input)
    add_message("assistant", result)

    return result


def stream_voice_response(user_input: str):
    """
    Voice-only streaming path.
    Yields sentence events as soon as natural speech chunks are available,
    then yields one done event with the final text and timing data.
    """

    timings = {}
    route = None
    final_text = ""

    if should_save_memory(user_input):
        memory_text = clean_memory_text(user_input)
        memory_result = _timed(
            timings,
            "memory_save_s",
            lambda: save_long_term_memory(memory_text, memory_type="user_provided"),
        )

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

        final_text = yield from _stream_prompt(stream_deepseek, final_prompt, timings)

        add_message("user", user_input)
        add_message("assistant", final_text)

        yield {
            "type": "done",
            "route": "memory",
            "text": final_text,
            "timings": timings,
        }
        return

    route = _timed(timings, "router_s", lambda: route_request(user_input))

    print(f"\n[ROUTER] -> {route}\n")

    if route == "browser":
        rewrite_prompt = _timed(
            timings,
            "search_prompt_s",
            lambda: build_search_rewrite_prompt(user_input),
        )
        browser_query = _timed(
            timings,
            "search_rewrite_s",
            lambda: rewrite_search_query(rewrite_prompt),
        )

        print(f"[SEARCH QUERY] -> {browser_query}\n")

        tool_result = _timed(
            timings,
            "browser_tool_s",
            lambda: TOOLS["browser"](browser_query),
        )

        final_prompt = _timed(
            timings,
            "final_prompt_s",
            lambda: build_tool_result_prompt(
                user_input=user_input,
                route=route,
                tool_result=tool_result,
            ),
        )

        final_text = yield from _stream_prompt(stream_deepseek, final_prompt, timings)

    elif route == "interpreter":
        rewrite_prompt = _timed(
            timings,
            "interpreter_prompt_s",
            lambda: build_interpreter_rewrite_prompt(user_input),
        )
        command = _timed(
            timings,
            "interpreter_rewrite_s",
            lambda: rewrite_interpreter_command(rewrite_prompt),
        )

        print(f"[COMMAND] -> {command}\n")

        tool_result = _timed(
            timings,
            "interpreter_tool_s",
            lambda: TOOLS["interpreter"](command),
        )

        final_prompt = f"""
Recent tool result:

Command run:
{command}

Tool output:
{tool_result}

Respond for voice mode.
Briefly say what happened.
Do not read long raw output unless the user explicitly asked for it.
Do not mention internal routing.
"""

        final_text = yield from _stream_prompt(stream_deepseek, final_prompt, timings)

    else:
        tool_input = _timed(
            timings,
            "context_prompt_s",
            lambda: build_context_prompt(
                user_input=user_input,
                route=route,
            ),
        )

        if route == "coding":
            final_text = yield from _stream_prompt(
                stream_qwen_coder,
                tool_input,
                timings,
            )
        else:
            final_text = yield from _stream_prompt(
                stream_deepseek,
                tool_input,
                timings,
            )

    add_message("user", user_input)
    add_message("assistant", final_text)

    yield {
        "type": "done",
        "route": route,
        "text": final_text,
        "timings": timings,
    }
