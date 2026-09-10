from datetime import date as Date

from pydantic import BaseModel, Field, PositiveInt, model_validator


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
    date: Date = Field(description="Plan date in YYYY-MM-DD format.")
    day_number: PositiveInt = Field(description="Day number in the itinerary.")
    plan_items: list[DayPlanItem] = Field(
        min_length=1, description="Activities in chronological order."
    )
    summary: str | None = Field(default=None, description="Summary of the day.")
    weather_forecast: str | None = Field(
        default=None,
        description="Weather forecast when available.",
    )


class FullItineraryInput(BaseModel):
    destination: str = Field(description="Main destination city.")
    start_date: Date = Field(description="Trip start date in YYYY-MM-DD format.")
    end_date: Date = Field(description="Trip end date in YYYY-MM-DD format.")
    total_days: PositiveInt = Field(description="Total number of trip days.")
    daily_plans: list[str] = Field(
        min_length=1,
        description="Formatted daily plans.",
    )
    overall_summary: str | None = Field(default=None, description="Trip summary.")
    budget_information: str | None = Field(
        default=None,
        description="Trip budget summary.",
    )
    overall_weather_summary: str | None = Field(
        default=None,
        description="Overall weather summary.",
    )

    @model_validator(mode="after")
    def validate_trip_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")

        expected_days = (self.end_date - self.start_date).days + 1
        if self.total_days != expected_days:
            raise ValueError(
                "total_days must match the inclusive start_date and end_date range"
            )
        if len(self.daily_plans) != self.total_days:
            raise ValueError("daily_plans must contain one plan for every trip day")
        return self
