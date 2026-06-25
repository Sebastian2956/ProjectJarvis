# bigbrain/stt_server.py

import json
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel


HOST = "127.0.0.1"
PORT = 7020

PROJECT_ROOT = r"C:\AI\ProjectJarvis"
AUDIO_PATH = rf"{PROJECT_ROOT}\audio\mic_input.wav"
WHISPER_MODEL_PATH = rf"{PROJECT_ROOT}\models\whisper"

SAMPLE_RATE = 16000
DEFAULT_DURATION = 8


print("Loading Whisper model once...")
model = WhisperModel(
    "large-v3",
    device="cuda",
    compute_type="float16",
    download_root=WHISPER_MODEL_PATH
)
print("Whisper model loaded.")


class STTHandler(BaseHTTPRequestHandler):

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
            request_start = time.perf_counter()

            if self.path != "/listen":
                self._send_json({
                    "ok": False,
                    "error": f"Unknown path: {self.path}"
                }, status=404)
                return

            data = self._read_json()
            duration = float(data.get("duration", DEFAULT_DURATION))

            print(f"Recording for {duration} seconds...")

            record_start = time.perf_counter()
            audio = sd.rec(
                int(duration * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="float32"
            )

            sd.wait()
            record_end = time.perf_counter()

            write_start = time.perf_counter()
            sf.write(AUDIO_PATH, audio, SAMPLE_RATE)
            write_end = time.perf_counter()

            print("Transcribing...")

            transcribe_start = time.perf_counter()
            segments, info = model.transcribe(
                AUDIO_PATH,
                vad_filter=True
            )

            text_parts = []

            for segment in segments:
                text_parts.append(segment.text.strip())

            text = " ".join(text_parts).strip()
            transcribe_end = time.perf_counter()

            print(f"Heard: {text}")

            self._send_json({
                "ok": True,
                "text": text,
                "language": info.language,
                "timings": {
                    "record_s": record_end - record_start,
                    "write_s": write_end - write_start,
                    "transcribe_s": transcribe_end - transcribe_start,
                    "total_s": time.perf_counter() - request_start
                }
            })

        except Exception as e:
            self._send_json({
                "ok": False,
                "error": str(e)
            }, status=500)

    def log_message(self, format, *args):
        return


def main():
    print(f"STT server online at http://{HOST}:{PORT}")
    server = ThreadingHTTPServer((HOST, PORT), STTHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
