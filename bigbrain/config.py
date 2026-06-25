import os


STT_SERVER_URL = os.getenv("JARVIS_STT_URL", "http://127.0.0.1:7020")
TTS_SERVER_URL = os.getenv("JARVIS_TTS_URL", "http://127.0.0.1:7030")

PROFILE_ENABLED = os.getenv("JARVIS_PROFILE", "0").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

PLAYBACK_LEAD_IN_MS = int(os.getenv("JARVIS_PLAYBACK_LEAD_IN_MS", "180"))

OLLAMA_NUM_CTX = int(os.getenv("JARVIS_OLLAMA_NUM_CTX", "4096"))
OLLAMA_KEEP_ALIVE = os.getenv("JARVIS_OLLAMA_KEEP_ALIVE", "10m")

OLLAMA_MODEL_GENERAL = os.getenv("JARVIS_MODEL_GENERAL", "deepseek-r1:7b")
OLLAMA_MODEL_ROUTER = os.getenv("JARVIS_MODEL_ROUTER", "deepseek-r1:7b")
OLLAMA_MODEL_CODING = os.getenv("JARVIS_MODEL_CODING", "qwen2.5-coder:14b")
OLLAMA_MODEL_SEARCH_REWRITE = os.getenv("JARVIS_MODEL_SEARCH_REWRITE", "deepseek-r1:7b")
OLLAMA_MODEL_INTERPRETER_REWRITE = os.getenv(
    "JARVIS_MODEL_INTERPRETER_REWRITE",
    "qwen2.5-coder:14b",
)
OLLAMA_MODEL_BROWSER = os.getenv("JARVIS_MODEL_BROWSER", "qwen2.5-coder:14b")
