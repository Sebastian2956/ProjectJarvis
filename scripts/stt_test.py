import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel

model = WhisperModel(
    "large-v3",
    device="cuda",
    compute_type="float16",
    download_root="C:/AI/ProjectJarvis/models/whisper"
)

duration = 30
samplerate = 16000

print("Recording...")

audio = sd.rec(
    int(duration * samplerate),
    samplerate=samplerate,
    channels=1,
    dtype="float32"
)

sd.wait()

sf.write("test.wav", audio, samplerate)

print("Transcribing...")

segments, info = model.transcribe("./voices/SebVoice/test.wav")

print("\nDetected language:", info.language)

for segment in segments:
    print(segment.text)