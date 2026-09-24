# Only has to be run once to generate the fixed plots for the report. The plots are saved in the outputs folder.

import os

import matplotlib.pyplot as plt
import pandas as pd

os.makedirs("outputs", exist_ok=True)


# --------------------------------------------------
# Plot: Historical A320-family deliveries
# --------------------------------------------------

history = pd.read_csv(
    "data/a320_deliveries_history.csv"
)

plt.figure(figsize=(10, 5))

plt.plot(
    history["year"],
    history["a320_family_deliveries"],
    marker="o",
)

plt.title("Airbus A320 Family Deliveries")
plt.xlabel("Year")
plt.ylabel("Aircraft Delivered")

plt.xticks(
    history["year"],
    rotation=45,
    ha="center",
)

plt.tight_layout()

plt.savefig(
    "outputs/a320_historical_deliveries.png",
    dpi=300,
    bbox_inches="tight",
)


# --------------------------------------------------
# Plot: Quarterly A320-family deliveries
# --------------------------------------------------

quarterly = pd.read_csv(
    "data/a320_quarterly_deliveries.csv"
)

plt.figure(figsize=(10, 5))

plt.bar(
    quarterly["quarter"],
    quarterly["a320_family_deliveries"],
)

plt.title("Airbus A320 Family Quarterly Deliveries")
plt.xlabel("Quarter")
plt.ylabel("Aircraft Delivered")

plt.xticks(
    rotation=45,
    ha="center",
)

plt.tight_layout()

plt.savefig(
    "outputs/a320_quarterly_deliveries.png",
    dpi=300,
    bbox_inches="tight",
)


plt.close("all")
