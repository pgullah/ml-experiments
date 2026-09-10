class BudgetingService:
    @staticmethod
    def _validate_costs(costs: tuple[float, ...]) -> None:
        if any(cost < 0 for cost in costs):
            raise ValueError("Costs must not be negative")

    def add(self, *costs: float) -> float:
        """
        Sum all the given costs.

        Args:
            *costs: List of costs to add

        Returns:
            float: Sum all costs.
        """
        self._validate_costs(costs)
        return sum(costs)

    def multiply(self, *costs: float) -> float:
        """
        Multiply given costs.

        Args:
            *costs: List of costs to multiply

        Returns:
            float: Product of all costs.
        """
        self._validate_costs(costs)
        result = 1
        for cost in costs:
            result *= cost
        return result

    def calculate_daily_budget(self, total_cost: float, days: int) -> float:
        """
        Calculate the daily budget based on total cost and number of days.
        Args:
            total_cost (float): Total cost of the trip.
            days (int): Number of days for the trip.
        Returns:
            float: Daily budget for the trip.
        """
        if total_cost < 0:
            raise ValueError("Total cost must not be negative")
        if days <= 0:
            raise ValueError("Days must be greater than zero")
        return total_cost / days
