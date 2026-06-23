# bigbrain/tts_server.py

import json
import shutil
import winsound
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

import torch

from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig
from TTS.tts.models.xtts import XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
from TTS.api import TTS

from gradio_client import Client, handle_file


HOST = "127.0.0.1"
PORT = 7030

PROJECT_ROOT = r"C:\AI\ProjectJarvis"

XTTS_OUTPUT = rf"{PROJECT_ROOT}\audio\output.wav"
JARVIS_FINAL = rf"{PROJECT_ROOT}\audio\jarvis_final.wav"

APPLIO_URL = "http://127.0.0.1:6969/"

RVC_MODEL = r"C:\AI\Tools\ApplioV3.6.2\logs\JarvisV2\JarvisV2_200e_1200s.pth"
RVC_INDEX = r"C:\AI\Tools\ApplioV3.6.2\logs\JarvisV2\JarvisV2.index"

SPEAKER_WAVS = [
    rf"{PROJECT_ROOT}\voices\JarvisV2\JarvisVoice_clean.wav",
    rf"{PROJECT_ROOT}\voices\JarvisBackUp\Voicy_As You Wish .wav",
    rf"{PROJECT_ROOT}\voices\JarvisBackUp\Voicy_At Your Service Sir.wav",
    rf"{PROJECT_ROOT}\voices\JarvisBackUp\Voicy_Creating A Flight Plan.wav",
    rf"{PROJECT_ROOT}\voices\JarvisBackUp\Voicy_Device That's Keeping You Alive.wav",
    rf"{PROJECT_ROOT}\voices\JarvisBackUp\Voicy_He Is Insisting .wav",
    rf"{PROJECT_ROOT}\voices\JarvisBackUp\Voicy_I Have Run Simulation .wav",
    rf"{PROJECT_ROOT}\voices\JarvisBackUp\Voicy_Impossible To Synthesize.wav",
    rf"{PROJECT_ROOT}\voices\JarvisBackUp\Voicy_May I Remind You.wav",
    rf"{PROJECT_ROOT}\voices\JarvisBackUp\Voicy_Running Out Of Both Time And Action .wav",
    rf"{PROJECT_ROOT}\voices\JarvisBackUp\Voicy_What Is It You Are Trying To Achieve Sir_.wav"
]


torch.serialization.add_safe_globals([
    XttsConfig,
    XttsAudioConfig,
    BaseDatasetConfig,
    XttsArgs
])


print("Loading XTTS model once...")
tts = TTS(
    model_name="tts_models/multilingual/multi-dataset/xtts_v2"
).to("cuda")
print("XTTS model loaded.")

print("Connecting to Applio...")
applio_client = Client(APPLIO_URL)
print("Applio connected.")


def generate_xtts(text: str):
    tts.tts_to_file(
        text=text,
        speaker_wav=SPEAKER_WAVS,
        language="en",
        file_path=XTTS_OUTPUT
    )


def convert_with_applio():
    select_audio, output_path = applio_client.predict(
        handle_file(XTTS_OUTPUT),
        api_name="/save_to_wav2"
    )

    result = applio_client.predict(
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


class TTSHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status=200):
        response = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def _read_json(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        if not body:
            return {}

        return json.loads(body)

    def do_POST(self):
        try:
            if self.path != "/speak":
                self._send_json({
                    "ok": False,
                    "error": f"Unknown path: {self.path}"
                }, status=404)
                return

            data = self._read_json()
            text = data.get("text", "").strip()
            play_audio = bool(data.get("play_audio", True))

            if not text:
                self._send_json({
                    "ok": False,
                    "error": "No text provided."
                }, status=400)
                return

            print(f"Speaking: {text}")

            generate_xtts(text)
            convert_with_applio()

            if play_audio:
                winsound.PlaySound(JARVIS_FINAL, winsound.SND_FILENAME)

            self._send_json({
                "ok": True,
                "audio_path": JARVIS_FINAL
            })

        except Exception as e:
            self._send_json({
                "ok": False,
                "error": str(e)
            }, status=500)

    def log_message(self, format, *args):
        return


def main():
    print(f"TTS server online at http://{HOST}:{PORT}")
    server = ThreadingHTTPServer((HOST, PORT), TTSHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()