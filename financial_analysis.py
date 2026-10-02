def npv(initial_investment, annual_cash_flows, discount_rate):
    """Calculate net present value in the same currency units as the inputs."""
    value = -initial_investment

    for year, cash_flow in enumerate(annual_cash_flows, start=1):
        value += cash_flow / ((1 + discount_rate) ** year)

    return value


def extension_value(
    final_cash_flow,
    discount_rate,
    modelled_years,
    extension_years,
):
    """Present value of the capacity continuing to earn after the model ends.

    The final modelled year's cash flow is assumed to continue at the
    same level for a fixed number of further years. Each of those cash
    flows is discounted back to time zero.

    This is more conservative than a terminal value with perpetual
    growth, which assumes the cash flow continues and grows for ever.
    """
    value = 0

    for extra_year in range(1, int(extension_years) + 1):
        year = modelled_years + extra_year

        value += final_cash_flow / ((1 + discount_rate) ** year)

    return value


def payback_period(initial_investment, annual_incremental_profit):
    """Simple payback period in years."""
    if annual_incremental_profit <= 0:
        return None

    return initial_investment / annual_incremental_profit
