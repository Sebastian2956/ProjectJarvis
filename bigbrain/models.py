# bigbrain/models.py

import ollama


def ask_deepseek(prompt: str):

    response = ollama.chat(
        model="deepseek-r1:14b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "num_ctx": 4096
        }
    )

    return response["message"]["content"]

def ask_deepseek_light(prompt: str):

    response = ollama.chat(
        model="deepseek-r1:7b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "num_ctx": 4096
        }
    )

    return response["message"]["content"]

def ask_qwen_coder(prompt: str):

    response = ollama.chat(
        model="qwen2.5-coder:14b",
        messages=[
            {
                "role": "system",
                "content": """
                    You are Jarvis's coding specialist.

                    Help with software development tasks:
                    - writing code
                    - debugging code
                    - explaining code
                    - refactoring code
                    - designing files/functions/classes
                    - suggesting tests

                    Do not claim you ran code unless a terminal/interpreter tool actually ran it.
                    If the user asks to execute commands, say the interpreter tool should handle that.
                    Keep answers practical and code-focused.
                    """
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "num_ctx": 4096,
            "temperature": 0.2
        }
    )

    return response["message"]["content"]

def rewrite_search_query(prompt: str):

    response = ollama.chat(
        model="qwen2.5-coder:14b",
        messages=[
            {
                "role": "system",
                "content": "You rewrite user browser/search requests into clean standalone search queries. Return only the query."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "num_ctx": 4096,
            "temperature": 0.1
        }
    )

    return response["message"]["content"].strip()

def rewrite_interpreter_command(prompt: str):

    response = ollama.chat(
        model="qwen2.5-coder:14b",
        messages=[
            {
                "role": "system",
                "content": """
                    You rewrite local computer/terminal requests into safe Windows PowerShell commands.

                    Return only one command.

                    Rules:
                    - Use conversation context to resolve vague references.
                    - Do not explain.
                    - Do not use markdown.
                    - Avoid destructive commands.
                    - If the command could delete, overwrite, format, kill important processes, expose secrets, or is ambiguous, return NEEDS_CONFIRMATION.
                    """
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "num_ctx": 4096,
            "temperature": 0.0
        }
    )

    return response["message"]["content"].strip()