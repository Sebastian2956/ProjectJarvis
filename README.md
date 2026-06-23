# ProjectJarvis

ProjectJarvis is a local-first personal assistant built around a small Python orchestration layer named `bigbrain`. It routes user requests to local LLMs, browser automation, a guarded PowerShell interpreter, persistent vector memory, speech-to-text, and text-to-speech with optional Applio/RVC voice conversion.

The project currently targets Windows with an NVIDIA GPU. The default configuration assumes the repository lives at `C:\AI\ProjectJarvis` and that Applio is installed at `C:\AI\Tools\ApplioV3.6.2`.

## Features

- Text chat loop through `bigbrain/main.py`
- Voice mode with wake words through `bigbrain/voice_main.py`
- Local model routing through Ollama
- Specialized routes for browser, coding, interpreter, and general reasoning tasks
- Browser automation through `browser-use` and Playwright
- Guarded local PowerShell execution with basic dangerous-command blocking
- Short-term in-process conversation history
- Long-term ChromaDB memory backed by sentence-transformer embeddings
- STT server using `faster-whisper`
- TTS server using Coqui XTTS v2
- Optional Applio/RVC conversion for a custom Jarvis-style voice
- Utility scripts for testing STT, TTS, browser automation, memory, and Applio training

## Repository Layout

```text
ProjectJarvis/
|-- bigbrain/                  # Main assistant code
|   |-- main.py                # Text REPL entry point
|   |-- voice_main.py          # Wake-word voice entry point
|   |-- jarvis_core.py         # Main request orchestration
|   |-- router.py              # LLM route selector
|   |-- models.py              # Ollama model calls
|   |-- tools.py               # Browser, coding, interpreter, reasoning tools
|   |-- memory_server.py       # Long-term memory HTTP server
|   |-- stt_server.py          # Speech-to-text HTTP server
|   |-- tts_server.py          # Text-to-speech HTTP server
|   `-- safety.py              # Local command safety checks
|-- requirements/              # Separate dependency sets by subsystem
|-- scripts/                   # Test, conversion, and training utilities
|-- voices/                    # Speaker/reference voice audio
|-- audio/                     # Generated audio and microphone captures
|-- memory/                    # Local ChromaDB data
|-- models/                    # Downloaded model caches
`-- applio_api.txt             # Notes/API output for Applio integration
```

The `audio/`, `memory/`, `models/`, virtual environment folders, logs, and model weight files are ignored by Git because they are generated or machine-specific.

## Requirements

### System Requirements

- Windows 10 or 11
- PowerShell
- Python 3.11 is recommended
- NVIDIA GPU with CUDA support for the default STT/TTS configuration
- Microphone and audio output device for voice mode
- Ollama installed and running
- Playwright browser dependencies for browser automation
- Applio running locally for custom RVC voice conversion

The code uses Windows-specific modules and paths, including `winsound`, PowerShell commands, and hard-coded `C:\AI\...` paths. Running on macOS or Linux will require code changes.

### Ollama Models

Install Ollama, then pull the models used by `bigbrain/models.py`:

```powershell
ollama pull deepseek-r1:14b
ollama pull deepseek-r1:7b
ollama pull qwen2.5-coder:14b
```

Make sure the Ollama service is running before starting Jarvis.

### Applio

The TTS voice conversion path expects Applio to be available at:

```text
http://127.0.0.1:6969/
```

The default RVC files are referenced from:

```text
C:\AI\Tools\ApplioV3.6.2\logs\JarvisV2\JarvisV2_200e_1200s.pth
C:\AI\Tools\ApplioV3.6.2\logs\JarvisV2\JarvisV2.index
```

If you train or use a different model, update `RVC_MODEL` and `RVC_INDEX` in `bigbrain/tts_server.py`.

## Clone and Setup

Clone the repository:

```powershell
git clone <your-fork-url> C:\AI\ProjectJarvis
cd C:\AI\ProjectJarvis
```

This project is organized around multiple virtual environments because the agent, memory, STT, and TTS stacks have different heavy dependencies.

### Agent Environment

Use this environment for the text assistant, routing, browser automation, and core orchestration.

```powershell
python -m venv agent_venv
.\agent_venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements\requirements_agent.txt
playwright install chromium
```

### Memory Environment

Use this environment for the ChromaDB long-term memory server.

```powershell
python -m venv memory_venv
.\memory_venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements\requirements_memory.txt
```

### Speech-to-Text Environment

Use this environment for Whisper transcription.

```powershell
python -m venv stt_venv
.\stt_venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements\requirements_stt.txt
```

The default STT server loads `large-v3` on CUDA with `float16`. If you do not have a compatible GPU, edit `bigbrain/stt_server.py` and change the `WhisperModel` settings to a CPU-compatible configuration.

### Text-to-Speech Environment

Use this environment for XTTS and Applio voice conversion.

```powershell
python -m venv tts_venv
.\tts_venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements\requirements_tts.txt
```

This dependency set includes GPU-heavy packages and Coqui TTS from GitHub. Installation can take time and may require a CUDA-compatible PyTorch build for your machine.

## Running ProjectJarvis

### Minimum Text Mode

Start the memory server in one PowerShell window:

```powershell
cd C:\AI\ProjectJarvis
.\memory_venv\Scripts\Activate.ps1
python bigbrain\memory_server.py
```

Start the text assistant in a second PowerShell window:

```powershell
cd C:\AI\ProjectJarvis
.\agent_venv\Scripts\Activate.ps1
python bigbrain\main.py
```

Type `exit`, `quit`, or `bye` to stop the text loop.

### Full Voice Mode

Voice mode needs these local services:

1. Ollama
2. Memory server on `127.0.0.1:7010`
3. STT server on `127.0.0.1:7020`
4. TTS server on `127.0.0.1:7030`
5. Applio on `127.0.0.1:6969` if using the default RVC conversion path

Start memory:

```powershell
cd C:\AI\ProjectJarvis
.\memory_venv\Scripts\Activate.ps1
python bigbrain\memory_server.py
```

Start STT:

```powershell
cd C:\AI\ProjectJarvis
.\stt_venv\Scripts\Activate.ps1
python bigbrain\stt_server.py
```

Start Applio separately and confirm it is listening at `http://127.0.0.1:6969/`.

Start TTS:

```powershell
cd C:\AI\ProjectJarvis
.\tts_venv\Scripts\Activate.ps1
python bigbrain\tts_server.py
```

Start voice mode:

```powershell
cd C:\AI\ProjectJarvis
.\agent_venv\Scripts\Activate.ps1
python bigbrain\voice_main.py
```

Wake words are:

- `jarvis`
- `hey jarvis`
- `ok jarvis`

Example:

```text
Jarvis, what is the weather in New York?
```

Shutdown commands include:

- `jarvis shutdown`
- `jarvis go offline`
- `jarvis stop listening`
- `jarvis power down`

## Local Services and Ports

| Service | File | Port |
| --- | --- | --- |
| Memory server | `bigbrain/memory_server.py` | `7010` |
| STT server | `bigbrain/stt_server.py` | `7020` |
| TTS server | `bigbrain/tts_server.py` | `7030` |
| Applio | External app | `6969` |

The clients are currently configured with fixed localhost URLs:

- `bigbrain/memory_client.py`
- `bigbrain/voice_client.py`

Change those files if you move services to different hosts or ports.

## How Routing Works

`bigbrain/jarvis_core.py` is the main entry point for user requests.

1. Explicit memory requests are detected by `bigbrain/memory_rules.py` and saved to ChromaDB.
2. Other requests are classified by `bigbrain/router.py`.
3. The selected route calls one of the tools in `bigbrain/tools.py`.
4. Responses and recent conversation history are stored in process memory by `bigbrain/context.py`.

Routes:

- `browser`: current information, websites, searches, URLs, prices, news, docs, releases
- `coding`: code writing, debugging, architecture, explanation, refactoring
- `interpreter`: local PowerShell commands and file/system inspection
- `reasoning`: general discussion, advice, planning, and conceptual answers

## Long-Term Memory

Long-term memory uses:

- ChromaDB persistent storage
- `sentence-transformers/all-MiniLM-L6-v2`
- Storage path: `C:\AI\ProjectJarvis\memory\chroma_db`

Memory is only saved when a user uses phrases such as:

- `remember that`
- `save this`
- `keep in mind`
- `for future reference`
- `from now on`

You can test memory manually:

```powershell
.\memory_venv\Scripts\Activate.ps1
python scripts\memory_test.py
```

## Voice Pipeline

Voice mode flows through these steps:

```text
microphone
  -> STT server / faster-whisper
  -> jarvis_core router and tools
  -> TTS server / XTTS v2
  -> Applio RVC conversion
  -> audio playback
```

Generated audio files are written under `audio/`:

- `audio\mic_input.wav`
- `audio\output.wav`
- `audio\jarvis_final.wav`

Reference voice samples are stored under `voices/`.

## Utility Scripts

| Script | Purpose |
| --- | --- |
| `scripts\memory_test.py` | Save and search a sample memory |
| `scripts\stt_test.py` | Test Whisper transcription |
| `scripts\tts_test.py` | Generate a sample XTTS output |
| `scripts\browser_use_test.py` | Test browser-use with Ollama |
| `scripts\playwright_test.py` | Test Playwright browser launch |
| `scripts\convert_jarvis.py` | Convert XTTS output through Applio |
| `scripts\prepare_jarvis_v2_audio.py` | Prepare voice audio for Applio training |
| `scripts\train_applio_jarvis.py` | Train the original Applio Jarvis model |
| `scripts\train_applio_jarvis_v2.py` | Train the JarvisV2 Applio model |

Some scripts contain hard-coded absolute paths. Review each script before running it on a new machine.

## Configuration Notes

Several values are currently hard-coded:

- Project root: `C:\AI\ProjectJarvis`
- Applio root: `C:\AI\Tools\ApplioV3.6.2`
- ChromaDB path: `C:\AI\ProjectJarvis\memory\chroma_db`
- Whisper cache path: `C:\AI\ProjectJarvis\models\whisper`
- RVC model and index paths in `bigbrain\tts_server.py`
- STT/TTS device settings use CUDA by default

If you fork the project and clone it somewhere else, update these files first:

- `bigbrain\memory_store.py`
- `bigbrain\stt_server.py`
- `bigbrain\stt_worker.py`
- `bigbrain\tts_server.py`
- `bigbrain\tts_worker.py`
- `scripts\*.py` files that reference `C:\AI\ProjectJarvis` or `C:\AI\Tools`

A future improvement would be to move these values into environment variables or a real config file.

## Security Notes

The interpreter route can execute local PowerShell commands. `bigbrain/safety.py` blocks many destructive commands and patterns, but this is not a complete sandbox.

Before exposing this assistant to other users or network access:

- Keep services bound to `127.0.0.1`
- Do not expose the interpreter route over the internet
- Review and tighten `bigbrain/safety.py`
- Avoid running the assistant as an administrator
- Treat browser automation as capable of interacting with live websites
- Do not commit secrets, model weights, generated memory, or private audio

## Troubleshooting

### Ollama model not found

Pull the missing model:

```powershell
ollama pull deepseek-r1:14b
ollama pull deepseek-r1:7b
ollama pull qwen2.5-coder:14b
```

### Memory search/save fails

Start the memory server before running `main.py` or `voice_main.py`:

```powershell
.\memory_venv\Scripts\Activate.ps1
python bigbrain\memory_server.py
```

### Browser automation fails

Install the Playwright browser:

```powershell
.\agent_venv\Scripts\Activate.ps1
playwright install chromium
```

### STT fails to load Whisper

The default server uses CUDA:

```python
WhisperModel("large-v3", device="cuda", compute_type="float16")
```

Use a smaller model or CPU settings if your machine does not support this.

### TTS fails when connecting to Applio

Confirm Applio is running at:

```text
http://127.0.0.1:6969/
```

Also confirm that `RVC_MODEL` and `RVC_INDEX` in `bigbrain\tts_server.py` point to files that exist on your machine.

### Audio device errors

Check that Windows has a default microphone and output device configured. The STT server uses `sounddevice`, and the TTS server uses `winsound` for playback.

## Development Notes

- Keep generated files out of Git. The `.gitignore` already excludes virtual environments, model caches, memory databases, audio outputs, logs, and common model weight formats.
- Prefer adding new assistant behavior through `bigbrain/tools.py` and route selection through `bigbrain/router.py`.
- Keep long-running model servers alive instead of repeatedly loading models for each request.
- Review hard-coded paths when moving the project to another machine.

## License

No license file is currently included. Add a license before publishing the repository publicly or accepting outside contributions.
