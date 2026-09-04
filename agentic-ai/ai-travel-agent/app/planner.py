from langchain_core.tools import BaseTool

from app.common.config import AppSettings
from app.common.llm_loader import load_llm
from app.tools.budget import BudgetingTool
from app.tools.currency import CurrencyTool
from app.tools.search import SearchService
from app.tools.travel import build_travel_tools
from app.tools.weather import WeatherTool


class TravelPlanner:
    """Compose travel services and expose their tools to the language model."""

    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.weather_service = WeatherTool(settings)
        self.currency_converter = CurrencyTool(settings)
        self.calculator = BudgetingTool()
        self.search_service = SearchService(settings)
        self.llm = load_llm(settings)
        self.tools = self._build_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def _build_tools(self) -> list[BaseTool]:
        return build_travel_tools(
            search_service=self.search_service,
            weather_service=self.weather_service,
            currency_converter=self.currency_converter,
            calculator=self.calculator,
        )