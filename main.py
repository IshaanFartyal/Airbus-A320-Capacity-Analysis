from model import load_assumptions, load_input_values
from scenarios import evaluate_scenario

reported = load_input_values()
assumptions = load_assumptions("base")


result = evaluate_scenario(
    monthly_rate=reported["target_monthly_rate_high"],
    margin_per_aircraft=assumptions["incremental_margin_per_aircraft"],
    ramp_investment=assumptions["ramp_investment"],
    discount_rate=assumptions["discount_rate"],
    project_life_years=assumptions["project_life_years"],
    supply_chain_availability=assumptions["supply_chain_availability"],
    demand_utilization=assumptions["demand_utilization"],
)


print("AIRBUS A320 CAPACITY EXPANSION - BASE CASE")
print("=" * 60)

print(f"2025 A320-family deliveries: {reported['a320_2025_deliveries']:.0f}")
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
print(f"Incremental annual deliveries: {result['incremental_deliveries']:.1f}")
print(f"Annual incremental profit: €{result['annual_profit_gain']:,.1f}m")
print(f"Project NPV: €{result['npv']:,.1f}m")

if result["payback_years"] is None:
    print("Simple payback: No positive payback")
else:
    print(f"Simple payback: {result['payback_years']:.2f} years")

print()
print(
    "Important: Reported Airbus figures and model assumptions are stored "
    "separately in the data folder. The assumption values are not to be "
    "interpreted as official Airbus data or projections."
)
