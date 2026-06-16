# bigbrain/tts_worker.py

import sys
import json
import shutil
import winsound

import torch

from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig
from TTS.tts.models.xtts import XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
from TTS.api import TTS

from gradio_client import Client, handle_file


torch.serialization.add_safe_globals([
    XttsConfig,
    XttsAudioConfig,
    BaseDatasetConfig,
    XttsArgs
])


PROJECT_ROOT = r"C:\AI\ProjectJarvis"

XTTS_OUTPUT = rf"{PROJECT_ROOT}\audio\output.wav"
JARVIS_FINAL = rf"{PROJECT_ROOT}\audio\jarvis_final.wav"

APPLIO_URL = "http://127.0.0.1:6969/"

RVC_MODEL = r"C:\AI\Tools\ApplioV3.6.2\logs\Jarvis\Jarvis_300e_1800s.pth"
RVC_INDEX = r"C:\AI\Tools\ApplioV3.6.2\logs\Jarvis\Jarvis.index"

SPEAKER_WAVS = [
    rf"{PROJECT_ROOT}\voices\Jarvis\Voicy_As You Wish .wav",
    rf"{PROJECT_ROOT}\voices\Jarvis\Voicy_At Your Service Sir.wav",
    rf"{PROJECT_ROOT}\voices\Jarvis\Voicy_Creating A Flight Plan.wav",
    rf"{PROJECT_ROOT}\voices\Jarvis\Voicy_Device That's Keeping You Alive.wav",
    rf"{PROJECT_ROOT}\voices\Jarvis\Voicy_He Is Insisting .wav",
    rf"{PROJECT_ROOT}\voices\Jarvis\Voicy_I Have Run Simulation .wav",
    rf"{PROJECT_ROOT}\voices\Jarvis\Voicy_Impossible To Synthesize.wav",
    rf"{PROJECT_ROOT}\voices\Jarvis\Voicy_May I Remind You.wav",
    rf"{PROJECT_ROOT}\voices\Jarvis\Voicy_Running Out Of Both Time And Action .wav",
    rf"{PROJECT_ROOT}\voices\Jarvis\Voicy_What Is It You Are Trying To Achieve Sir_.wav"
]


def generate_xtts(text: str):
    tts = TTS(
        model_name="tts_models/multilingual/multi-dataset/xtts_v2"
    ).to("cuda")

    tts.tts_to_file(
        text=text,
        speaker_wav=SPEAKER_WAVS,
        language="en",
        file_path=XTTS_OUTPUT
    )


def convert_with_applio():
    client = Client(APPLIO_URL)

    select_audio, output_path = client.predict(
        handle_file(XTTS_OUTPUT),
        api_name="/save_to_wav2"
    )

    result = client.predict(
        True,
        0,
        0.75,
        1,
        0.5,
        "rmvpe",
        select_audio,
        output_path,
        RVC_MODEL,
        RVC_INDEX,
        False, False, 1, False, 155.0, False, 0.5,
        "WAV",
        "contentvec",
        None,
        False, 1.0, 1.0,
        False, False, False, False, False, False, False, False, False, False, False,
        0.5, 0.5, 0.33, 0.4, 1.0, 0.0, 0, -6, 0.05, 0, 25,
        1.0, 0.25, 7, 0.0, 0.5, 8, -6, 0, 1, 1.0, 100, 0.5, 0.0, 0.5,
        0,
        api_name="/enforce_terms"
    )

    temp_output = result[1]

    shutil.copy(temp_output, JARVIS_FINAL)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "ok": False,
            "error": "No text provided."
        }))
        return

    text = sys.argv[1]

    try:
        generate_xtts(text)
        convert_with_applio()

        winsound.PlaySound(JARVIS_FINAL, winsound.SND_FILENAME)

        print(json.dumps({
            "ok": True,
            "audio_path": JARVIS_FINAL
        }))

    except Exception as e:
        print(json.dumps({
            "ok": False,
            "error": str(e)
        }))


if __name__ == "__main__":
    main()