class BudgetingService:
    def add(self, *costs: float) -> float:
        """
        Sum all the given costs.

        Args:
            *costs: List of costs to add

        Returns:
            float: Sum all costs.
        """
        return sum(costs)

    def multiply(self, *costs: float) -> float:
        """
        Multiply given costs.

        Args:
            *costs: List of costs to multiply

        Returns:
            float: Product of all costs.
        """
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
        if days == 0:
            return 0.0
        return total_cost / days
