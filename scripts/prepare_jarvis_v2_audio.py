from pydub import AudioSegment
from pydub.effects import normalize
import os


INPUT_MP3 = r"C:\AI\ProjectJarvis\voices\JarvisV2\JarvisVoice8min.mp3"
OUTPUT_WAV = r"C:\AI\ProjectJarvis\voices\JarvisV2\JarvisVoice8min_clean.wav"

audio = AudioSegment.from_file(INPUT_MP3)

# Convert to mono
audio = audio.set_channels(1)

# Use 40k because your Applio training script uses 40000 sample rate
audio = audio.set_frame_rate(40000)

# Normalize volume
audio = normalize(audio)

# Export clean WAV
audio.export(OUTPUT_WAV, format="wav")

print(f"Saved clean WAV to:\n{OUTPUT_WAV}")