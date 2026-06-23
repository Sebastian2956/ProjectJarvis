# bigbrain/voice_main.py

import logging

logging.basicConfig(level=logging.WARNING)
logging.getLogger("browser_use").setLevel(logging.ERROR)
logging.getLogger("browser_use.agent").setLevel(logging.ERROR)
logging.getLogger("browser_use.browser").setLevel(logging.ERROR)
logging.getLogger("browser_use.service").setLevel(logging.ERROR)

from jarvis_core import handle_user_input
from voice_client import listen_once, speak


WAKE_WORDS = [
    "jarvis",
    "hey jarvis",
    "ok jarvis"
]


EXIT_COMMANDS = [
    "shutdown",
    "shut down",
    "exit",
    "quit",
    "go offline",
    "stop listening",
    "turn off",
    "power down"
]


def normalize_text(text: str):
    """
    Normalizes speech text for command detection.
    """

    return (
        text.lower()
        .replace(",", "")
        .replace(".", "")
        .replace("!", "")
        .replace("?", "")
        .strip()
    )


def has_wake_word(text: str):
    lowered = normalize_text(text)
    return any(wake_word in lowered for wake_word in WAKE_WORDS)


def remove_wake_word(text: str):
    cleaned = normalize_text(text)

    for wake_word in WAKE_WORDS:
        cleaned = cleaned.replace(wake_word, "")

    return cleaned.strip()


def is_exit_command(command: str):
    cleaned = normalize_text(command)
    return cleaned in EXIT_COMMANDS


def main():
    print("Jarvis voice mode online.")
    print("Say 'Jarvis' followed by your command.")
    print("Say 'Jarvis shutdown' to exit.\n")

    speak("Voice systems online. Awaiting your command.")

    while True:
        print("\nListening...")
        heard = listen_once()

        if not heard:
            print("Heard nothing.")
            continue

        print(f"You said: {heard}")

        if not has_wake_word(heard):
            print("Wake word not detected.")
            continue

        command = remove_wake_word(heard)

        if not command:
            print("Wake word detected, but no command heard.")
            continue

        print(f"Command: {command}")

        if is_exit_command(command):
            speak("Shutting down.")
            print("Jarvis shutting down.")
            break

        response = handle_user_input(
            command + "\n\nVoice mode instruction: respond briefly, naturally, and conversationally. Keep it under two short sentences unless I ask for detail."
        )

        print(f"\nJarvis: {response}\n")

        speak(response)


if __name__ == "__main__":
    main()