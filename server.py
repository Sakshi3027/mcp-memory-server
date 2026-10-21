from mcp.server.fastmcp import FastMCP

mcp = FastMCP("memory")


@mcp.tool()
def save_memory(content: str) -> str:
    """Save a piece of information to long-term memory.

    Use this when the user shares a fact, preference, or decision
    that would be useful to remember in future conversations.
    """
    return f"Saved: {content}"


if __name__ == "__main__":
    mcp.run()