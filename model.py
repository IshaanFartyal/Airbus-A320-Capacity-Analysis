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
):
    """Annual output that suppliers can support at a planned monthly rate.

    Supply-chain availability is the share of the planned rate that key
    suppliers can support, so this is the supply ceiling on production.
    """
    return (
        monthly_rate
        * 12
        * supply_chain_availability
    )


def planned_production(
    production_capacity,
    beginning_inventory,
    beginning_backlog,
    new_orders,
    delivery_demand,
):
    """Aircraft actually built in a year.

    Production is capped at what can be delivered: customer delivery
    demand and outstanding orders, less aircraft already in inventory.
    Capacity above that level stays idle rather than building aircraft
    nobody can take.
    """
    deliverable_orders = min(
        delivery_demand,
        beginning_backlog + new_orders,
    )

    required_production = max(
        0,
        deliverable_orders - beginning_inventory,
    )

    return min(
        production_capacity,
        required_production,
    )


def baseline_annual_deliveries(
    baseline_monthly_rate,
    supply_ceiling,
    delivery_demand,
):
    """Deliveries the existing system achieves with no further investment.

    The existing factories can build baseline_monthly_rate x 12 aircraft
    a year. They are held back by the same supply ceiling as the ramp,
    so if suppliers cannot support more than the existing factories can
    already build, the investment adds nothing.
    """
    return min(
        baseline_monthly_rate * 12,
        supply_ceiling,
        delivery_demand,
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

def inventory_build_cash_flow(
    beginning_inventory,
    ending_inventory,
    production_cost_per_aircraft,
):
    """Cash tied up in (or released from) built-but-undelivered aircraft.

    The incremental margin is only earned when an aircraft is delivered,
    so an aircraft that is built and not delivered costs its full
    production cost in that year. The cash comes back if the aircraft
    is delivered from inventory in a later year.
    """
    return (
        ending_inventory
        - beginning_inventory
    ) * production_cost_per_aircraft


def phased_capacity_investment(
    production_ramp,
    base_monthly_rate,
    reference_target_rate,
    reference_investment,
    capex_scaling_exponent,
    comfortable_annual_rate_step,
    expedite_cost_per_rate_point,
):
    """Spread capacity investment over the ramp instead of paying it all at time zero.

    Total capex is set by the peak rate of the ramp. It is allocated to
    each year in proportion to the capacity that comes online that year.
    Year-on-year rate increases above the comfortable step also incur an
    expedite cost, so a faster ramp is no longer free.

    Returns a list of dicts, one per ramp year, with the capex and
    expedite cost attributable to the capacity added in that year.
    """
    peak_rate = max(production_ramp.values())

    total_capex = capacity_dependent_investment(
        target_monthly_rate=peak_rate,
        base_monthly_rate=base_monthly_rate,
        reference_target_rate=reference_target_rate,
        reference_investment=reference_investment,
        capex_scaling_exponent=capex_scaling_exponent,
    )

    total_capacity_added = max(
        0,
        peak_rate - base_monthly_rate,
    )

    schedule = []
    installed_rate = base_monthly_rate

    for year, monthly_rate in production_ramp.items():

        capacity_added = max(
            0,
            monthly_rate - installed_rate,
        )

        if total_capacity_added > 0:
            capex = (
                total_capex
                * capacity_added
                / total_capacity_added
            )
        else:
            capex = 0

        expedite_cost = max(
            0,
            capacity_added - comfortable_annual_rate_step,
        ) * expedite_cost_per_rate_point

        schedule.append({
            "year": year,
            "capacity_added": capacity_added,
            "capex": capex,
            "expedite_cost": expedite_cost,
        })

        installed_rate = max(
            installed_rate,
            monthly_rate,
        )

    return schedule


if __name__ == "__main__":
    show_input_classification()
