import pandas as pd

from demand import get_demand_plan
from financial_analysis import extension_value, npv
from model import (
    annual_delivery_flow,
    annual_production,
    baseline_annual_deliveries,
    capacity_dependent_investment,
    inventory_build_cash_flow,
    incremental_annual_profit,
    inventory_holding_cost,
    load_assumptions,
    load_input_values,
    phased_capacity_investment,
    planned_production,
)
from production_plan import (
    DELAY_YEARS,
    RAMP_LABELS,
    TARGET_CASE,
    first_full_year_at_rate,
    get_delayed_ramp,
    get_production_ramp,
    get_rate_sensitivity,
)

reported = load_input_values()


# --------------------------------------------------
# Shared year-by-year delivery and cash-flow simulation
# Used by both the constant-rate and the ramp scenarios
# --------------------------------------------------

def simulate_years(
    monthly_rate_by_year,
    margin_per_aircraft,
    supply_chain_availability,
    inventory_cost_per_aircraft,
    production_cost_per_aircraft,
    baseline_monthly_rate,
    demand_case="base",
):
    demand_plan = get_demand_plan(demand_case)

    beginning_inventory = 0
    beginning_backlog = reported["a320_backlog_2025"]

    annual_results = []

    for year, monthly_rate in monthly_rate_by_year.items():

        production_capacity = annual_production(
            monthly_rate=monthly_rate,
            supply_chain_availability=supply_chain_availability,
        )

        delivery_demand = demand_plan[year]["delivery_demand"]
        new_orders = demand_plan[year]["new_orders"]

        # Production is capped at what can be delivered, so capacity
        # above deliverable demand stays idle instead of building stock.
        production = planned_production(
            production_capacity=production_capacity,
            beginning_inventory=beginning_inventory,
            beginning_backlog=beginning_backlog,
            new_orders=new_orders,
            delivery_demand=delivery_demand,
        )

        deliveries, ending_inventory, ending_backlog = annual_delivery_flow(
            annual_production=production,
            beginning_inventory=beginning_inventory,
            beginning_backlog=beginning_backlog,
            new_orders=new_orders,
            delivery_demand=delivery_demand,
        )

        # Without the investment, the existing factories face the same
        # supply ceiling. Gains are measured against what they deliver.
        baseline_deliveries = baseline_annual_deliveries(
            baseline_monthly_rate=baseline_monthly_rate,
            supply_ceiling=production_capacity,
            delivery_demand=delivery_demand,
        )

        incremental_deliveries = (
            deliveries
            - baseline_deliveries
        )

        annual_profit_gain = incremental_annual_profit(
            incremental_deliveries=incremental_deliveries,
            incremental_margin_per_aircraft=margin_per_aircraft,
        )

        inventory_cost = inventory_holding_cost(
            beginning_inventory=beginning_inventory,
            ending_inventory=ending_inventory,
            inventory_cost_per_aircraft=inventory_cost_per_aircraft,
        )

        # Aircraft built but not delivered cost their full production
        # cost in the year they are built. Without this, overproduction
        # would only cost the small annual holding charge.
        inventory_build_cost = inventory_build_cash_flow(
            beginning_inventory=beginning_inventory,
            ending_inventory=ending_inventory,
            production_cost_per_aircraft=production_cost_per_aircraft,
        )

        operating_cash_flow = (
            annual_profit_gain
            - inventory_cost
            - inventory_build_cost
        )

        annual_results.append({
            "year": year,
            "monthly_rate": monthly_rate,
            "production_capacity": production_capacity,
            "production": production,
            "delivery_demand": delivery_demand,
            "new_orders": new_orders,
            "deliveries": deliveries,
            "baseline_deliveries": baseline_deliveries,
            "ending_inventory": ending_inventory,
            "ending_backlog": ending_backlog,
            "incremental_deliveries": incremental_deliveries,
            "profit_gain": annual_profit_gain,
            "inventory_cost": inventory_cost,
            "inventory_build_cost": inventory_build_cost,
            "operating_cash_flow": operating_cash_flow,
        })

        beginning_inventory = ending_inventory
        beginning_backlog = ending_backlog

    return annual_results


# --------------------------------------------------
# Improved constant-rate scenario
# Used for production-rate sensitivity
# --------------------------------------------------

def evaluate_rate_scenario(
    monthly_rate,
    margin_per_aircraft,
    ramp_investment,
    discount_rate,
    project_life_years,
    supply_chain_availability,
    inventory_cost_per_aircraft,
    capex_scaling_exponent,
    production_cost_per_aircraft,
    baseline_monthly_rate,
    extended_life_years=0,
    demand_case="base",
):
    base_monthly_rate = baseline_monthly_rate
    reference_target_rate = reported["target_monthly_rate_high"]

    actual_ramp_investment = capacity_dependent_investment(
        target_monthly_rate=monthly_rate,
        base_monthly_rate=base_monthly_rate,
        reference_target_rate=reference_target_rate,
        reference_investment=ramp_investment,
        capex_scaling_exponent=capex_scaling_exponent,
    )

    years = list(get_demand_plan().keys())[:int(project_life_years)]

    annual_results = simulate_years(
        monthly_rate_by_year={year: monthly_rate for year in years},
        margin_per_aircraft=margin_per_aircraft,
        supply_chain_availability=supply_chain_availability,
        inventory_cost_per_aircraft=inventory_cost_per_aircraft,
        production_cost_per_aircraft=production_cost_per_aircraft,
        baseline_monthly_rate=baseline_monthly_rate,
        demand_case=demand_case,
    )

    annual_cash_flows = [
        row["operating_cash_flow"]
        for row in annual_results
    ]

    project_npv = npv(
        initial_investment=actual_ramp_investment,
        annual_cash_flows=annual_cash_flows,
        discount_rate=discount_rate,
    )

    extension = extension_value(
        final_cash_flow=annual_cash_flows[-1],
        discount_rate=discount_rate,
        modelled_years=len(annual_cash_flows),
        extension_years=extended_life_years,
    )

    return {
        "monthly_rate": monthly_rate,
        "ramp_investment": actual_ramp_investment,
        "npv": project_npv,
        "extension_value": extension,
        "npv_with_extension": project_npv + extension,
        "ending_inventory": annual_results[-1]["ending_inventory"],
        "ending_backlog": annual_results[-1]["ending_backlog"],
        "total_deliveries": sum(
            row["deliveries"] for row in annual_results
        ),
        "total_inventory_cost": sum(
            row["inventory_cost"] for row in annual_results
        ),
        "total_inventory_build_cost": sum(
            row["inventory_build_cost"] for row in annual_results
        ),
    }


# --------------------------------------------------
# Production-ramp scenario
# Capacity investment is phased over the ramp, and
# year-on-year rate increases above the comfortable
# step incur an expedite cost
# --------------------------------------------------

def evaluate_ramp_scenario(
    ramp_case,
    margin_per_aircraft,
    ramp_investment,
    discount_rate,
    supply_chain_availability,
    inventory_cost_per_aircraft,
    capex_scaling_exponent,
    production_cost_per_aircraft,
    comfortable_annual_rate_step,
    expedite_premium,
    baseline_monthly_rate,
    extended_life_years=0,
    demand_case="base",
    production_ramp=None,
    investment_ramp=None,
):
    # By default the scenario uses the named ramp, and investment
    # follows the same ramp. Passing a separate investment ramp models
    # capacity that is paid for on one schedule but used on another.
    if production_ramp is None:
        production_ramp = get_production_ramp(ramp_case)

    if investment_ramp is None:
        investment_ramp = production_ramp

    investment_schedule = phased_capacity_investment(
        production_ramp=investment_ramp,
        base_monthly_rate=baseline_monthly_rate,
        reference_target_rate=reported["target_monthly_rate_high"],
        reference_investment=ramp_investment,
        capex_scaling_exponent=capex_scaling_exponent,
        comfortable_annual_rate_step=comfortable_annual_rate_step,
        expedite_premium=expedite_premium,
    )

    # Capacity that comes online in a given year is paid for at the end
    # of the previous year. The first year's capacity is paid at time zero.
    investment_spend = [
        step["capex"] + step["expedite_cost"]
        for step in investment_schedule
    ]

    upfront_investment = investment_spend[0]

    annual_results = simulate_years(
        monthly_rate_by_year=production_ramp,
        margin_per_aircraft=margin_per_aircraft,
        supply_chain_availability=supply_chain_availability,
        inventory_cost_per_aircraft=inventory_cost_per_aircraft,
        production_cost_per_aircraft=production_cost_per_aircraft,
        baseline_monthly_rate=baseline_monthly_rate,
        demand_case=demand_case,
    )

    annual_cash_flows = []

    for index, row in enumerate(annual_results):

        if index + 1 < len(investment_spend):
            capacity_investment = investment_spend[index + 1]
        else:
            capacity_investment = 0

        row["capacity_investment"] = capacity_investment

        row["net_cash_flow"] = (
            row["operating_cash_flow"]
            - capacity_investment
        )

        annual_cash_flows.append(row["net_cash_flow"])

    project_npv = npv(
        initial_investment=upfront_investment,
        annual_cash_flows=annual_cash_flows,
        discount_rate=discount_rate,
    )

    # Value of the capacity continuing to earn after the modelled
    # period. By the final year the investment is complete, so the
    # final year's cash flow is the steady-state level.
    extension = extension_value(
        final_cash_flow=annual_cash_flows[-1],
        discount_rate=discount_rate,
        modelled_years=len(annual_cash_flows),
        extension_years=extended_life_years,
    )

    # Payback year: the first year in which cumulative cash flow is
    # positive and stays positive to the end of the modelled period
    payback_year = None
    cumulative_cash_flow = -upfront_investment

    for row in annual_results:
        cumulative_cash_flow += row["net_cash_flow"]

        if cumulative_cash_flow < 0:
            payback_year = None
        elif payback_year is None:
            payback_year = row["year"]

    return {
        "annual_results": pd.DataFrame(
            annual_results
        ),
        "ramp_investment": sum(investment_spend),
        "upfront_investment": upfront_investment,
        "capex": sum(
            step["capex"] for step in investment_schedule
        ),
        "expedite_cost": sum(
            step["expedite_cost"] for step in investment_schedule
        ),
        "npv": project_npv,
        "extension_value": extension,
        "npv_with_extension": project_npv + extension,
        "payback_year": payback_year,
    }


# --------------------------------------------------
# Ramp cases
# --------------------------------------------------

def run_ramp_case(
    ramp_case,
    assumptions,
    demand_case="base",
    production_ramp=None,
    investment_ramp=None,
):
    return evaluate_ramp_scenario(
        ramp_case=ramp_case,
        margin_per_aircraft=assumptions["incremental_margin_per_aircraft"],
        ramp_investment=assumptions["ramp_investment"],
        discount_rate=assumptions["discount_rate"],
        supply_chain_availability=assumptions["supply_chain_availability"],
        inventory_cost_per_aircraft=assumptions["inventory_cost_per_aircraft"],
        capex_scaling_exponent=assumptions["capex_scaling_exponent"],
        production_cost_per_aircraft=assumptions["production_cost_per_aircraft"],
        comfortable_annual_rate_step=assumptions["comfortable_annual_rate_step"],
        expedite_premium=assumptions["expedite_premium"],
        baseline_monthly_rate=assumptions["baseline_monthly_rate"],
        extended_life_years=assumptions["extended_life_years"],
        demand_case=demand_case,
        production_ramp=production_ramp,
        investment_ramp=investment_ramp,
    )


def ramp_cases():
    assumptions = load_assumptions("base")

    results = {}

    for ramp_case in RAMP_LABELS:
        results[ramp_case] = run_ramp_case(
            ramp_case,
            assumptions,
        )

    return results


# --------------------------------------------------
# Delays of the Airbus target case
#
# Planned delay:   Airbus chooses to ramp later, so the
#                  investment is deferred along with it
# Unplanned delay: Airbus invests on the target schedule,
#                  but the capacity cannot be used until
#                  later, for example because suppliers
#                  are not ready
# --------------------------------------------------

def delay_cases():
    assumptions = load_assumptions("base")

    target_ramp = get_production_ramp(TARGET_CASE)
    target_rate = reported["target_monthly_rate_high"]

    rows = []

    for delay_years in [0] + DELAY_YEARS:
        delayed_ramp = get_delayed_ramp(delay_years)

        planned = run_ramp_case(
            TARGET_CASE,
            assumptions,
            production_ramp=delayed_ramp,
        )

        unplanned = run_ramp_case(
            TARGET_CASE,
            assumptions,
            production_ramp=delayed_ramp,
            investment_ramp=target_ramp,
        )

        rows.append({
            "delay_years": delay_years,
            "first_full_year_at_target_rate": first_full_year_at_rate(
                delayed_ramp,
                target_rate,
            ),
            "planned_npv": planned["npv"],
            "planned_npv_with_extension": planned["npv_with_extension"],
            "unplanned_npv": unplanned["npv"],
            "unplanned_npv_with_extension": unplanned["npv_with_extension"],
        })

    return pd.DataFrame(rows)


# --------------------------------------------------
# Combined downside / base / upside cases
# Each runs the Airbus target case with every
# assumption, including delivery demand, at its
# downside, base, or upside value
# --------------------------------------------------

def standard_cases():
    cases = {}

    for case_name in ["downside", "base", "upside"]:
        cases[case_name] = run_ramp_case(
            TARGET_CASE,
            load_assumptions(case_name),
            demand_case=case_name,
        )

    return cases


# --------------------------------------------------
# Improved production-rate sensitivity
# --------------------------------------------------

def rate_sensitivity(demand_case="base"):
    assumptions = load_assumptions("base")

    rows = []

    for monthly_rate in get_rate_sensitivity():
        result = evaluate_rate_scenario(
            monthly_rate=monthly_rate,
            margin_per_aircraft=assumptions["incremental_margin_per_aircraft"],
            ramp_investment=assumptions["ramp_investment"],
            discount_rate=assumptions["discount_rate"],
            project_life_years=assumptions["project_life_years"],
            supply_chain_availability=assumptions["supply_chain_availability"],
            inventory_cost_per_aircraft=assumptions["inventory_cost_per_aircraft"],
            capex_scaling_exponent=assumptions["capex_scaling_exponent"],
            production_cost_per_aircraft=assumptions["production_cost_per_aircraft"],
            baseline_monthly_rate=assumptions["baseline_monthly_rate"],
            extended_life_years=assumptions["extended_life_years"],
            demand_case=demand_case,
        )

        rows.append(result)

    return pd.DataFrame(rows)


# --------------------------------------------------
# Run analysis
# --------------------------------------------------

if __name__ == "__main__":

    print("COMBINED CASES (Airbus target case, all assumptions at downside / base / upside)")
    print("=" * 60)

    for case_name, result in standard_cases().items():
        final_year = result["annual_results"].iloc[-1]

        print(f"\n{case_name.upper()}")
        print(
            f"Deliveries in {final_year['year']:.0f}: "
            f"{final_year['deliveries']:.0f}"
        )
        print(f"Capacity investment: €{result['capex']:,.0f}m")
        print(f"Expedite cost: €{result['expedite_cost']:,.0f}m")
        print(f"NPV, 2026-2035: €{result['npv']:,.0f}m")
        print(
            f"NPV including extended life: "
            f"€{result['npv_with_extension']:,.0f}m"
        )

        if result["payback_year"] is None:
            print("Cumulative cash flow turns positive: not within horizon")
        else:
            print(
                f"Cumulative cash flow turns positive: "
                f"{result['payback_year']:.0f}"
            )


    print()
    print("RATE SENSITIVITY")
    print("=" * 60)
    print(rate_sensitivity().to_string(index=False))


    print()
    print("RAMP SCENARIOS")
    print("=" * 70)

    for ramp_case, result in ramp_cases().items():
        print()
        print(RAMP_LABELS[ramp_case].upper())

        print(
            result["annual_results"].to_string(
                index=False
            )
        )

        print(
            f"Capacity investment: "
            f"€{result['capex']:,.0f} million "
            f"(€{result['upfront_investment']:,.0f} million at time zero)"
        )

        print(
            f"Expedite cost: "
            f"€{result['expedite_cost']:,.0f} million"
        )

        print(
            f"NPV, 2026-2035: "
            f"€{result['npv']:,.0f} million"
        )

        print(
            f"NPV including extended life: "
            f"€{result['npv_with_extension']:,.0f} million"
        )


    print()
    print("DELAYS OF THE AIRBUS TARGET CASE (NPV in EUR million)")
    print("=" * 70)
    print(delay_cases().round(0).to_string(index=False))
