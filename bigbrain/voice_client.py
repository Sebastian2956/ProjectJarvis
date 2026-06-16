# bigbrain/voice_client.py

import json
import subprocess


STT_PYTHON = r"C:\AI\ProjectJarvis\stt_venv\Scripts\python.exe"
TTS_PYTHON = r"C:\AI\ProjectJarvis\tts_venv\Scripts\python.exe"

STT_WORKER = r"C:\AI\ProjectJarvis\bigbrain\stt_worker.py"
TTS_WORKER = r"C:\AI\ProjectJarvis\bigbrain\tts_worker.py"


def extract_json_from_output(output: str):
    lines = output.strip().splitlines()

    for line in reversed(lines):
        line = line.strip()

        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)

    raise ValueError(f"No JSON object found in worker output:\n{output}")


def listen_once():
    result = subprocess.check_output(
        [STT_PYTHON, STT_WORKER],
        text=True,
        stderr=subprocess.STDOUT
    )

    response = extract_json_from_output(result)

    if not response.get("ok"):
        return ""

    return response.get("text", "").strip()


def speak(text: str):
    result = subprocess.check_output(
        [TTS_PYTHON, TTS_WORKER, text],
        text=True,
        stderr=subprocess.STDOUT
    )

    response = extract_json_from_output(result)

    if not response.get("ok"):
        print("[TTS ERROR]", response.get("error"))

    return response