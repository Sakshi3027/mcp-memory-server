from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

import storage

mcp = FastMCP("memory")
storage.init_db()


@mcp.tool()
def save_memory(
    content: Annotated[str, Field(min_length=1, description="The fact to remember, as a short standalone sentence.")],
    tags: Annotated[str, Field(description="Optional comma-separated keywords, e.g. 'food,preference'.")] = "",
) -> str:
    """Save a piece of information to long-term memory.

    Use this when the user shares a fact, preference, or decision
    that would be useful to remember in future conversations.
    """
    memory_id = storage.add_memory(content, tags)
    return f"Saved memory #{memory_id}."


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def search_memory(
    query: Annotated[str, Field(min_length=1, description="One short keyword, e.g. 'food' or 'python'.")],
    limit: Annotated[int, Field(ge=1, le=20)] = 5,
) -> dict:
    """Search long-term memory for information saved in past conversations.

    Call this before answering questions about the user's preferences,
    background, or past decisions. Search with one short keyword at a
    time, not a full sentence.
    """
    results = storage.search_memories(query, limit)
    return {"count": len(results), "memories": results}


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def list_memories(limit: Annotated[int, Field(ge=1, le=50)] = 20) -> dict:
    """List the most recent memories, newest first.

    Use this when the user asks what you remember about them.
    """
    results = storage.list_memories(limit)
    return {"count": len(results), "memories": results}


@mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
def forget_memory(
    memory_id: Annotated[int, Field(description="The id of the memory to delete.")],
) -> str:
    """Permanently delete a memory by its id.

    Use this when the user asks you to forget something or says a saved
    fact is wrong. Find the id with search_memory or list_memories first.
    """
    if storage.delete_memory(memory_id):
        return f"Forgot memory #{memory_id}."
    return f"No memory with id #{memory_id} was found."


if __name__ == "__main__":
    mcp.run()