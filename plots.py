import os

import matplotlib.pyplot as plt
import pandas as pd

from model import load_assumptions, load_input_values
from scenarios import (
    evaluate_rate_scenario,
    ramp_cases,
    rate_sensitivity,
)

reported = load_input_values()
base_assumptions = load_assumptions("base")

os.makedirs("outputs", exist_ok=True)


# --------------------------------------------------
# Plot: NPV vs production rate
# Improved model
# --------------------------------------------------

rate_df = rate_sensitivity()

plt.figure(figsize=(8, 5))

plt.plot(
    rate_df["monthly_rate"],
    rate_df["npv"],
    marker="o",
)

plt.axhline(0, linewidth=1)

plt.title("NPV vs Monthly A320 Production Rate")
plt.xlabel("Monthly Production Rate")
plt.ylabel("NPV (€ million)")

plt.tight_layout()

plt.savefig(
    "outputs/npv_vs_production_rate.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()


# --------------------------------------------------
# Plot: NPV sensitivity to margin per aircraft
# Improved model
# --------------------------------------------------

monthly_rate = reported["target_monthly_rate_high"]

margins = [3, 5, 8, 10, 12]
margin_npvs = []

for margin in margins:

    result = evaluate_rate_scenario(
        monthly_rate=monthly_rate,
        margin_per_aircraft=margin,
        ramp_investment=base_assumptions["ramp_investment"],
        discount_rate=base_assumptions["discount_rate"],
        project_life_years=base_assumptions["project_life_years"],
        supply_chain_availability=base_assumptions["supply_chain_availability"],
        inventory_cost_per_aircraft=base_assumptions["inventory_cost_per_aircraft"],
        capex_scaling_exponent=base_assumptions["capex_scaling_exponent"],
    )

    margin_npvs.append(result["npv"])

plt.figure(figsize=(8, 5))

plt.plot(
    margins,
    margin_npvs,
    marker="o",
)

plt.axhline(0, linewidth=1)

plt.title("NPV Sensitivity to Incremental Margin per Aircraft")
plt.xlabel("Incremental Margin per Aircraft (€ million)")
plt.ylabel("NPV (€ million)")

plt.tight_layout()

plt.savefig(
    "outputs/npv_vs_margin.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()


# --------------------------------------------------
# Plot: NPV sensitivity to supply-chain availability
# Improved model
# --------------------------------------------------

availability_levels = [x / 100 for x in range(50, 101, 5)]

availability_npvs = []

for availability in availability_levels:

    result = evaluate_rate_scenario(
        monthly_rate=monthly_rate,
        margin_per_aircraft=base_assumptions["incremental_margin_per_aircraft"],
        ramp_investment=base_assumptions["ramp_investment"],
        discount_rate=base_assumptions["discount_rate"],
        project_life_years=base_assumptions["project_life_years"],
        supply_chain_availability=availability,
        inventory_cost_per_aircraft=base_assumptions["inventory_cost_per_aircraft"],
        capex_scaling_exponent=base_assumptions["capex_scaling_exponent"],
    )

    availability_npvs.append(result["npv"])

plt.figure(figsize=(8, 5))

plt.plot(
    [x * 100 for x in availability_levels],
    availability_npvs,
    marker="o",
)

plt.axhline(0, linewidth=1)

plt.title("NPV Sensitivity to Supply-Chain Availability")
plt.xlabel("Supply-Chain Availability (%)")
plt.ylabel("NPV (€ million)")

plt.tight_layout()

plt.savefig(
    "outputs/npv_vs_supply_chain_availability.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()


# --------------------------------------------------
# Plot: NPV comparison by ramp scenario
# --------------------------------------------------

ramp_results = ramp_cases()

ramp_names = []
ramp_npvs = []

for ramp_case, result in ramp_results.items():
    ramp_names.append(ramp_case.capitalize())
    ramp_npvs.append(result["npv"])

plt.figure(figsize=(8, 5))

plt.bar(
    ramp_names,
    ramp_npvs,
)

plt.axhline(0, linewidth=1)

plt.title("NPV by A320 Production Ramp Scenario")
plt.xlabel("Ramp Scenario")
plt.ylabel("NPV (€ million)")

plt.tight_layout()

plt.savefig(
    "outputs/npv_by_ramp_scenario.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()


# --------------------------------------------------
# Plot: Base-ramp production, deliveries and inventory
# --------------------------------------------------

base_ramp_df = ramp_results["base"]["annual_results"]

plt.figure(figsize=(8, 5))

plt.plot(
    base_ramp_df["year"],
    base_ramp_df["production"],
    marker="o",
    label="Production",
)

plt.plot(
    base_ramp_df["year"],
    base_ramp_df["deliveries"],
    marker="o",
    label="Deliveries",
)

plt.plot(
    base_ramp_df["year"],
    base_ramp_df["ending_inventory"],
    marker="o",
    label="Ending Inventory",
)

plt.plot(
    base_ramp_df["year"],
    base_ramp_df["delivery_demand"],
    marker="o",
    label="Delivery Demand",
)

plt.title("Base Ramp: Production, Deliveries and Inventory")
plt.xlabel("Year")
plt.ylabel("Aircraft")

plt.legend()

plt.tight_layout()

plt.savefig(
    "outputs/base_ramp_production_deliveries_inventory.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()


# --------------------------------------------------
# Show all figures
# --------------------------------------------------

# Uncomment this, and comment out plt.close() if you want all figures to open:
# plt.show()
