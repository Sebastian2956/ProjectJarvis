import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bigbrain.memory_store import save_memory, search_memory, format_memories


print("Saving memory...")
print(save_memory("Sebastian's Project Jarvis uses bigbrain as the main orchestrator folder.", "project"))

print("\nSearching memory...")
results = search_memory("What is the orchestrator folder called?")

print("\nResults:")
print(format_memories(results))