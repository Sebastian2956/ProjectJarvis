# bigbrain/tts_server.py

import json
import os
import queue
import shutil
import threading
import time
import uuid
import wave
import winsound
from dataclasses import dataclass, field
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

import torch

from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig
from TTS.tts.models.xtts import XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
from TTS.api import TTS

from gradio_client import Client, handle_file

from config import PLAYBACK_LEAD_IN_MS


HOST = "127.0.0.1"
PORT = 7030

PROJECT_ROOT = r"C:\AI\ProjectJarvis"

XTTS_OUTPUT = rf"{PROJECT_ROOT}\audio\output.wav"
JARVIS_FINAL = rf"{PROJECT_ROOT}\audio\jarvis_final.wav"
STREAM_DIR = rf"{PROJECT_ROOT}\audio\stream"

APPLIO_URL = "http://127.0.0.1:6969/"

RVC_MODEL = r"C:\AI\Tools\ApplioV3.6.2\logs\JarvisV2\JarvisV2_200e_28200s.pth"
RVC_INDEX = r"C:\AI\Tools\ApplioV3.6.2\logs\JarvisV2\JarvisV2.index"

SPEAKER_WAVS = [
    rf"{PROJECT_ROOT}\voices\JarvisV2\JarvisVoice_clean.wav",
]


torch.serialization.add_safe_globals([
    XttsConfig,
    XttsAudioConfig,
    BaseDatasetConfig,
    XttsArgs,
])

os.makedirs(STREAM_DIR, exist_ok=True)

XTTS_LOCK = threading.Lock()
APPLIO_LOCK = threading.Lock()
STATE_LOCK = threading.Lock()
PLAYBACK_PENDING_LOCK = threading.Lock()

xtts_queue = queue.Queue()
rvc_queue = queue.Queue()
playback_queue = queue.Queue()

utterances = {}
playback_pending = {}
workers_started = False


print("Loading XTTS model once...")
tts = TTS(
    model_name="tts_models/multilingual/multi-dataset/xtts_v2"
).to("cuda")
print("XTTS model loaded.")

print("Connecting to Applio...")
applio_client = Client(APPLIO_URL)
print("Applio connected.")


def elapsed(start, end):
    if start is None or end is None:
        return None

    return end - start


@dataclass
class ChunkState:
    utterance_id: str
    sequence: int
    text: str
    queued_at: float = field(default_factory=time.perf_counter)
    status: str = "queued"
    error: str = ""
    xtts_path: str = ""
    final_path: str = ""
    xtts_start_at: float | None = None
    xtts_end_at: float | None = None
    rvc_start_at: float | None = None
    rvc_end_at: float | None = None
    playback_wait_start_at: float | None = None
    playback_start_at: float | None = None
    playback_end_at: float | None = None

    def to_dict(self):
        return {
            "sequence": self.sequence,
            "text": self.text,
            "status": self.status,
            "error": self.error,
            "xtts_path": self.xtts_path,
            "audio_path": self.final_path,
            "xtts_s": elapsed(self.xtts_start_at, self.xtts_end_at),
            "rvc_s": elapsed(self.rvc_start_at, self.rvc_end_at),
            "playback_wait_s": elapsed(
                self.playback_wait_start_at,
                self.playback_start_at,
            ),
            "playback_s": elapsed(self.playback_start_at, self.playback_end_at),
            "queue_to_playback_start_s": elapsed(
                self.queued_at,
                self.playback_start_at,
            ),
            "queue_to_done_s": elapsed(self.queued_at, self.playback_end_at),
        }


@dataclass
class UtteranceState:
    utterance_id: str
    play_audio: bool
    created_at: float = field(default_factory=time.perf_counter)
    finished_at: float | None = None
    completed_at: float | None = None
    next_play_sequence: int = 0
    chunks: dict = field(default_factory=dict)
    complete_event: threading.Event = field(default_factory=threading.Event, repr=False)

    def to_dict(self):
        chunks = [
            chunk.to_dict()
            for _, chunk in sorted(self.chunks.items(), key=lambda item: item[0])
        ]

        first_chunk = chunks[0] if chunks else None

        return {
            "utterance_id": self.utterance_id,
            "play_audio": self.play_audio,
            "completed": self.complete_event.is_set(),
            "chunk_count": len(chunks),
            "first_audio_ready_s": None
            if not first_chunk
            else first_chunk.get("queue_to_playback_start_s"),
            "total_s": elapsed(self.created_at, self.completed_at),
            "chunks": chunks,
        }


def generate_xtts(text: str, output_path: str = XTTS_OUTPUT):
    with XTTS_LOCK:
        tts.tts_to_file(
            text=text,
            speaker_wav=SPEAKER_WAVS,
            language="en",
            file_path=output_path,
        )


def add_leading_silence(wav_path: str, silence_ms: int = PLAYBACK_LEAD_IN_MS):
    if silence_ms <= 0:
        return

    temp_path = f"{wav_path}.padded.wav"

    with wave.open(wav_path, "rb") as source:
        params = source.getparams()
        frames = source.readframes(source.getnframes())

    frame_count = int(params.framerate * silence_ms / 1000)
    bytes_per_frame = params.nchannels * params.sampwidth

    if params.sampwidth == 1:
        silence_frame = b"\x80" * bytes_per_frame
    else:
        silence_frame = b"\x00" * bytes_per_frame

    with wave.open(temp_path, "wb") as target:
        target.setparams(params)
        target.writeframes(silence_frame * frame_count)
        target.writeframes(frames)

    os.replace(temp_path, wav_path)


def convert_with_applio(
    input_path: str = XTTS_OUTPUT,
    final_path: str = JARVIS_FINAL,
):
    with APPLIO_LOCK:
        select_audio, output_path = applio_client.predict(
            handle_file(input_path),
            api_name="/save_to_wav2",
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
            api_name="/enforce_terms",
        )

        temp_output = result[1]
        shutil.copy(temp_output, final_path)
        add_leading_silence(final_path)


def create_utterance(play_audio: bool):
    utterance_id = str(uuid.uuid4())
    state = UtteranceState(
        utterance_id=utterance_id,
        play_audio=play_audio,
    )

    with STATE_LOCK:
        utterances[utterance_id] = state

    return state


def get_utterance(utterance_id: str):
    with STATE_LOCK:
        return utterances.get(utterance_id)


def stream_paths(utterance_id: str, sequence: int):
    safe_id = utterance_id.replace("-", "")
    base = f"{safe_id}_{sequence:04d}"

    return (
        os.path.join(STREAM_DIR, f"{base}_xtts.wav"),
        os.path.join(STREAM_DIR, f"{base}_final.wav"),
    )


def queue_chunk(utterance_id: str, sequence: int, text: str):
    state = get_utterance(utterance_id)

    if state is None:
        raise ValueError(f"Unknown utterance_id: {utterance_id}")

    xtts_path, final_path = stream_paths(utterance_id, sequence)
    chunk = ChunkState(
        utterance_id=utterance_id,
        sequence=sequence,
        text=text,
        xtts_path=xtts_path,
        final_path=final_path,
    )

    with STATE_LOCK:
        if sequence in state.chunks:
            raise ValueError(f"Duplicate sequence for utterance: {sequence}")

        state.chunks[sequence] = chunk

    xtts_queue.put(chunk)
    return chunk


def finish_utterance(utterance_id: str):
    state = get_utterance(utterance_id)

    if state is None:
        raise ValueError(f"Unknown utterance_id: {utterance_id}")

    with STATE_LOCK:
        state.finished_at = time.perf_counter()

    maybe_mark_utterance_complete(utterance_id)
    return state


def mark_chunk_error(chunk: ChunkState, error: Exception):
    chunk.error = str(error)
    chunk.status = "error"
    chunk.playback_end_at = time.perf_counter()

    advance_failed_chunks(chunk.utterance_id)
    maybe_mark_utterance_complete(chunk.utterance_id)
    drain_playback(chunk.utterance_id)


def advance_failed_chunks(utterance_id: str):
    with STATE_LOCK:
        state = utterances.get(utterance_id)

        if state is None:
            return

        while True:
            chunk = state.chunks.get(state.next_play_sequence)

            if chunk is None or chunk.status != "error":
                return

            state.next_play_sequence += 1


def maybe_mark_utterance_complete(utterance_id: str):
    with STATE_LOCK:
        state = utterances.get(utterance_id)

        if state is None or state.finished_at is None:
            return

        if not state.chunks:
            state.completed_at = time.perf_counter()
            state.complete_event.set()
            return

        done = all(
            chunk.status in {"played", "error"}
            for chunk in state.chunks.values()
        )

        if done and not state.complete_event.is_set():
            state.completed_at = time.perf_counter()
            state.complete_event.set()


def xtts_worker():
    while True:
        chunk = xtts_queue.get()

        try:
            chunk.status = "xtts"
            chunk.xtts_start_at = time.perf_counter()
            generate_xtts(chunk.text, chunk.xtts_path)
            chunk.xtts_end_at = time.perf_counter()
            chunk.status = "xtts_done"
            rvc_queue.put(chunk)

        except Exception as e:
            mark_chunk_error(chunk, e)

        finally:
            xtts_queue.task_done()


def rvc_worker():
    while True:
        chunk = rvc_queue.get()

        try:
            chunk.status = "rvc"
            chunk.rvc_start_at = time.perf_counter()
            convert_with_applio(chunk.xtts_path, chunk.final_path)
            chunk.rvc_end_at = time.perf_counter()
            chunk.status = "rvc_done"
            chunk.playback_wait_start_at = time.perf_counter()
            playback_queue.put(chunk)

        except Exception as e:
            mark_chunk_error(chunk, e)

        finally:
            rvc_queue.task_done()


def playback_worker():
    while True:
        chunk = playback_queue.get()

        try:
            with PLAYBACK_PENDING_LOCK:
                pending = playback_pending.setdefault(chunk.utterance_id, {})
                pending[chunk.sequence] = chunk

            drain_playback(chunk.utterance_id)

        finally:
            playback_queue.task_done()


def drain_playback(utterance_id: str):
    while True:
        advance_failed_chunks(utterance_id)
        state = get_utterance(utterance_id)

        if state is None:
            return

        with PLAYBACK_PENDING_LOCK:
            pending = playback_pending.setdefault(utterance_id, {})
            chunk = pending.get(state.next_play_sequence)

            if chunk is None:
                return

            del pending[state.next_play_sequence]

        chunk.status = "playback"
        chunk.playback_start_at = time.perf_counter()

        try:
            if state.play_audio:
                winsound.PlaySound(chunk.final_path, winsound.SND_FILENAME)

        except Exception as e:
            mark_chunk_error(chunk, e)
            continue

        chunk.playback_end_at = time.perf_counter()
        chunk.status = "played"

        with STATE_LOCK:
            state.next_play_sequence += 1

        maybe_mark_utterance_complete(utterance_id)


def start_workers():
    global workers_started

    if workers_started:
        return

    workers_started = True

    for name, target in [
        ("Jarvis XTTS worker", xtts_worker),
        ("Jarvis RVC worker", rvc_worker),
        ("Jarvis playback worker", playback_worker),
    ]:
        thread = threading.Thread(target=target, name=name, daemon=True)
        thread.start()


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

    def _handle_speak(self, data):
        text = data.get("text", "").strip()
        play_audio = bool(data.get("play_audio", True))

        if not text:
            self._send_json({
                "ok": False,
                "error": "No text provided.",
            }, status=400)
            return

        print(f"Speaking: {text}")

        overall_start = time.perf_counter()

        xtts_start = time.perf_counter()
        generate_xtts(text)
        xtts_end = time.perf_counter()

        rvc_start = time.perf_counter()
        convert_with_applio()
        rvc_end = time.perf_counter()

        playback_start = None
        playback_end = None

        if play_audio:
            playback_start = time.perf_counter()
            winsound.PlaySound(JARVIS_FINAL, winsound.SND_FILENAME)
            playback_end = time.perf_counter()

        overall_end = time.perf_counter()

        self._send_json({
            "ok": True,
            "audio_path": JARVIS_FINAL,
            "timings": {
                "xtts_s": xtts_end - xtts_start,
                "rvc_s": rvc_end - rvc_start,
                "playback_startup_s": elapsed(rvc_end, playback_start),
                "playback_s": elapsed(playback_start, playback_end),
                "total_s": overall_end - overall_start,
            },
        })

    def _handle_utterance_start(self, data):
        play_audio = bool(data.get("play_audio", True))
        state = create_utterance(play_audio=play_audio)

        self._send_json({
            "ok": True,
            "utterance_id": state.utterance_id,
        })

    def _handle_utterance_chunk(self, data):
        utterance_id = data.get("utterance_id", "").strip()
        text = data.get("text", "").strip()
        sequence = int(data.get("sequence", 0))

        if not utterance_id:
            self._send_json({
                "ok": False,
                "error": "No utterance_id provided.",
            }, status=400)
            return

        if not text:
            self._send_json({
                "ok": False,
                "error": "No text provided.",
            }, status=400)
            return

        chunk = queue_chunk(utterance_id, sequence, text)

        self._send_json({
            "ok": True,
            "utterance_id": utterance_id,
            "sequence": sequence,
            "status": chunk.status,
        })

    def _handle_utterance_finish(self, data):
        utterance_id = data.get("utterance_id", "").strip()
        wait = bool(data.get("wait", True))
        timeout = float(data.get("timeout", 300))

        if not utterance_id:
            self._send_json({
                "ok": False,
                "error": "No utterance_id provided.",
            }, status=400)
            return

        state = finish_utterance(utterance_id)

        if wait and not state.complete_event.wait(timeout):
            self._send_json({
                "ok": False,
                "error": f"Timed out waiting for utterance {utterance_id}.",
                "utterance": state.to_dict(),
            }, status=504)
            return

        self._send_json({
            "ok": True,
            "utterance": state.to_dict(),
        })

    def do_POST(self):
        try:
            data = self._read_json()

            if self.path == "/speak":
                self._handle_speak(data)
                return

            if self.path == "/utterance/start":
                self._handle_utterance_start(data)
                return

            if self.path == "/utterance/chunk":
                self._handle_utterance_chunk(data)
                return

            if self.path == "/utterance/finish":
                self._handle_utterance_finish(data)
                return

            self._send_json({
                "ok": False,
                "error": f"Unknown path: {self.path}",
            }, status=404)

        except Exception as e:
            self._send_json({
                "ok": False,
                "error": str(e),
            }, status=500)

    def log_message(self, format, *args):
        return


def main():
    start_workers()

    print(f"TTS server online at http://{HOST}:{PORT}")
    server = ThreadingHTTPServer((HOST, PORT), TTSHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
