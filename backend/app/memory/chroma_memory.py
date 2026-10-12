"""
AI Memory (ChromaDB-backed).

Stores short text "memory entries" per user -- things like opportunities
they clicked on, chat messages revealing a preference, or tasks they
completed -- as embeddings. The chatbot and opportunity ranker can then
recall semantically similar past entries to personalize future
responses, which is what actually makes "recommendations improve over
time" true rather than just a claim in the project description.

Runs embedded/local via ChromaDB's PersistentClient -- no separate
server needed, unlike Pinecone which requires a cloud account. This is
exactly why ChromaDB was chosen over Pinecone for this build.
"""
from app.core.config import get_settings

settings = get_settings()
_chroma_client = None
_collection = None


def _get_collection():
    global _chroma_client, _collection
    if _collection is None:
        import chromadb
        _chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        _collection = _chroma_client.get_or_create_collection(name="user_memory")
    return _collection


def add_memory(user_id: str, text: str, metadata: dict = None) -> None:
    """
    Stores one memory entry. Called whenever something worth remembering
    happens: a chat message, an opportunity click, a completed task with
    a notable category, etc.
    """
    import uuid
    collection = _get_collection()
    entry_id = str(uuid.uuid4())
    meta = {"user_id": user_id, **(metadata or {})}
    collection.add(ids=[entry_id], documents=[text], metadatas=[meta])


def recall_memories(user_id: str, query: str, n_results: int = 5) -> list:
    """
    Returns the n most semantically similar past memory entries for this
    user, given a query string (e.g. the user's current chat message).
    """
    collection = _get_collection()
    user_count = get_user_memory_count(user_id)
    if user_count == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, user_count),  # bounded by THIS user's count, not the global total
        where={"user_id": user_id},
    )
    documents = results.get("documents", [[]])[0]
    return documents


def get_user_memory_count(user_id: str) -> int:
    collection = _get_collection()
    if collection.count() == 0:
        return 0
    results = collection.get(where={"user_id": user_id})
    return len(results.get("ids", []))
