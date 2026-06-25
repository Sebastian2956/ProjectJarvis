# bigbrain/voice_main.py

import logging
import time

logging.basicConfig(level=logging.WARNING)
logging.getLogger("browser_use").setLevel(logging.ERROR)
logging.getLogger("browser_use.agent").setLevel(logging.ERROR)
logging.getLogger("browser_use.browser").setLevel(logging.ERROR)
logging.getLogger("browser_use.service").setLevel(logging.ERROR)

from config import PROFILE_ENABLED
from jarvis_core import stream_voice_response
from voice_client import QueuedSpeechClient, listen_once_with_metadata, speak


WAKE_WORDS = [
    "jarvis",
    "hey jarvis",
    "ok jarvis",
]


EXIT_COMMANDS = [
    "shutdown",
    "shut down",
    "exit",
    "quit",
    "go offline",
    "stop listening",
    "turn off",
    "power down",
]


VOICE_MODE_INSTRUCTION = (
    "Voice mode instruction: respond briefly, naturally, and conversationally. "
    "Keep it under two short sentences unless I ask for detail. "
    "Do not use emojis, emoticons, pictograms, decorative symbols, or markdown."
)


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


def print_profile(timings: dict):
    if not PROFILE_ENABLED:
        return

    print("\n[LATENCY]")

    ordered_keys = [
        "stt_record_s",
        "stt_write_s",
        "stt_transcribe_s",
        "stt_total_s",
        "router_s",
        "context_prompt_s",
        "search_prompt_s",
        "search_rewrite_s",
        "browser_tool_s",
        "interpreter_prompt_s",
        "interpreter_rewrite_s",
        "interpreter_tool_s",
        "memory_save_s",
        "llm_first_token_s",
        "llm_first_sentence_s",
        "llm_total_s",
        "tts_first_audio_ready_s",
        "tts_total_s",
        "e2e_first_audible_s",
        "e2e_complete_spoken_s",
    ]

    for key in ordered_keys:
        value = timings.get(key)

        if value is None:
            continue

        print(f"{key:28} {value:8.3f}s")

    model = timings.get("llm_model")
    route = timings.get("route")

    if route:
        print(f"{'route':28} {route}")

    if model:
        print(f"{'llm_model':28} {model}")

    print()


def get_speech_end_time(listen_data: dict):
    client_timings = listen_data.get("client_timings", {})
    server_timings = listen_data.get("timings", {})

    request_started_at = client_timings.get("request_started_at", time.perf_counter())
    record_s = server_timings.get("record_s")

    if record_s is None:
        return client_timings.get("request_ended_at", time.perf_counter())

    return request_started_at + record_s


def build_latency_timings(listen_data: dict):
    server_timings = listen_data.get("timings", {})

    return {
        "stt_record_s": server_timings.get("record_s"),
        "stt_write_s": server_timings.get("write_s"),
        "stt_transcribe_s": server_timings.get("transcribe_s"),
        "stt_total_s": server_timings.get("total_s"),
    }


def main():
    print("Jarvis voice mode online.")
    print("Say 'Jarvis' followed by your command.")
    print("Say 'Jarvis shutdown' to exit.\n")

    speak("Voice systems online. Awaiting your command.")

    while True:
        print("\nListening...")
        listen_data = listen_once_with_metadata()
        heard = listen_data.get("text", "").strip()

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

        voice_prompt = f"{command}\n\n{VOICE_MODE_INSTRUCTION}"
        speech_end_at = get_speech_end_time(listen_data)
        timings = build_latency_timings(listen_data)

        tts_client = QueuedSpeechClient(play_audio=True)
        tts_start = tts_client.start()
        use_queued_tts = bool(tts_start.get("ok"))

        response_text = ""
        done_event = None
        first_sentence_submitted_at = None

        for event in stream_voice_response(voice_prompt):
            if event["type"] == "sentence":
                sentence = event["text"]
                response_text = f"{response_text} {sentence}".strip()
                print(f"[VOICE CHUNK] {sentence}")

                if use_queued_tts:
                    submitted_at = time.perf_counter()

                    if first_sentence_submitted_at is None:
                        first_sentence_submitted_at = submitted_at

                    tts_client.submit(sentence)

            if event["type"] == "done":
                done_event = event
                response_text = event.get("text") or response_text

        if done_event:
            timings.update(done_event.get("timings", {}))
            timings["route"] = done_event.get("route")

        if use_queued_tts:
            tts_finished_at = time.perf_counter()
            finish_data = tts_client.finish()
            tts_done_at = time.perf_counter()

            utterance = finish_data.get("utterance", {})
            chunks = utterance.get("chunks", [])

            timings["tts_total_s"] = utterance.get("total_s")

            if chunks:
                first_audio_ready_s = chunks[0].get("queue_to_playback_start_s")
                timings["tts_first_audio_ready_s"] = first_audio_ready_s

                if (
                    first_sentence_submitted_at is not None
                    and first_audio_ready_s is not None
                ):
                    timings["e2e_first_audible_s"] = (
                        first_sentence_submitted_at
                        - speech_end_at
                        + first_audio_ready_s
                    )

            timings["e2e_complete_spoken_s"] = tts_done_at - speech_end_at
            timings["tts_finish_wait_s"] = tts_done_at - tts_finished_at

        else:
            speak_start_at = time.perf_counter()
            speak(response_text)
            speak_done_at = time.perf_counter()

            timings["e2e_complete_spoken_s"] = speak_done_at - speech_end_at
            timings["tts_total_s"] = speak_done_at - speak_start_at

        print(f"\nJarvis: {response_text}\n")
        print_profile(timings)


if __name__ == "__main__":
    main()
