# Generates the figures based only on historical Airbus data.
# These only need to be re-run when the data files change.
# Run with: python fixed_plots.py
#
# Figures are saved in the outputs folder:
#   a320_historical_deliveries.png
#   a320_quarterly_deliveries.png

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from plot_style import (
    COLOR_PRIMARY,
    COLOR_TEXT,
    OUTPUT_DIR,
    add_titles,
    mark_point,
    new_figure,
    save_figure,
)

DATA_DIR = Path(__file__).parent / "data"

HISTORY_SOURCE_NOTE = (
    "Source: Airbus reported A320-family deliveries."
)

QUARTERLY_SOURCE_NOTE = (
    "Source: Airbus quarterly results. Q2 to Q4 derived from "
    "cumulative reported deliveries."
)

COLOR_DE_EMPHASIZED = "#c5c4be"


# --------------------------------------------------
# Figure: Historical A320-family deliveries
# --------------------------------------------------

def plot_historical_deliveries():
    history = pd.read_csv(
        DATA_DIR / "a320_deliveries_history.csv"
    )

    years = history["year"]
    deliveries = history["a320_family_deliveries"]

    peak_index = deliveries.idxmax()
    peak_year = years[peak_index]
    peak_value = deliveries[peak_index]

    latest_year = years.iloc[-1]
    latest_value = deliveries.iloc[-1]

    # Lowest year after the peak
    after_peak = history[history["year"] > peak_year]

    fig, ax = new_figure()

    ax.plot(years, deliveries, color=COLOR_PRIMARY)

    mark_point(ax, peak_year, peak_value)

    ax.annotate(
        f"{peak_year}: {peak_value}",
        xy=(peak_year, peak_value),
        xytext=(-8, 6),
        textcoords="offset points",
        ha="right",
        va="bottom",
        color=COLOR_TEXT,
        fontsize=9,
    )

    if not after_peak.empty:
        low_index = after_peak["a320_family_deliveries"].idxmin()
        low_year = years[low_index]
        low_value = deliveries[low_index]

        mark_point(ax, low_year, low_value)

        ax.annotate(
            f"{low_year}: {low_value}",
            xy=(low_year, low_value),
            xytext=(8, -6),
            textcoords="offset points",
            ha="left",
            va="top",
            color=COLOR_TEXT,
            fontsize=9,
        )

        mark_point(ax, latest_year, latest_value)

        ax.annotate(
            f"{latest_year}: {latest_value}",
            xy=(latest_year, latest_value),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            va="bottom",
            color=COLOR_TEXT,
            fontsize=9,
        )

    ax.set_ylim(bottom=0, top=peak_value * 1.12)
    ax.set_xlabel("Year")
    ax.set_ylabel("Aircraft delivered per year")

    if latest_value < peak_value:
        headline = (
            f"A320-family deliveries have not yet recovered "
            f"their {peak_year} peak"
        )
    else:
        headline = (
            f"A320-family deliveries reached a record "
            f"{latest_value} in {latest_year}"
        )

    add_titles(
        fig,
        headline=headline,
        subtitle=(
            f"Annual Airbus A320-family deliveries, "
            f"{years.iloc[0]} to {latest_year}"
        ),
    )

    save_figure(
        fig,
        "a320_historical_deliveries.png",
        source_note=HISTORY_SOURCE_NOTE,
    )


# --------------------------------------------------
# Figure: Quarterly A320-family deliveries
# --------------------------------------------------

def plot_quarterly_deliveries():
    quarterly = pd.read_csv(
        DATA_DIR / "a320_quarterly_deliveries.csv"
    )

    # Quarter labels look like "Q1 2021"
    quarter_names = quarterly["quarter"].str.split(" ").str[0]
    quarter_years = quarterly["quarter"].str.split(" ").str[1]

    deliveries = quarterly["a320_family_deliveries"]
    is_fourth_quarter = quarter_names == "Q4"

    positions = range(len(quarterly))

    fig, ax = new_figure()

    ax.bar(
        positions,
        deliveries,
        width=0.6,
        color=[
            COLOR_PRIMARY if fourth else COLOR_DE_EMPHASIZED
            for fourth in is_fourth_quarter
        ],
    )

    for position, value, fourth in zip(
        positions, deliveries, is_fourth_quarter
    ):
        if fourth:
            ax.annotate(
                f"{value}",
                xy=(position, value),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                color=COLOR_TEXT,
                fontsize=9,
            )

    # Show the year once, under the first quarter of each year
    ax.set_xticks(list(positions))
    ax.set_xticklabels(
        [
            f"{name}\n{year}" if name == "Q1" else name
            for name, year in zip(quarter_names, quarter_years)
        ],
        fontsize=8,
    )

    ax.set_ylim(top=deliveries.max() * 1.12)
    ax.set_ylabel("Aircraft delivered per quarter")

    ax.legend(
        handles=[
            plt.Rectangle((0, 0), 1, 1, color=COLOR_PRIMARY),
            plt.Rectangle((0, 0), 1, 1, color=COLOR_DE_EMPHASIZED),
        ],
        labels=[
            "Fourth quarter",
            "Other quarters",
        ],
        loc="upper left",
        ncol=2,
        fontsize=9,
    )

    strongest_quarter_by_year = (
        quarterly.assign(name=quarter_names, year=quarter_years)
        .sort_values("a320_family_deliveries")
        .groupby("year")
        .tail(1)["name"]
    )

    if (strongest_quarter_by_year == "Q4").all():
        headline = (
            "Deliveries are back-loaded: the fourth quarter "
            "is the strongest in every year"
        )
    else:
        headline = "Deliveries are concentrated in the fourth quarter"

    add_titles(
        fig,
        headline=headline,
        subtitle=(
            f"Quarterly Airbus A320-family deliveries, "
            f"{quarter_years.iloc[0]} to {quarter_years.iloc[-1]}"
        ),
    )

    save_figure(
        fig,
        "a320_quarterly_deliveries.png",
        source_note=QUARTERLY_SOURCE_NOTE,
    )


def main():
    plot_historical_deliveries()
    plot_quarterly_deliveries()

    print(f"Figures saved in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
