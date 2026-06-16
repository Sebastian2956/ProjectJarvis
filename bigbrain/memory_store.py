import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime
import uuid


CHROMA_PATH = r"C:\AI\ProjectJarvis\memory\chroma_db"
COLLECTION_NAME = "jarvis_long_term_memory"

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


def create_embedding(text: str):
    return embedding_model.encode(text).tolist()


def save_memory(text: str, memory_type: str = "general"):
    """
    Saves a piece of long-term memory.
    """

    if not text.strip():
        return "No memory saved."

    memory_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    embedding = create_embedding(text)

    collection.add(
        ids=[memory_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[
            {
                "type": memory_type,
                "created_at": timestamp
            }
        ]
    )

    return f"Memory saved: {text}"


def search_memory(query: str, n_results: int = 5):
    """
    Searches long-term memory for relevant memories.
    """

    if not query.strip():
        return []

    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    memories = []

    for document, metadata in zip(documents, metadatas):
        memories.append(
            {
                "text": document,
                "metadata": metadata
            }
        )

    return memories


def format_memories(memories):
    """
    Converts memory search results into prompt text.
    """

    if not memories:
        return "No relevant long-term memories."

    formatted = []

    for memory in memories:
        text = memory["text"]
        created_at = memory["metadata"].get("created_at", "unknown time")
        memory_type = memory["metadata"].get("type", "general")

        formatted.append(f"- [{memory_type} | {created_at}] {text}")

    return "\n".join(formatted)