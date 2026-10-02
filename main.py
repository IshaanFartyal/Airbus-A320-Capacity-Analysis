from model import load_assumptions, load_input_values
from scenarios import evaluate_rate_scenario, ramp_cases

reported = load_input_values()
assumptions = load_assumptions("base")


# Headline case: the base production ramp, with phased capacity
# investment, the demand plan, backlog and inventory effects.
ramp_results = ramp_cases()
base_ramp = ramp_results["base"]

# Reference case: constant rate 75 from the first year, with the
# full investment paid at time zero.
constant_rate = evaluate_rate_scenario(
    monthly_rate=reported["target_monthly_rate_high"],
    margin_per_aircraft=assumptions["incremental_margin_per_aircraft"],
    ramp_investment=assumptions["ramp_investment"],
    discount_rate=assumptions["discount_rate"],
    project_life_years=assumptions["project_life_years"],
    supply_chain_availability=assumptions["supply_chain_availability"],
    inventory_cost_per_aircraft=assumptions["inventory_cost_per_aircraft"],
    capex_scaling_exponent=assumptions["capex_scaling_exponent"],
    production_cost_per_aircraft=assumptions["production_cost_per_aircraft"],
    baseline_monthly_rate=assumptions["baseline_monthly_rate"],
)


print("AIRBUS A320 CAPACITY EXPANSION - BASE CASE")
print("=" * 60)

print(f"2025 A320-family deliveries: {reported['a320_2025_deliveries']:.0f}")
print(
    f"No-investment baseline rate assumption: "
    f"{assumptions['baseline_monthly_rate']:.0f} per month"
)
print(
    f"Target monthly production rate: "
    f"{reported['target_monthly_rate_high']:.0f}"
)
print(
    f"Supply-chain availability assumption: "
    f"{assumptions['supply_chain_availability']:.0%}"
)
print(
    f"Incremental margin assumption: "
    f"€{assumptions['incremental_margin_per_aircraft']:.1f}m per aircraft"
)
print(
    f"Ramp investment assumption: "
    f"€{assumptions['ramp_investment']:,.0f}m"
)

print()
print("BASE RAMP (headline case)")
print("-" * 60)

final_year = base_ramp["annual_results"].iloc[-1]

print(
    f"Deliveries in {final_year['year']:.0f}: "
    f"{final_year['deliveries']:.0f} "
    f"({final_year['incremental_deliveries']:+.0f} vs no-investment baseline)"
)
print(
    f"Capacity investment: €{base_ramp['capex']:,.0f}m "
    f"(€{base_ramp['upfront_investment']:,.0f}m at time zero, rest phased)"
)
print(f"Expedite cost: €{base_ramp['expedite_cost']:,.0f}m")
print(f"Project NPV: €{base_ramp['npv']:,.0f}m")

if base_ramp["payback_year"] is None:
    print("Cumulative cash flow turns positive: not within the model horizon")
else:
    print(
        f"Cumulative cash flow turns positive: "
        f"{base_ramp['payback_year']:.0f}"
    )

print()
print("RAMP COMPARISON")
print("-" * 60)

for ramp_case, result in ramp_results.items():
    print(
        f"{ramp_case.capitalize():<5} "
        f"NPV €{result['npv']:>7,.0f}m | "
        f"expedite cost €{result['expedite_cost']:>5,.0f}m"
    )

print()
print("REFERENCE: CONSTANT RATE 75 FROM YEAR ONE")
print("-" * 60)
print(f"Project NPV: €{constant_rate['npv']:,.0f}m")
print(
    "This assumes the full rate is available immediately and all "
    "investment is paid at time zero, so it overstates the base ramp."
)

print()
print(
    "Important: Reported Airbus figures and model assumptions are stored "
    "separately in the data folder. The assumption values are not to be "
    "interpreted as official Airbus data or projections."
)
