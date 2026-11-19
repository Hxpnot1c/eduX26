"""Input limits (register C18): oversized input is refused by the tool schema, ordinary input is not."""

import asyncio

import pytest

from edux import server


def _schema(tool: str) -> dict:
    mcp = server.build_server()
    tools = asyncio.run(mcp.list_tools())
    return next(t for t in tools if t.name == tool).inputSchema


def test_the_message_has_a_length_limit():
    assert _schema("tutor_turn")["properties"]["message"]["maxLength"] == server.MAX_MESSAGE


def test_lists_and_ids_are_bounded():
    schema = _schema("tutor_turn")
    assert schema["properties"]["node_ids"]["anyOf"][0]["maxItems"] == server.MAX_LIST
    answer = schema["$defs"]["Answer"]["properties"]
    assert answer["points_met"]["maxItems"] == server.MAX_LIST and answer["points_met"]["items"]["maxLength"] == server.MAX_ID


def test_the_interests_line_is_bounded():
    assert _schema("update_my_profile")["properties"]["interests"]["anyOf"][0]["maxLength"] == server.MAX_INTERESTS


def test_the_limits_are_far_above_ordinary_use():
    assert server.MAX_MESSAGE >= 4000 and server.MAX_LIST >= 20 and server.MAX_ID >= 80
