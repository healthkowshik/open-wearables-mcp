"""Open Wearables MCP Server - Main entry point."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastmcp import FastMCP

from app.config import settings
from app.services.api_client import client
from app.tools.sleep import get_sleep_records
from app.tools.users import list_users
from app.tools.workouts import get_workouts

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastMCP) -> AsyncIterator[None]:
    """Manage application lifecycle - startup and shutdown.

    Note: In FastMCP, lifespan runs per-client-session, not per-server.
    This is still useful for cleanup when the session ends.
    """
    logger.info("MCP session starting - HTTP client will be initialized on first request")
    try:
        yield
    finally:
        logger.info("MCP session ending - closing HTTP client")
        await client.close()


# Create FastMCP server instance
mcp = FastMCP(
    "open-wearables",
    instructions="""
    Open Wearables MCP Server - Query wearable health data from multiple providers.

    Available tools:
    - list_users: Discover users accessible via your API key
    - get_sleep_records: Get sleep data for a user over the last X days
    - get_workouts: Get workout data for a user over the last X days

    Workflow:
    1. If you don't know the user's ID, call list_users first
    2. Use the user's ID (or name) to query their health data
    3. Present the data in a human-friendly format

    The API key determines which users you can access (personal, team, or enterprise scope).
    """,
    lifespan=lifespan,
)

# Register tools
mcp.tool(list_users)
mcp.tool(get_sleep_records)
mcp.tool(get_workouts)

logger.info(f"Open Wearables MCP server initialized. API URL: {settings.open_wearables_api_url}")


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
