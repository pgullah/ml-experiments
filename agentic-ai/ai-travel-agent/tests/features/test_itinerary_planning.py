from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from app.common.errors import ServiceError
from app.planner import TravelPlanner
from app.schemas.itinerary import DayPlanInput, FullItineraryInput
from app.service.budget import BudgetingService


class TestItineraryPlanning:
    @staticmethod
    def planner_with_fakes():
        planner = TravelPlanner.__new__(TravelPlanner)
        planner.search_service = Mock()
        planner.weather_service = Mock()
        planner.currency_converter = Mock()
        planner.calculator = BudgetingService()
        return planner

    def test_planner_exposes_the_complete_travel_tool_registry(self):
        planner = TravelPlanner.__new__(TravelPlanner)
        planner.search_service = Mock()
        planner.weather_service = Mock()
        planner.currency_converter = Mock()
        planner.calculator = Mock()

        assert {tool.name for tool in planner._build_tools()} == {
            "search_attraction",
            "search_restaurant",
            "search_activity",
            "search_transport",
            "get_current_weather",
            "get_weather_forecast",
            "search_hotels",
            "hotel_cost",
            "add_costs",
            "multiply_costs",
            "calculate_daily_budget",
            "convert_currency",
            "get_day_plan",
            "create_full_itinerary",
        }

    def test_cost_tools_accept_lists_of_values(self):
        planner = TravelPlanner.__new__(TravelPlanner)
        planner.search_service = Mock()
        planner.weather_service = Mock()
        planner.currency_converter = Mock()
        planner.calculator = Mock()
        planner.calculator.add.side_effect = lambda *values: sum(values)
        planner.calculator.multiply.side_effect = lambda *values: values[0] * values[1]
        tools = {tool.name: tool for tool in planner._build_tools()}

        assert tools["add_costs"].invoke({"costs": [2, 3]}) == 5
        assert tools["multiply_costs"].invoke({"costs": [2, 3]}) == 6

    def test_search_tools_return_bounded_service_results(self):
        planner = self.planner_with_fakes()
        planner.search_service.run.return_value = "Source: https://example.com"
        tools = {tool.name: tool for tool in planner._build_tools()}

        assert "Top attractions in Rome" in tools["search_attraction"].invoke(
            {"city": "Rome"}
        )
        assert "Top restaurant in Rome" in tools["search_restaurant"].invoke(
            {"city": "Rome"}
        )
        assert "Top activities in Rome" in tools["search_activity"].invoke(
            {"city": "Rome"}
        )
        assert "Means of transport in Rome" in tools["search_transport"].invoke(
            {"city": "Rome"}
        )
        assert "Hotels in Rome" in tools["search_hotels"].invoke(
            {
                "city": "Rome",
                "check_in_date": "2026-06-01",
                "check_out_date": "2026-06-03",
            }
        )

    def test_weather_tools_format_success_and_safe_failure(self):
        planner = self.planner_with_fakes()
        planner.weather_service.get_weather.return_value = {
            "main": {"temp": 20},
            "weather": [{"description": "clear"}],
        }
        planner.weather_service.get_forecast.return_value = {"list": [{"temp": 20}]}
        tools = {tool.name: tool for tool in planner._build_tools()}

        assert tools["get_current_weather"].invoke({"city": "Rome"}) == (
            "Current weather in Rome : 20°C, clear"
        )
        assert tools["get_weather_forecast"].invoke({"city": "Rome", "days": 3}) == {
            "list": [{"temp": 20}]
        }

        planner.weather_service.get_weather.side_effect = ServiceError("secret detail")
        assert "due to error" in tools["get_current_weather"].invoke({"city": "Rome"})

    def test_budget_currency_and_itinerary_tools_work_together(self):
        planner = self.planner_with_fakes()
        planner.currency_converter.convert_currency.return_value = 120.0
        tools = {tool.name: tool for tool in planner._build_tools()}

        assert tools["hotel_cost"].invoke({"price_per_night": 50, "days": 2}) == 100
        assert (
            tools["calculate_daily_budget"].invoke({"total_cost": 300, "days": 3})
            == 100
        )
        assert (
            tools["convert_currency"].invoke(
                {"amount": 100, "from_currency": "GBP", "to_currency": "EUR"}
            )
            == 120.0
        )

        day = tools["get_day_plan"].invoke(
            {
                "date": "2026-06-01",
                "day_number": 1,
                "plan_items": [
                    {
                        "time": "09:00",
                        "activity": "Colosseum",
                        "location": "Rome",
                        "estimated_cost": "€20",
                        "notes": "Book ahead",
                    }
                ],
                "summary": "Ancient Rome",
                "weather_forecast": "Clear",
            }
        )
        assert "Colosseum" in day
        assert "Book ahead" in day

        itinerary = tools["create_full_itinerary"].invoke(
            {
                "destination": "Rome",
                "start_date": "2026-06-01",
                "end_date": "2026-06-01",
                "total_days": 1,
                "daily_plans": [day],
                "overall_summary": "A short trip",
                "budget_information": "€200",
                "overall_weather_summary": "Clear",
            }
        )
        assert "Your Trip to Rome" in itinerary
        assert "generated by AI" in itinerary

    def test_currency_tool_hides_service_failure_details(self):
        planner = self.planner_with_fakes()
        planner.currency_converter.convert_currency.side_effect = ServiceError(
            "provider secret"
        )
        tools = {tool.name: tool for tool in planner._build_tools()}

        result = tools["convert_currency"].invoke(
            {"amount": 1, "from_currency": "GBP", "to_currency": "EUR"}
        )

        assert result == "Currency conversion is currently unavailable"
        assert "provider secret" not in result

    def test_day_plan_validates_nested_plan_items(self):
        plan = DayPlanInput(
            date="2026-01-01",
            day_number=1,
            plan_items=[
                {
                    "time": "09:00",
                    "activity": "Walk",
                    "estimated_cost": "£10",
                }
            ],
        )

        assert plan.plan_items[0].estimated_cost == "£10"

    @pytest.mark.parametrize(
        "values",
        [
            {"date": "not-a-date", "day_number": 1, "plan_items": [{}]},
            {"date": "2026-01-01", "day_number": 0, "plan_items": []},
        ],
    )
    def test_invalid_day_plans_are_rejected(self, values):
        with pytest.raises(ValidationError):
            DayPlanInput.model_validate(values)

    def test_itinerary_dates_days_and_plan_count_must_agree(self):
        with pytest.raises(ValidationError):
            FullItineraryInput(
                destination="Rome",
                start_date="2026-01-01",
                end_date="2026-01-03",
                total_days=2,
                daily_plans=["day one", "day two"],
            )

    def test_budget_rejects_invalid_values(self):
        service = BudgetingService()

        with pytest.raises(ValueError):
            service.add(10, -1)
        with pytest.raises(ValueError):
            service.calculate_daily_budget(100, 0)

        assert service.add(10, 20) == 30
        assert service.multiply(10, 2) == 20
        assert service.calculate_daily_budget(300, 3) == 100
