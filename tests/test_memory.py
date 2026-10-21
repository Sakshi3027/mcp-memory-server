import pytest
from mcp.server.fastmcp.exceptions import ToolError

import server
import storage


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "test.db")
    storage.init_db()


def test_add_and_list_newest_first():
    first = storage.add_memory("Sakshi prefers Python", "preference")
    second = storage.add_memory("Sakshi is vegetarian", "food")
    memories = storage.list_memories()
    assert [m["id"] for m in memories] == [second, first]


def test_search_matches_content_and_tags():
    storage.add_memory("Sakshi prefers Python", "preference")
    storage.add_memory("Sakshi is vegetarian", "food")
    assert storage.search_memories("PYTHON")[0]["content"] == "Sakshi prefers Python"
    assert storage.search_memories("food")[0]["content"] == "Sakshi is vegetarian"
    assert storage.search_memories("marathon") == []


def test_search_respects_limit():
    for i in range(10):
        storage.add_memory(f"note {i}")
    assert len(storage.search_memories("note", limit=3)) == 3


def test_delete_returns_whether_memory_existed():
    memory_id = storage.add_memory("temporary fact")
    assert storage.delete_memory(memory_id) is True
    assert storage.delete_memory(memory_id) is False
    assert storage.list_memories() == []


@pytest.mark.anyio
async def test_server_exposes_four_tools():
    tools = await server.mcp.list_tools()
    assert {tool.name for tool in tools} == {
        "save_memory",
        "search_memory",
        "list_memories",
        "forget_memory",
    }


@pytest.mark.anyio
async def test_invalid_limit_is_rejected():
    with pytest.raises(ToolError):
        await server.mcp.call_tool("search_memory", {"query": "python", "limit": 100})