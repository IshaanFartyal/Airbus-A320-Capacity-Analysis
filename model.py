import pandas as pd


def load_reported_inputs():
    df = pd.read_csv("data/airbus_inputs.csv")
    return df


def load_input_values():
    df = load_reported_inputs()

    return dict(
        zip(
            df["parameter"],
            df["value"]
        )
    )


def load_assumptions(case="base"):

    if case not in {
        "base",
        "low",
        "high"
    }:
        raise ValueError(
            "case must be 'base', 'low', or 'high'"
        )

    df = pd.read_csv(
        "data/airbus_assumptions.csv"
    )

    return dict(
        zip(
            df["parameter"],
            df[case]
        )
    )


def annual_production(
    monthly_rate,
    supply_chain_availability=1.0,
    demand_utilization=1.0
):
    return (
        monthly_rate
        * 12
        * supply_chain_availability
        * demand_utilization
    )


def incremental_annual_deliveries(
    target_monthly_rate,
    base_annual_deliveries,
    supply_chain_availability=1.0,
    demand_utilization=1.0
):

    target_annual = annual_production(
        monthly_rate=target_monthly_rate,
        supply_chain_availability=supply_chain_availability,
        demand_utilization=demand_utilization
    )

    return (
        target_annual
        - base_annual_deliveries
    )


def incremental_annual_profit(
    incremental_deliveries,
    incremental_margin_per_aircraft
):
    return (
        incremental_deliveries
        * incremental_margin_per_aircraft
    )


def show_input_classification():

    reported_df = pd.read_csv(
        "data/airbus_inputs.csv"
    )

    assumptions_df = pd.read_csv(
        "data/airbus_assumptions.csv"
    )

    print("REPORTED / DERIVED INPUTS")
    print("=" * 70)

    print(
        reported_df[
            [
                "parameter",
                "value",
                "unit",
                "source_type",
                "source_or_derivation"
            ]
        ].to_string(index=False)
    )

    print()

    print("MODEL ASSUMPTIONS")
    print("=" * 70)

    print(
        assumptions_df[
            [
                "parameter",
                "base",
                "low",
                "high",
                "unit",
                "source_type",
                "assumption_note"
            ]
        ].to_string(index=False)
    )

def annual_delivery_flow(
    annual_production,
    beginning_inventory,
    beginning_backlog,
    new_orders,
    delivery_demand,
):
    available_aircraft = (
        beginning_inventory
        + annual_production
    )

    available_orders = (
        beginning_backlog
        + new_orders
    )

    deliverable_orders = min(
        delivery_demand,
        available_orders,
    )

    deliveries = min(
        available_aircraft,
        deliverable_orders,
    )

    ending_inventory = (
        available_aircraft
        - deliveries
    )

    ending_backlog = (
        available_orders
        - deliveries
    )

    return (
        deliveries,
        ending_inventory,
        ending_backlog,
    )


def inventory_holding_cost(
    beginning_inventory,
    ending_inventory,
    inventory_cost_per_aircraft,
):
    average_inventory = (
        beginning_inventory
        + ending_inventory
    ) / 2

    return (
        average_inventory
        * inventory_cost_per_aircraft
    )


def capacity_dependent_investment(
    target_monthly_rate,
    base_monthly_rate,
    reference_target_rate,
    reference_investment,
    capex_scaling_exponent,
):
    additional_capacity = max(
        0,
        target_monthly_rate - base_monthly_rate,
    )

    reference_additional_capacity = (
        reference_target_rate
        - base_monthly_rate
    )

    if additional_capacity == 0:
        return 0

    capacity_ratio = (
        additional_capacity
        / reference_additional_capacity
    )

    return (
        reference_investment
        * capacity_ratio ** capex_scaling_exponent
    )

if __name__ == "__main__":
    show_input_classification()
