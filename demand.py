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


def get_demand_plan():
    return {
        year: values.copy()
        for year, values in DEMAND_PLAN.items()
    }


if __name__ == "__main__":
    print("A320 Demand Plan")
    print("-" * 50)

    for year, values in DEMAND_PLAN.items():
        print(
            f"{year}: "
            f"demand={values['delivery_demand']}, "
            f"new orders={values['new_orders']}"
        )
