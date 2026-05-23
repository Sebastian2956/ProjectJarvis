import torch

from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig
from TTS.tts.models.xtts import XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig

torch.serialization.add_safe_globals([
    XttsConfig,
    XttsAudioConfig,
    BaseDatasetConfig,
    XttsArgs
])

from TTS.api import TTS

tts = TTS(
    model_name="tts_models/multilingual/multi-dataset/xtts_v2"
).to("cuda")

tts.tts_to_file(
    text="Hello Sebastian. Systems are now fully operational. My name is Jarvis. How can I assist you today?",
    speaker_wav= [
        "voices\Jarvis\Voicy_As You Wish .wav",
        "voices\Jarvis\Voicy_At Your Service Sir.wav",
        "voices\Jarvis\Voicy_Creating A Flight Plan.wav",
        "voices\Jarvis\Voicy_Device That's Keeping You Alive.wav",
        "voices\Jarvis\Voicy_He Is Insisting .wav",
        "voices\Jarvis\Voicy_I Have Run Simulation .wav",
        "voices\Jarvis\Voicy_Impossible To Synthesize.wav",
        "voices\Jarvis\Voicy_May I Remind You.wav",
        "voices\Jarvis\Voicy_Running Out Of Both Time And Action .wav",
        "voices\Jarvis\Voicy_What Is It You Are Trying To Achieve Sir_.wav"
    ],
    language="en",
    file_path="audio/output.wav"
)
