# bigbrain/models.py

import re
import time

import ollama

from config import (
    OLLAMA_KEEP_ALIVE,
    OLLAMA_MODEL_CODING,
    OLLAMA_MODEL_GENERAL,
    OLLAMA_MODEL_INTERPRETER_REWRITE,
    OLLAMA_MODEL_ROUTER,
    OLLAMA_MODEL_SEARCH_REWRITE,
    OLLAMA_NUM_CTX,
)


CODING_SYSTEM_PROMPT = """
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

SEARCH_REWRITE_SYSTEM_PROMPT = (
    "You rewrite user browser/search requests into clean standalone search queries. "
    "Return only the query."
)

INTERPRETER_REWRITE_SYSTEM_PROMPT = """
You rewrite local computer/terminal requests into safe Windows PowerShell commands.

Return only one command.

Rules:
- Use conversation context to resolve vague references.
- Do not explain.
- Do not use markdown.
- Avoid destructive commands.
- If the command could delete, overwrite, format, kill important processes, expose secrets, or is ambiguous, return NEEDS_CONFIRMATION.
"""

THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)
OPEN_THINK_RE = re.compile(r"<think>.*$", re.IGNORECASE | re.DOTALL)
SENTENCE_RE = re.compile(r"(.+?[.!?])(?=\s|$)", re.DOTALL)
EMOJI_RE = re.compile(
    "["
    "\U0001F1E6-\U0001F1FF"
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FAFF"
    "\u2600-\u27BF"
    "\uFE0F"
    "\u200D"
    "]+"
)


def _base_options(extra_options=None):
    options = {
        "num_ctx": OLLAMA_NUM_CTX,
    }

    if extra_options:
        options.update(extra_options)

    return options


def _chat(model: str, messages, options=None):
    response = ollama.chat(
        model=model,
        messages=messages,
        options=_base_options(options),
        keep_alive=OLLAMA_KEEP_ALIVE,
    )

    return response["message"]["content"]


def strip_thinking(text: str):
    """
    Removes DeepSeek thinking blocks from text that may be incomplete mid-stream.
    """

    without_closed_blocks = THINK_BLOCK_RE.sub("", text)
    return OPEN_THINK_RE.sub("", without_closed_blocks)


def clean_spoken_text(text: str):
    cleaned = strip_thinking(text)
    cleaned = EMOJI_RE.sub("", cleaned)
    cleaned = cleaned.replace("\r", " ").replace("\n", " ")
    cleaned = re.sub(r"\s+([,.!?;:])", r"\1", cleaned)

    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")

    return cleaned.strip()


def pop_complete_sentences(buffer: str):
    """
    Pops complete sentence-like chunks from a streaming text buffer.
    """

    sentences = []
    remaining = buffer

    while True:
        match = SENTENCE_RE.search(remaining)

        if not match:
            break

        sentence = clean_spoken_text(match.group(1))

        if sentence:
            sentences.append(sentence)

        remaining = remaining[match.end():].lstrip()

    return sentences, remaining


def stream_chat_sentences(model: str, messages, options=None):
    """
    Streams an Ollama chat response as natural sentence chunks.
    Yields sentence events followed by one done event containing full text and timings.
    """

    start = time.perf_counter()
    first_token_at = None
    first_sentence_at = None
    raw_text = ""
    spoken_cursor = 0
    sentence_buffer = ""

    for chunk in ollama.chat(
        model=model,
        messages=messages,
        options=_base_options(options),
        stream=True,
        keep_alive=OLLAMA_KEEP_ALIVE,
    ):
        piece = chunk.get("message", {}).get("content", "")

        if not piece:
            continue

        now = time.perf_counter()

        if first_token_at is None:
            first_token_at = now

        raw_text += piece

        speakable_text = clean_spoken_text(raw_text)
        new_speakable_text = speakable_text[spoken_cursor:]

        if not new_speakable_text:
            continue

        spoken_cursor = len(speakable_text)
        sentence_buffer += new_speakable_text

        sentences, sentence_buffer = pop_complete_sentences(sentence_buffer)

        for sentence in sentences:
            if first_sentence_at is None:
                first_sentence_at = time.perf_counter()

            yield {
                "type": "sentence",
                "text": sentence,
            }

    full_text = clean_spoken_text(raw_text)
    final_delta = full_text[spoken_cursor:]

    if final_delta:
        sentence_buffer += final_delta

    final_sentence = clean_spoken_text(sentence_buffer)

    if final_sentence:
        if first_sentence_at is None:
            first_sentence_at = time.perf_counter()

        yield {
            "type": "sentence",
            "text": final_sentence,
        }

    total_at = time.perf_counter()

    yield {
        "type": "done",
        "text": full_text,
        "timings": {
            "llm_model": model,
            "llm_first_token_s": None
            if first_token_at is None
            else first_token_at - start,
            "llm_first_sentence_s": None
            if first_sentence_at is None
            else first_sentence_at - start,
            "llm_total_s": total_at - start,
        },
    }


def stream_deepseek(prompt: str):
    return stream_chat_sentences(
        model=OLLAMA_MODEL_GENERAL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )


def stream_qwen_coder(prompt: str):
    return stream_chat_sentences(
        model=OLLAMA_MODEL_CODING,
        messages=[
            {
                "role": "system",
                "content": CODING_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        options={
            "temperature": 0.2,
        },
    )


def ask_deepseek(prompt: str):
    return _chat(
        model=OLLAMA_MODEL_GENERAL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )


def ask_deepseek_light(prompt: str):
    return _chat(
        model=OLLAMA_MODEL_ROUTER,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )


def ask_qwen_coder(prompt: str):
    return _chat(
        model=OLLAMA_MODEL_CODING,
        messages=[
            {
                "role": "system",
                "content": CODING_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        options={
            "temperature": 0.2,
        },
    )


def rewrite_search_query(prompt: str):
    response = _chat(
        model=OLLAMA_MODEL_SEARCH_REWRITE,
        messages=[
            {
                "role": "system",
                "content": SEARCH_REWRITE_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        options={
            "temperature": 0.1,
        },
    )

    return response.strip()


def rewrite_interpreter_command(prompt: str):
    response = _chat(
        model=OLLAMA_MODEL_INTERPRETER_REWRITE,
        messages=[
            {
                "role": "system",
                "content": INTERPRETER_REWRITE_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        options={
            "temperature": 0.0,
        },
    )

    return response.strip()
