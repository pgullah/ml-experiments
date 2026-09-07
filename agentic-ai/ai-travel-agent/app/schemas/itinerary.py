from pydantic import BaseModel, Field


class DayPlanItem(BaseModel):
    time: str = Field(
        description="Estimated time of the activity, for example 09:00-11:00."
    )
    activity: str = Field(description="Description of the planned activity.")
    location: str | None = Field(default=None, description="Location or address.")
    notes: str | None = Field(default=None, description="Relevant recommendations.")
    estimated_cost: str | None = Field(
        default=None,
        description="Estimated cost including its currency.",
    )


class DayPlanInput(BaseModel):
    date: str = Field(description="Plan date in YYYY-MM-DD format.")
    day_number: int = Field(description="Day number in the itinerary.")
    plan_items: list[DayPlanItem] = Field(
        description="Activities in chronological order."
    )
    summary: str | None = Field(default=None, description="Summary of the day.")
    weather_forecast: str | None = Field(
        default=None,
        description="Weather forecast when available.",
    )


class FullItineraryInput(BaseModel):
    destination: str = Field(description="Main destination city.")
    start_date: str = Field(description="Trip start date in YYYY-MM-DD format.")
    end_date: str = Field(description="Trip end date in YYYY-MM-DD format.")
    total_days: int = Field(description="Total number of trip days.")
    daily_plans: list[str] = Field(description="Formatted daily plans.")
    overall_summary: str | None = Field(default=None, description="Trip summary.")
    budget_information: str | None = Field(
        default=None,
        description="Trip budget summary.",
    )
    overall_weather_summary: str | None = Field(
        default=None,
        description="Overall weather summary.",
    )
