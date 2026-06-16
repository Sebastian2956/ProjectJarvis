# bigbrain/memory_worker.py

import sys
import json

from memory_store import save_memory, search_memory, format_memories


def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "ok": False,
            "error": "Usage: memory_worker.py <action> <text>"
        }))
        return

    action = sys.argv[1]
    text = sys.argv[2]

    try:
        if action == "save":
            memory_type = sys.argv[3] if len(sys.argv) >= 4 else "general"

            result = save_memory(text, memory_type=memory_type)

            print(json.dumps({
                "ok": True,
                "action": "save",
                "result": result
            }))

        elif action == "search":
            n_results = int(sys.argv[3]) if len(sys.argv) >= 4 else 5

            memories = search_memory(text, n_results=n_results)
            formatted = format_memories(memories)

            print(json.dumps({
                "ok": True,
                "action": "search",
                "result": formatted,
                "raw": memories
            }))

        else:
            print(json.dumps({
                "ok": False,
                "error": f"Unknown action: {action}"
            }))

    except Exception as e:
        print(json.dumps({
            "ok": False,
            "error": str(e)
        }))


if __name__ == "__main__":
    main()