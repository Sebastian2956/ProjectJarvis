# bigbrain/voice_client.py

import re
import time

import requests

from config import STT_SERVER_URL, TTS_SERVER_URL


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


def clean_text_for_speech(text: str):
    cleaned = EMOJI_RE.sub("", text)

    replacements = {
        "```": "",
        "`": "",
        "*": "",
        "#": "",
        "\\": " backslash ",
        "/": " slash ",
        "C:": "C drive",
        "\n": " ",
        "[ROUTER]": "",
        "COMMAND RUN:": "Command run.",
        "RAW OUTPUT:": "Raw output.",
        "SUMMARY:": "Summary.",
    }

    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    cleaned = re.sub(r"\s+([,.!?;:])", r"\1", cleaned)

    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")

    return cleaned.strip()


def listen_once_with_metadata(duration: float = 8):
    started_at = time.perf_counter()

    try:
        response = requests.post(
            f"{STT_SERVER_URL}/listen",
            json={
                "duration": duration,
            },
            timeout=duration + 60,
        )

        ended_at = time.perf_counter()
        data = response.json()
        data["client_timings"] = {
            "request_started_at": started_at,
            "request_ended_at": ended_at,
            "request_s": ended_at - started_at,
        }

        if not data.get("ok"):
            print("[STT ERROR]", data.get("error"))

        return data

    except Exception as e:
        ended_at = time.perf_counter()
        print("[STT ERROR]", e)

        return {
            "ok": False,
            "text": "",
            "error": str(e),
            "client_timings": {
                "request_started_at": started_at,
                "request_ended_at": ended_at,
                "request_s": ended_at - started_at,
            },
        }


def listen_once(duration: float = 8):
    data = listen_once_with_metadata(duration=duration)

    if not data.get("ok"):
        return ""

    return data.get("text", "").strip()


def speak(text: str):
    try:
        text = clean_text_for_speech(text)

        response = requests.post(
            f"{TTS_SERVER_URL}/speak",
            json={
                "text": text,
                "play_audio": True,
            },
            timeout=300,
        )

        data = response.json()

        if not data.get("ok"):
            print("[TTS ERROR]", data.get("error"))

        return data

    except Exception as e:
        print("[TTS ERROR]", e)
        return {
            "ok": False,
            "error": str(e),
        }


def start_utterance(play_audio: bool = True):
    try:
        response = requests.post(
            f"{TTS_SERVER_URL}/utterance/start",
            json={
                "play_audio": play_audio,
            },
            timeout=30,
        )
        data = response.json()

        if not data.get("ok"):
            print("[TTS ERROR]", data.get("error"))

        return data

    except Exception as e:
        print("[TTS ERROR]", e)
        return {
            "ok": False,
            "error": str(e),
        }


def queue_utterance_chunk(utterance_id: str, sequence: int, text: str):
    try:
        cleaned = clean_text_for_speech(text)

        response = requests.post(
            f"{TTS_SERVER_URL}/utterance/chunk",
            json={
                "utterance_id": utterance_id,
                "sequence": sequence,
                "text": cleaned,
            },
            timeout=30,
        )
        data = response.json()

        if not data.get("ok"):
            print("[TTS ERROR]", data.get("error"))

        return data

    except Exception as e:
        print("[TTS ERROR]", e)
        return {
            "ok": False,
            "error": str(e),
        }


def finish_utterance(utterance_id: str, wait: bool = True, timeout: float = 300):
    try:
        response = requests.post(
            f"{TTS_SERVER_URL}/utterance/finish",
            json={
                "utterance_id": utterance_id,
                "wait": wait,
                "timeout": timeout,
            },
            timeout=timeout + 10,
        )
        data = response.json()

        if not data.get("ok"):
            print("[TTS ERROR]", data.get("error"))

        return data

    except Exception as e:
        print("[TTS ERROR]", e)
        return {
            "ok": False,
            "error": str(e),
        }


class QueuedSpeechClient:
    def __init__(self, play_audio: bool = True, timeout: float = 300):
        self.play_audio = play_audio
        self.timeout = timeout
        self.sequence = 0
        self.utterance_id = None
        self.started_at = None
        self.first_chunk_submitted_at = None
        self.chunk_submit_times = {}

    def start(self):
        self.started_at = time.perf_counter()
        data = start_utterance(play_audio=self.play_audio)

        if data.get("ok"):
            self.utterance_id = data.get("utterance_id")

        return data

    def submit(self, text: str):
        if not self.utterance_id:
            return {
                "ok": False,
                "error": "No active utterance.",
            }

        submitted_at = time.perf_counter()

        if self.first_chunk_submitted_at is None:
            self.first_chunk_submitted_at = submitted_at

        sequence = self.sequence
        self.sequence += 1
        self.chunk_submit_times[sequence] = submitted_at

        return queue_utterance_chunk(
            utterance_id=self.utterance_id,
            sequence=sequence,
            text=text,
        )

    def finish(self):
        if not self.utterance_id:
            return {
                "ok": False,
                "error": "No active utterance.",
            }

        return finish_utterance(
            utterance_id=self.utterance_id,
            wait=True,
            timeout=self.timeout,
        )
