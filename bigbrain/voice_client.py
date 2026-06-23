# bigbrain/voice_client.py

import requests


STT_SERVER_URL = "http://127.0.0.1:7020"
TTS_SERVER_URL = "http://127.0.0.1:7030"

def clean_text_for_speech(text: str):
    cleaned = text

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

    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")

    return cleaned.strip()

def listen_once(duration: float = 8):
    try:
        response = requests.post(
            f"{STT_SERVER_URL}/listen",
            json={
                "duration": duration
            },
            timeout=duration + 60
        )

        data = response.json()

        if not data.get("ok"):
            print("[STT ERROR]", data.get("error"))
            return ""

        return data.get("text", "").strip()

    except Exception as e:
        print("[STT ERROR]", e)
        return ""


def speak(text: str):
    try:
        text = clean_text_for_speech(text)

        response = requests.post(
            f"{TTS_SERVER_URL}/speak",
            json={
                "text": text,
                "play_audio": True
            },
            timeout=300
        )

        data = response.json()

        if not data.get("ok"):
            print("[TTS ERROR]", data.get("error"))

        return data

    except Exception as e:
        print("[TTS ERROR]", e)
        return {
            "ok": False,
            "error": str(e)
        }