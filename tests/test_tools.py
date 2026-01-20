"""Tests for MCP tools using FastMCP's direct client connection."""

import json
from unittest.mock import AsyncMock, patch

from fastmcp import Client
from mcp.types import TextContent

from app.main import mcp


async def test_list_users():
    """Test list_users tool returns user data."""
    mock_response = {
        "items": [{"id": "user-123", "first_name": "John", "last_name": "Doe", "email": "john@example.com"}],
        "total": 1,
    }

    with patch("app.tools.users.client.get_users", new_callable=AsyncMock, return_value=mock_response):
        async with Client(mcp) as client:
            result = await client.call_tool("list_users", {})

            assert isinstance(result.content[0], TextContent)
            data = json.loads(result.content[0].text)
            assert data["total"] == 1
            assert data["users"][0]["first_name"] == "John"


async def test_get_sleep_records():
    """Test get_sleep_records tool returns sleep data."""
    mock_users = {"items": [{"id": "user-123", "first_name": "John", "last_name": "Doe"}], "total": 1}
    mock_sleep = {
        "data": [{"date": "2025-01-15", "start_time": "23:00", "end_time": "07:00", "duration_minutes": 480}]
    }

    with (
        patch("app.tools.sleep.client.get_users", new_callable=AsyncMock, return_value=mock_users),
        patch("app.tools.sleep.client.get_sleep_summaries", new_callable=AsyncMock, return_value=mock_sleep),
    ):
        async with Client(mcp) as client:
            result = await client.call_tool("get_sleep_records", {"days": 7})

            assert isinstance(result.content[0], TextContent)
            data = json.loads(result.content[0].text)
            assert data["user"]["first_name"] == "John"
            assert len(data["records"]) == 1
            assert data["records"][0]["duration_minutes"] == 480


async def test_get_workouts():
    """Test get_workouts tool returns workout data."""
    mock_users = {"items": [{"id": "user-123", "first_name": "John", "last_name": "Doe"}], "total": 1}
    mock_workouts = {
        "data": [
            {
                "type": "running",
                "name": "Morning Run",
                "start_time": "2025-01-15T07:00:00Z",
                "end_time": "2025-01-15T07:45:00Z",
                "duration_seconds": 2700,
                "distance_meters": 5000,
                "calories_kcal": 350,
            }
        ]
    }

    with (
        patch("app.tools.workouts.client.get_users", new_callable=AsyncMock, return_value=mock_users),
        patch("app.tools.workouts.client.get_workouts", new_callable=AsyncMock, return_value=mock_workouts),
    ):
        async with Client(mcp) as client:
            result = await client.call_tool("get_workouts", {"days": 7})

            assert isinstance(result.content[0], TextContent)
            data = json.loads(result.content[0].text)
            assert data["user"]["first_name"] == "John"
            assert len(data["workouts"]) == 1
            assert data["workouts"][0]["type"] == "running"
