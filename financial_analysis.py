def npv(initial_investment, annual_cash_flows, discount_rate):
    """Calculate net present value in the same currency units as the inputs."""
    value = -initial_investment

    for year, cash_flow in enumerate(annual_cash_flows, start=1):
        value += cash_flow / ((1 + discount_rate) ** year)

    return value


def payback_period(initial_investment, annual_incremental_profit):
    """Simple payback period in years."""
    if annual_incremental_profit <= 0:
        return None

    return initial_investment / annual_incremental_profit
