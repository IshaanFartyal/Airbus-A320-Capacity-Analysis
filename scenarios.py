import pandas as pd

from demand import get_demand_plan
from financial_analysis import npv, payback_period
from model import (
    annual_delivery_flow,
    annual_production,
    capacity_dependent_investment,
    incremental_annual_deliveries,
    incremental_annual_profit,
    inventory_holding_cost,
    load_assumptions,
    load_input_values,
)
from production_plan import get_production_ramp, get_rate_sensitivity

reported = load_input_values()


# --------------------------------------------------
# Original simplified constant-rate scenario
# --------------------------------------------------

def evaluate_scenario(
    monthly_rate,
    margin_per_aircraft,
    ramp_investment,
    discount_rate,
    project_life_years,
    supply_chain_availability,
    demand_utilization,
):
    base_annual_deliveries = reported["a320_2025_deliveries"]

    incremental_deliveries = incremental_annual_deliveries(
        target_monthly_rate=monthly_rate,
        base_annual_deliveries=base_annual_deliveries,
        supply_chain_availability=supply_chain_availability,
        demand_utilization=demand_utilization,
    )

    annual_profit_gain = incremental_annual_profit(
        incremental_deliveries=incremental_deliveries,
        incremental_margin_per_aircraft=margin_per_aircraft,
    )

    annual_cash_flows = [
        annual_profit_gain
        for _ in range(int(project_life_years))
    ]

    project_npv = npv(
        initial_investment=ramp_investment,
        annual_cash_flows=annual_cash_flows,
        discount_rate=discount_rate,
    )

    payback = payback_period(
        initial_investment=ramp_investment,
        annual_incremental_profit=annual_profit_gain,
    )

    return {
        "monthly_rate": monthly_rate,
        "incremental_deliveries": incremental_deliveries,
        "annual_profit_gain": annual_profit_gain,
        "npv": project_npv,
        "payback_years": payback,
    }


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
):
    base_annual_deliveries = reported["a320_2025_deliveries"]
    base_monthly_rate = reported["a320_monthly_2025_average"]
    reference_target_rate = reported["target_monthly_rate_high"]

    demand_plan = get_demand_plan()

    actual_ramp_investment = capacity_dependent_investment(
        target_monthly_rate=monthly_rate,
        base_monthly_rate=base_monthly_rate,
        reference_target_rate=reference_target_rate,
        reference_investment=ramp_investment,
        capex_scaling_exponent=capex_scaling_exponent,
    )

    beginning_inventory = 0
    beginning_backlog = reported["a320_backlog_2025"]

    annual_cash_flows = []
    total_deliveries = 0
    total_inventory_cost = 0

    years = list(demand_plan.keys())[:int(project_life_years)]

    for year in years:

        production = annual_production(
            monthly_rate=monthly_rate,
            supply_chain_availability=supply_chain_availability,
            demand_utilization=1.0,
        )

        delivery_demand = demand_plan[year]["delivery_demand"]
        new_orders = demand_plan[year]["new_orders"]

        deliveries, ending_inventory, ending_backlog = annual_delivery_flow(
            annual_production=production,
            beginning_inventory=beginning_inventory,
            beginning_backlog=beginning_backlog,
            new_orders=new_orders,
            delivery_demand=delivery_demand,
        )

        incremental_deliveries = (
            deliveries
            - base_annual_deliveries
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

        annual_cash_flow = (
            annual_profit_gain
            - inventory_cost
        )

        annual_cash_flows.append(annual_cash_flow)

        total_deliveries += deliveries
        total_inventory_cost += inventory_cost

        beginning_inventory = ending_inventory
        beginning_backlog = ending_backlog

    project_npv = npv(
        initial_investment=actual_ramp_investment,
        annual_cash_flows=annual_cash_flows,
        discount_rate=discount_rate,
    )

    return {
        "monthly_rate": monthly_rate,
        "ramp_investment": actual_ramp_investment,
        "npv": project_npv,
        "ending_inventory": beginning_inventory,
        "ending_backlog": beginning_backlog,
        "total_deliveries": total_deliveries,
        "total_inventory_cost": total_inventory_cost,
    }


# --------------------------------------------------
# Production-ramp scenario
# --------------------------------------------------

def evaluate_ramp_scenario(
    ramp_case,
    margin_per_aircraft,
    ramp_investment,
    discount_rate,
    supply_chain_availability,
    inventory_cost_per_aircraft,
    capex_scaling_exponent,
):
    production_ramp = get_production_ramp(ramp_case)
    demand_plan = get_demand_plan()

    base_annual_deliveries = reported[
        "a320_2025_deliveries"
    ]

    base_monthly_rate = reported[
        "a320_monthly_2025_average"
    ]

    reference_target_rate = reported[
        "target_monthly_rate_high"
    ]

    target_monthly_rate = max(
        production_ramp.values()
    )

    actual_ramp_investment = capacity_dependent_investment(
        target_monthly_rate=target_monthly_rate,
        base_monthly_rate=base_monthly_rate,
        reference_target_rate=reference_target_rate,
        reference_investment=ramp_investment,
        capex_scaling_exponent=capex_scaling_exponent,
    )

    annual_results = []
    annual_cash_flows = []

    beginning_inventory = 0

    beginning_backlog = reported[
        "a320_backlog_2025"
    ]

    for year, monthly_rate in production_ramp.items():

        production = annual_production(
            monthly_rate=monthly_rate,
            supply_chain_availability=supply_chain_availability,
            demand_utilization=1.0,
        )

        delivery_demand = demand_plan[
            year
        ]["delivery_demand"]

        new_orders = demand_plan[
            year
        ]["new_orders"]

        deliveries, ending_inventory, ending_backlog = (
            annual_delivery_flow(
                annual_production=production,
                beginning_inventory=beginning_inventory,
                beginning_backlog=beginning_backlog,
                new_orders=new_orders,
                delivery_demand=delivery_demand,
            )
        )

        incremental_deliveries = (
            deliveries
            - base_annual_deliveries
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

        annual_cash_flow = (
            annual_profit_gain
            - inventory_cost
        )

        annual_cash_flows.append(
            annual_cash_flow
        )

        annual_results.append({
            "year": year,
            "monthly_rate": monthly_rate,
            "production": production,
            "delivery_demand": delivery_demand,
            "new_orders": new_orders,
            "deliveries": deliveries,
            "ending_inventory": ending_inventory,
            "ending_backlog": ending_backlog,
            "incremental_deliveries": incremental_deliveries,
            "profit_gain": annual_profit_gain,
            "inventory_cost": inventory_cost,
            "net_cash_flow": annual_cash_flow,
        })

        beginning_inventory = ending_inventory
        beginning_backlog = ending_backlog

    project_npv = npv(
        initial_investment=actual_ramp_investment,
        annual_cash_flows=annual_cash_flows,
        discount_rate=discount_rate,
    )

    return {
        "annual_results": pd.DataFrame(
            annual_results
        ),
        "ramp_investment": actual_ramp_investment,
        "npv": project_npv,
    }


# --------------------------------------------------
# Ramp cases
# --------------------------------------------------

def ramp_cases():
    assumptions = load_assumptions("base")

    results = {}

    for ramp_case in ["slow", "base", "fast"]:
        result = evaluate_ramp_scenario(
            ramp_case=ramp_case,
            margin_per_aircraft=assumptions[
                "incremental_margin_per_aircraft"
            ],
            ramp_investment=assumptions[
                "ramp_investment"
            ],
            discount_rate=assumptions[
                "discount_rate"
            ],
            supply_chain_availability=assumptions[
                "supply_chain_availability"
            ],
            inventory_cost_per_aircraft=assumptions[
                "inventory_cost_per_aircraft"
            ],
            capex_scaling_exponent=assumptions[
                "capex_scaling_exponent"
            ],
        )

        results[ramp_case] = result

    return results


# --------------------------------------------------
# Standard low / base / high cases
# --------------------------------------------------

def standard_cases():
    cases = {}

    for case_name in ["low", "base", "high"]:
        assumptions = load_assumptions(case_name)

        result = evaluate_scenario(
            monthly_rate=reported["target_monthly_rate_high"],
            margin_per_aircraft=assumptions["incremental_margin_per_aircraft"],
            ramp_investment=assumptions["ramp_investment"],
            discount_rate=assumptions["discount_rate"],
            project_life_years=assumptions["project_life_years"],
            supply_chain_availability=assumptions["supply_chain_availability"],
            demand_utilization=assumptions["demand_utilization"],
        )

        cases[case_name] = result

    return cases


# --------------------------------------------------
# Improved production-rate sensitivity
# --------------------------------------------------

def rate_sensitivity():
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
        )

        rows.append(result)

    return pd.DataFrame(rows)


# --------------------------------------------------
# Run analysis
# --------------------------------------------------

if __name__ == "__main__":

    print("STANDARD CASES")
    print("=" * 60)

    for case_name, result in standard_cases().items():
        print(f"\n{case_name.upper()}")
        print(f"Monthly rate: {result['monthly_rate']:.0f}")
        print(f"Incremental annual deliveries: {result['incremental_deliveries']:.1f}")
        print(f"Annual incremental profit: €{result['annual_profit_gain']:,.1f}m")
        print(f"NPV: €{result['npv']:,.1f}m")

        if result["payback_years"] is None:
            print("Payback: No positive payback")
        else:
            print(f"Payback: {result['payback_years']:.2f} years")


    print()
    print("RATE SENSITIVITY")
    print("=" * 60)
    print(rate_sensitivity().to_string(index=False))


    print()
    print("RAMP SCENARIOS")
    print("=" * 70)

    for ramp_case, result in ramp_cases().items():
        print()
        print(ramp_case.upper())

        print(
            result["annual_results"].to_string(
                index=False
            )
        )

        print(
            f"Capacity investment: "
            f"€{result['ramp_investment']:,.0f} million"
        )

        print(
            f"Ramp NPV: "
            f"€{result['npv']:,.0f} million"
        )