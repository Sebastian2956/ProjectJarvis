# bigbrain/context.py

from memory_client import search_long_term_memory


conversation_history = []


def add_message(role: str, content: str):
    """
    Stores a message in short-term memory for the current running session.
    role should be 'user' or 'assistant'.
    """

    conversation_history.append({
        "role": role,
        "content": content
    })


def get_recent_history(max_messages: int = 8):
    """
    Returns the most recent short-term messages.
    """

    return conversation_history[-max_messages:]


def format_recent_history(max_messages: int = 8):
    """
    Converts recent short-term history into readable text for the model.
    """

    recent_messages = get_recent_history(max_messages)

    if not recent_messages:
        return "No previous conversation."

    formatted = []

    for message in recent_messages:
        role = message["role"]
        content = message["content"]

        formatted.append(f"{role.upper()}: {content}")

    return "\n\n".join(formatted)


def get_relevant_long_term_memory(user_input: str, n_results: int = 5):
    """
    Searches persistent long-term memory using memory_venv.
    """

    return search_long_term_memory(user_input, n_results=n_results)


def build_context_prompt(user_input: str, route: str):
    """
    Builds a route-specific prompt using:
    - short-term session memory
    - long-term vector memory
    - current user request
    """

    recent_history = format_recent_history()
    long_term_memory = get_relevant_long_term_memory(user_input)

    if route == "browser":
        return user_input

    if route == "interpreter":
        return user_input

    if route == "coding":
        return f"""
Recent conversation:
{recent_history}

Relevant long-term memory:
{long_term_memory}

Coding request:
{user_input}
"""

    return f"""
Recent conversation:
{recent_history}

Relevant long-term memory:
{long_term_memory}

User request:
{user_input}
"""


def build_tool_result_prompt(user_input: str, route: str, tool_result: str):
    """
    Builds a final response prompt after a tool has been used.
    """

    recent_history = format_recent_history()
    long_term_memory = get_relevant_long_term_memory(user_input)

    return f"""
Recent conversation:
{recent_history}

Relevant long-term memory:
{long_term_memory}

The user asked:
{user_input}

The selected route was:
{route}

The tool returned:
{tool_result}

Now respond to the user naturally and helpfully.
Use the tool result if it is relevant.
Use long-term memory only if it is relevant.
Do not mention internal routing unless necessary.
"""


def build_search_rewrite_prompt(user_input: str):
    """
    Builds a prompt that rewrites the user's browser/search request
    into a clean standalone search query.
    """

    recent_history = format_recent_history()
    long_term_memory = get_relevant_long_term_memory(user_input, n_results=3)

    return f"""
Recent conversation:
{recent_history}

Relevant long-term memory:
{long_term_memory}

Current user search/browser request:
{user_input}

Rewrite the current request into a short, standalone web search query.

Rules:
- Resolve pronouns like he, she, it, his, her, they, that, this using the recent conversation and relevant long-term memory.
- Remove filler words like "yeah", "look up", "can you", "please".
- Keep only the key search terms.
- Do not answer the question.
- Do not explain.
- Return only the rewritten search query.
"""


def build_interpreter_rewrite_prompt(user_input: str):
    """
    Builds a prompt that rewrites the user's local computer/terminal request
    into a clean command.
    """

    recent_history = format_recent_history()
    long_term_memory = get_relevant_long_term_memory(user_input, n_results=3)

    return f"""
Recent conversation:
{recent_history}

Relevant long-term memory:
{long_term_memory}

Current local computer/terminal request:
{user_input}

Rewrite the current request into ONE safe Windows PowerShell command.

Rules:
- Use the recent conversation and relevant long-term memory to resolve words like it, that, this, there, the folder, the file.
- Return only the command.
- Do not explain.
- Do not include markdown.
- Do not wrap the command in backticks.
- Do not include dangerous destructive commands.
- If the request is not safe or not specific enough, return:
NEEDS_CONFIRMATION

Examples:

Recent conversation:
USER: my project is in C:\\AI\\ProjectJarvis
USER: show me the files in it

Output:
dir C:\\AI\\ProjectJarvis

Recent conversation:
USER: I am working in ProjectJarvis
USER: check what python version I have

Output:
python --version

Recent conversation:
USER: delete everything in that folder

Output:
NEEDS_CONFIRMATION
"""