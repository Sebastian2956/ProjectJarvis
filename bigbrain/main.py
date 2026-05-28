# bigbrain/main.py

#blocks extra output from browser_use
#######################################################
import logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger("browser_use").setLevel(logging.ERROR)
logging.getLogger("browser_use.agent").setLevel(logging.ERROR)
logging.getLogger("browser_use.browser").setLevel(logging.ERROR)
logging.getLogger("browser_use.service").setLevel(logging.ERROR)
##########################################################logging.getLogger("browser_use.telemetry").setLevel(logging.ERROR)

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


while True:

    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Jarvis shutting down.")
        break

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

    print(result)