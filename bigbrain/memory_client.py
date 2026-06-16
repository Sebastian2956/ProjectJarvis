# bigbrain/memory_client.py

import json
import subprocess


MEMORY_PYTHON = r"C:\AI\ProjectJarvis\memory_venv\Scripts\python.exe"
MEMORY_WORKER = r"C:\AI\ProjectJarvis\bigbrain\memory_worker.py"


def extract_json_from_output(output: str):
    """
    The memory worker may print warnings/progress before the JSON.
    This finds the final JSON object in the output.
    """

    lines = output.strip().splitlines()

    for line in reversed(lines):
        line = line.strip()

        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)

    raise ValueError(f"No JSON object found in worker output:\n{output}")


def run_memory_worker(args):
    """
    Runs the memory worker inside memory_venv.
    This keeps chromadb and sentence-transformers out of agent_venv.
    """

    try:
        result = subprocess.check_output(
            [MEMORY_PYTHON, MEMORY_WORKER] + args,
            text=True,
            stderr=subprocess.STDOUT
        )

        return extract_json_from_output(result)

    except subprocess.CalledProcessError as e:
        return {
            "ok": False,
            "error": e.output
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }


def save_long_term_memory(text: str, memory_type: str = "general"):
    response = run_memory_worker([
        "save",
        text,
        memory_type
    ])

    if not response.get("ok"):
        return f"Long-term memory save failed: {response.get('error')}"

    return response.get("result", "Memory saved.")


def search_long_term_memory(query: str, n_results: int = 5):
    response = run_memory_worker([
        "search",
        query,
        str(n_results)
    ])

    if not response.get("ok"):
        return f"Long-term memory search failed: {response.get('error')}"

    return response.get("result", "No relevant long-term memories.")