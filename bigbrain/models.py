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

def ask_deepseek_1_5(prompt: str):

    response = ollama.chat(
        model="deepseek-r1:1.5b",
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
            "num_ctx": 8192,
            "temperature": 0.2
        }
    )

    return response["message"]["content"]