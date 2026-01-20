"""Pydantic models for MCP tool return types.

These models provide explicit schema generation for FastMCP 2.0+,
improving LLM understanding of response structures.
"""

from pydantic import BaseModel, Field


# =============================================================================
# Shared Models
# =============================================================================


class UserInfo(BaseModel):
    """Basic user information included in responses."""

    id: str
    first_name: str | None = None
    last_name: str | None = None


class Period(BaseModel):
    """Date range for a query."""

    start: str = Field(description="Start date in YYYY-MM-DD format")
    end: str = Field(description="End date in YYYY-MM-DD format")


# =============================================================================
# Users Tool Models
# =============================================================================


class User(BaseModel):
    """User record from the API."""

    id: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None


class ListUsersResponse(BaseModel):
    """Response from the list_users tool."""

    users: list[User] = Field(default_factory=list, description="List of users matching the query")
    total: int = Field(default=0, description="Total number of users")
    error: str | None = Field(default=None, description="Error message if the request failed")


# =============================================================================
# Sleep Tool Models
# =============================================================================


class SleepRecord(BaseModel):
    """Individual sleep record."""

    date: str = Field(description="Date of the sleep record in YYYY-MM-DD format")
    start_time: str | None = Field(default=None, description="Sleep start time in HH:MM format")
    end_time: str | None = Field(default=None, description="Sleep end time in HH:MM format")
    duration_minutes: int | None = Field(default=None, description="Total sleep duration in minutes")
    duration_formatted: str | None = Field(default=None, description="Human-readable duration (e.g., '8h 15m')")
    source: str | None = Field(default=None, description="Data source provider (e.g., 'whoop', 'garmin')")


class SleepSummary(BaseModel):
    """Aggregate sleep statistics."""

    total_nights: int = Field(description="Total number of nights in the period")
    nights_with_data: int = Field(description="Number of nights with sleep data recorded")
    avg_duration_minutes: int | None = Field(default=None, description="Average sleep duration in minutes")
    avg_duration_formatted: str | None = Field(default=None, description="Human-readable average duration")
    min_duration_minutes: int | None = Field(default=None, description="Minimum sleep duration in minutes")
    max_duration_minutes: int | None = Field(default=None, description="Maximum sleep duration in minutes")


class SleepRecordsResponse(BaseModel):
    """Response from the get_sleep_records tool."""

    user: UserInfo | None = Field(default=None, description="User information")
    period: Period | None = Field(default=None, description="Date range queried")
    records: list[SleepRecord] = Field(default_factory=list, description="List of sleep records")
    summary: SleepSummary | None = Field(default=None, description="Aggregate statistics")
    error: str | None = Field(default=None, description="Error message if the request failed")
    details: str | None = Field(default=None, description="Additional error details")
    suggestion: str | None = Field(default=None, description="Suggested action to resolve the error")
    matches: list[UserInfo] | None = Field(
        default=None, description="List of matching users when multiple match a search"
    )
    available_users: list[UserInfo] | None = Field(
        default=None, description="List of available users when user_id is not specified"
    )
    total_users: int | None = Field(default=None, description="Total number of available users")


# =============================================================================
# Workouts Tool Models
# =============================================================================


class WorkoutRecord(BaseModel):
    """Individual workout record."""

    date: str | None = Field(default=None, description="Date of the workout in YYYY-MM-DD format")
    type: str | None = Field(default=None, description="Workout type (e.g., 'running', 'cycling')")
    name: str | None = Field(default=None, description="Workout name (e.g., 'Morning Run')")
    start_time: str | None = Field(default=None, description="Workout start time in HH:MM format")
    end_time: str | None = Field(default=None, description="Workout end time in HH:MM format")
    duration_seconds: int | None = Field(default=None, description="Duration in seconds")
    duration_formatted: str | None = Field(default=None, description="Human-readable duration")
    distance_meters: float | None = Field(default=None, description="Distance in meters")
    distance_formatted: str | None = Field(default=None, description="Human-readable distance (e.g., '7.50 km')")
    calories_kcal: float | None = Field(default=None, description="Calories burned")
    avg_heart_rate_bpm: int | None = Field(default=None, description="Average heart rate in BPM")
    max_heart_rate_bpm: int | None = Field(default=None, description="Maximum heart rate in BPM")
    pace_formatted: str | None = Field(default=None, description="Pace in min/km format")
    elevation_gain_meters: float | None = Field(default=None, description="Elevation gain in meters")
    source: str | None = Field(default=None, description="Data source provider")


class WorkoutSummary(BaseModel):
    """Aggregate workout statistics."""

    total_workouts: int = Field(description="Total number of workouts in the period")
    workouts_by_type: dict[str, int] | None = Field(default=None, description="Count of workouts by type")
    total_duration_seconds: int | None = Field(default=None, description="Total duration in seconds")
    total_duration_formatted: str | None = Field(default=None, description="Human-readable total duration")
    total_distance_meters: float | None = Field(default=None, description="Total distance in meters")
    total_distance_formatted: str | None = Field(default=None, description="Human-readable total distance")
    total_calories_kcal: int | None = Field(default=None, description="Total calories burned")


class WorkoutsResponse(BaseModel):
    """Response from the get_workouts tool."""

    user: UserInfo | None = Field(default=None, description="User information")
    period: Period | None = Field(default=None, description="Date range queried")
    workouts: list[WorkoutRecord] = Field(default_factory=list, description="List of workout records")
    summary: WorkoutSummary | None = Field(default=None, description="Aggregate statistics")
    error: str | None = Field(default=None, description="Error message if the request failed")
    details: str | None = Field(default=None, description="Additional error details")
    suggestion: str | None = Field(default=None, description="Suggested action to resolve the error")
    matches: list[UserInfo] | None = Field(
        default=None, description="List of matching users when multiple match a search"
    )
    available_users: list[UserInfo] | None = Field(
        default=None, description="List of available users when user_id is not specified"
    )
    total_users: int | None = Field(default=None, description="Total number of available users")