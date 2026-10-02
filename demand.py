# A320-family yearly demand assumptions
# delivery_demand = aircraft customers are assumed ready to accept that year
# new_orders = new firm orders added to backlog during that year
# Values are illustrative and not based on any Airbus internal data or forecasts

DEMAND_PLAN = {
    2026: {
        "delivery_demand": 800,
        "new_orders": 800,
    },
    2027: {
        "delivery_demand": 840,
        "new_orders": 820,
    },
    2028: {
        "delivery_demand": 870,
        "new_orders": 820,
    },
    2029: {
        "delivery_demand": 900,
        "new_orders": 820,
    },
    2030: {
        "delivery_demand": 900,
        "new_orders": 820,
    },
    2031: {
        "delivery_demand": 900,
        "new_orders": 820,
    },
    2032: {
        "delivery_demand": 900,
        "new_orders": 820,
    },
    2033: {
        "delivery_demand": 900,
        "new_orders": 820,
    },
    2034: {
        "delivery_demand": 900,
        "new_orders": 820,
    },
    2035: {
        "delivery_demand": 900,
        "new_orders": 820,
    },
}


# Long-run delivery demand levels used for the demand sensitivity.
# The base level is the long-run value of DEMAND_PLAN above.
#
# low:  roughly the long-run A320neo-family net order rate, so
#       deliveries match new orders with no backlog rundown
# base: Airbus's stated stabilisation rate of 75 per month, about 53%
#       of Airbus's forecast single-aisle market
# high: roughly a 58-60% share of the forecast single-aisle market
DEMAND_LEVELS = {
    "low": 760,
    "base": 900,
    "high": 1000,
}


def get_demand_plan(case="base"):
    """Yearly demand plan, scaled to the long-run level of the chosen case.

    The base case returns DEMAND_PLAN unchanged. The low and high cases
    scale delivery demand in every year by the same factor. New orders
    are left unchanged.
    """
    if case not in DEMAND_LEVELS:
        raise ValueError(
            "Demand case must be 'low', 'base', or 'high'"
        )

    scale = DEMAND_LEVELS[case] / DEMAND_LEVELS["base"]

    plan = {}

    for year, values in DEMAND_PLAN.items():
        plan[year] = values.copy()

        plan[year]["delivery_demand"] = round(
            values["delivery_demand"] * scale
        )

    return plan


if __name__ == "__main__":
    print("A320 Demand Plan")
    print("-" * 50)

    for year, values in DEMAND_PLAN.items():
        print(
            f"{year}: "
            f"demand={values['delivery_demand']}, "
            f"new orders={values['new_orders']}"
        )
