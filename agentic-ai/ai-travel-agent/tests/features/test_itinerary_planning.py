from unittest.mock import Mock

from app.schemas.itinerary import DayPlanInput
from app.planner import TravelPlanner


class TestItineraryPlanning:
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
            "get_weather_forcast",
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
