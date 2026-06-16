# bigbrain/stt_worker.py

import json
import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel


AUDIO_PATH = r"C:\AI\ProjectJarvis\audio\mic_input.wav"
WHISPER_MODEL_PATH = r"C:\AI\ProjectJarvis\models\whisper"


def main():
    try:
        model = WhisperModel(
            "large-v3",
            device="cuda",
            compute_type="float16",
            download_root=WHISPER_MODEL_PATH
        )

        duration = 8
        samplerate = 16000

        print(json.dumps({
            "status": "recording",
            "duration": duration
        }), flush=True)

        audio = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype="float32"
        )

        sd.wait()

        sf.write(AUDIO_PATH, audio, samplerate)

        segments, info = model.transcribe(AUDIO_PATH)

        text_parts = []

        for segment in segments:
            text_parts.append(segment.text.strip())

        text = " ".join(text_parts).strip()

        print(json.dumps({
            "ok": True,
            "text": text,
            "language": info.language
        }))

    except Exception as e:
        print(json.dumps({
            "ok": False,
            "error": str(e)
        }))


if __name__ == "__main__":
    main()