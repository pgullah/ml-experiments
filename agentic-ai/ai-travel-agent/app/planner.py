import logging
from typing import Any

from langchain_core.tools import BaseTool, tool

from app.common.config import AppSettings
from app.common.llm_loader import load_llm
from app.service.budget import BudgetingService
from app.service.currency import CurrencyService
from app.service.search import SearchService
from app.service.weather import WeatherTool
from app.schemas.itinerary import DayPlanInput, DayPlanItem, FullItineraryInput

logger = logging.getLogger(__name__)

class TravelPlanner:
    """Compose travel services and expose their tools to the language model."""

    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.weather_service = WeatherTool(settings)
        self.currency_converter = CurrencyService(settings)
        self.calculator = BudgetingService()
        self.search_service = SearchService(settings)
        self.llm = load_llm(settings)
        self.tools = self._build_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def _build_tools(self) -> list[BaseTool]:
        """Build the explicit registry of tools exposed to the travel agent."""

        def search(query: str, success_prefix: str, failure_message: str) -> str:
            try:
                results = self.search_service.run(query)
                return f"{success_prefix}: {results}" if results else failure_message
            except Exception:
                logger.exception("Travel search failed (query=%s)", query)
                return failure_message

        @tool
        def search_attraction(city: str) -> str:
            """Search for top tourist attractions in a city."""
            results = self.search_service.run(f"Top tourist attractions in {city}")
            if results:
                return f"Top attraction in {city} : {results}"
            return f"Top attraction in {city} not found"

        @tool
        def search_restaurant(city: str) -> str:
            """Search for top restaurants in a city."""
            return search(
                f"Top restaurants in {city}",
                f"Top restaurant in {city}",
                f"Top restaurant in {city} not found",
            )

        @tool
        def search_activity(city: str) -> str:
            """Search for top activities in a city."""
            return search(
                f"Top activities in {city}",
                f"Top activities in {city}",
                f"Top activities in {city} not found",
            )

        @tool
        def search_transport(city: str) -> str:
            """Search for local transportation options in a city."""
            return search(
                f"Means of transport in {city}",
                f"Means of transport in {city}",
                f"Means of transport in {city} not found",
            )

        @tool
        def get_current_weather(city: str) -> str:
            """Get the current weather for a city."""
            try:
                current_weather = self.weather_service.get_weather(city)
                if current_weather and "main" in current_weather and "weather" in current_weather:
                    description = current_weather["weather"][0]["description"]
                    temperature = current_weather["main"]["temp"]
                    return f"Current weather in {city} : {temperature}°C, {description}"
                return f"Current weather in {city} not found"
            except Exception:
                logger.exception("Current weather lookup failed (city=%s)", city)
                return f"Current weather in {city} not found due to error"

        @tool
        def get_weather_forcast(city: str, days: int = 5) -> dict[str, Any] | str:
            """Get up to five days of weather forecast data for a city."""
            try:
                forecast = self.weather_service.get_forecast(city, days)
                if forecast and "list" in forecast:
                    return forecast
                return {"error": f"Weather forecast for {city} not found"}
            except Exception:
                logger.exception("Weather forecast lookup failed (city=%s)", city)
                return f"Weather forecast for {city} not found due to error"

        @tool
        def search_hotels(
            city: str,
            check_in_date: str | None = None,
            check_out_date: str | None = None,
        ) -> str:
            """Search for hotels, current prices, and availability in a city."""
            query = f"Mid range hotels in {city}"
            if check_in_date and check_out_date:
                query += f" from {check_in_date} to {check_out_date}"
            query += ". Name of hotel and current price per night booking availability"
            return search(query, f"Hotels in {city}", f"Hotels in {city} not found")

        @tool
        def hotel_cost(price_per_night: float, days: int) -> float:
            """Calculate total accommodation cost."""
            return self.calculator.multiply(price_per_night, days)

        @tool
        def add_costs(costs: list[float]) -> float:
            """Add multiple travel costs."""
            return self.calculator.add(*costs)

        @tool
        def multiply_costs(costs: list[float]) -> float:
            """Multiply travel cost values."""
            return self.calculator.multiply(*costs)

        @tool
        def calculate_daily_budget(total_cost: float, days: int) -> float:
            """Calculate average daily cost for a trip."""
            return self.calculator.calculate_daily_budget(total_cost, days)

        @tool
        def convert_currency(
            amount: float,
            from_currency: str,
            to_currency: str,
        ) -> float | None:
            """Convert an amount between currencies."""
            return self.currency_converter.convert_currency(
                amount,
                from_currency,
                to_currency,
            )

        @tool(args_schema=DayPlanInput)
        def get_day_plan(
            date: str,
            day_number: int,
            plan_items: list[DayPlanItem],
            summary: str | None = None,
            weather_forecast: str | None = None,
        ) -> str:
            """Create a structured daily itinerary from chronological activities."""
            output = [f"---Day {day_number} ({date})---"]
            if summary:
                output.append(f"Summary: {summary}")
            if weather_forecast:
                output.append(f"Weather for the Day {day_number}: {weather_forecast}")
            output.append("\n")

            for item in plan_items:
                if isinstance(item, dict):
                    item = DayPlanItem.model_validate(item)
                output.append(f"  {item.time}: {item.activity}")
                if item.location:
                    output.append(f"   Location: {item.location}")
                if item.estimated_cost:
                    output.append(f"   Estimated Cost: {item.estimated_cost}")
                if item.notes:
                    output.append(f"   Notes: {item.notes}")
                output.append("")
            output.append("---------------------------------\n")
            return "\n".join(output)

        @tool(args_schema=FullItineraryInput)
        def create_full_itinerary(
            destination: str,
            start_date: str,
            end_date: str,
            total_days: int,
            daily_plans: list[str],
            overall_summary: str | None = None,
            budget_information: str | None = None,
            overall_weather_summary: str | None = None,
        ) -> str:
            """Combine daily plans into a complete trip itinerary."""
            output = [
                f"***** Your Trip to {destination} *****",
                f"Dates: {start_date} to {end_date} ({total_days} days)",
            ]
            if overall_summary:
                output.append(f"Overview: {overall_summary}")
            if budget_information:
                output.append(f"Budget : {budget_information}")
            if overall_weather_summary:
                output.append(f"Overall Weather Outlook: {overall_weather_summary}")
            output.append("\n" + "=" * 50 + "\n")
            output.extend(daily_plans)
            output.extend(
                [
                    "\n" + "=" * 50 + "\n",
                    "**This itinerary is generated by AI. Please verify the "
                    "information before making any bookings.**\n",
                    "***** End of Trip Plan *****",
                ]
            )
            return "\n".join(output)

        return [
            search_attraction,
            search_restaurant,
            search_activity,
            search_transport,
            get_current_weather,
            get_weather_forcast,
            search_hotels,
            hotel_cost,
            add_costs,
            multiply_costs,
            calculate_daily_budget,
            convert_currency,
            get_day_plan,
            create_full_itinerary,
        ]
