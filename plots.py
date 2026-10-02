# Generates the model-dependent figures for the report.
# Run with: python plots.py
#
# Figures are saved in the outputs folder:
#   ramp_paths.png
#   target_case_deliveries_vs_demand.png
#   target_case_cumulative_cash_flow.png
#   npv_by_ramp_scenario.png
#   npv_by_delay_unplanned.png
#   npv_by_delay.png
#   npv_slower_ramp_vs_delay.png
#   npv_vs_production_rate.png
#   npv_vs_production_rate_by_demand.png
#   npv_tornado.png
#   npv_vs_supply_chain_availability.png
#   npv_vs_supply_chain_availability_simple.png

import matplotlib.pyplot as plt

from model import load_assumptions, load_input_values
from plot_style import (
    COLOR_PRIMARY,
    COLOR_PRIMARY_LIGHT,
    COLOR_QUATERNARY,
    COLOR_REFERENCE,
    COLOR_SECONDARY,
    COLOR_TERTIARY,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    OUTPUT_DIR,
    add_titles,
    add_zero_line,
    billions,
    euro_billions,
    mark_point,
    new_figure,
    save_figure,
)
from demand import DEMAND_LEVELS
from production_plan import (
    RAMP_LABELS,
    TARGET_CASE,
    first_full_year_at_rate,
    get_production_ramp,
)
from scenarios import (
    delay_cases,
    evaluate_rate_scenario,
    ramp_cases,
    rate_sensitivity,
    run_ramp_case,
)


def modelled_period_text():
    """The years covered by the model itself, without the extended life."""
    years = list(get_production_ramp(TARGET_CASE).keys())

    return f"{years[0]} to {years[-1]}"


# --------------------------------------------------
# Figure: NPV vs production rate
# --------------------------------------------------

def plot_npv_vs_production_rate(reported):
    rate_df = rate_sensitivity()

    rates = rate_df["monthly_rate"]
    npvs = billions(rate_df["npv"])

    peak_index = npvs.idxmax()
    peak_rate = rates[peak_index]
    peak_npv = npvs[peak_index]

    target_rate = reported["target_monthly_rate_high"]
    target_npv = npvs[rates == target_rate].iloc[0]

    fig, ax = new_figure()

    ax.plot(rates, npvs, color=COLOR_PRIMARY)

    add_zero_line(ax, npvs)

    # Airbus target rate
    ax.axvline(
        target_rate,
        color=COLOR_REFERENCE,
        linewidth=1,
    )

    ax.plot(
        target_rate,
        target_npv,
        marker="o",
        markersize=8,
        color=COLOR_PRIMARY,
        markeredgecolor="white",
        markeredgewidth=2,
    )

    ax.annotate(
        f"Airbus target: {target_rate:.0f}/month\n€{target_npv:.1f}bn",
        xy=(target_rate, target_npv),
        xytext=(10, -8),
        textcoords="offset points",
        ha="left",
        va="top",
        color=COLOR_TEXT,
        fontsize=9,
    )

    # Value-maximising rate under the model assumptions
    ax.plot(
        peak_rate,
        peak_npv,
        marker="o",
        markersize=8,
        color=COLOR_PRIMARY,
        markeredgecolor="white",
        markeredgewidth=2,
    )

    ax.annotate(
        f"Peak: {peak_rate:.0f}/month\n€{peak_npv:.1f}bn",
        xy=(peak_rate, peak_npv),
        xytext=(10, 4),
        textcoords="offset points",
        ha="left",
        va="bottom",
        color=COLOR_TEXT,
        fontsize=9,
    )

    ax.set_ylim(top=peak_npv * 1.15)
    ax.set_xlabel("Constant monthly production rate (aircraft)")
    ax.set_ylabel("NPV (€ billion)")

    add_titles(
        fig,
        headline=(
            f"NPV peaks at {peak_rate:.0f} aircraft/month, "
            f"where capacity meets delivery demand"
        ),
        subtitle=(
            f"NPV, {modelled_period_text()}, by constant monthly "
            f"A320-family production rate"
        ),
    )

    save_figure(fig, "npv_vs_production_rate.png")


# --------------------------------------------------
# Figure: NPV vs production rate by demand level
# Shows how the value-maximising rate depends on the
# assumed long-run delivery demand
# --------------------------------------------------

def plot_npv_vs_production_rate_by_demand(reported):
    target_rate = reported["target_monthly_rate_high"]

    demand_styles = [
        ("downside", "Low demand", COLOR_TERTIARY),
        ("base", "Base demand", COLOR_PRIMARY),
        ("upside", "High demand", COLOR_SECONDARY),
    ]

    fig, ax = new_figure()

    ax.axvline(
        target_rate,
        color=COLOR_REFERENCE,
        linewidth=1,
    )

    peaks = {}
    all_npvs = []

    for demand_case, label, color in demand_styles:
        rate_df = rate_sensitivity(demand_case)

        rates = rate_df["monthly_rate"]
        npvs = billions(rate_df["npv"])

        all_npvs.extend(npvs)

        peak_index = npvs.idxmax()
        peak_rate = rates[peak_index]
        peak_npv = npvs[peak_index]

        peaks[demand_case] = peak_rate

        # The peak of each curve is given in the legend, to keep
        # labels off the lines
        ax.plot(
            rates,
            npvs,
            color=color,
            label=(
                f"{label}, {DEMAND_LEVELS[demand_case]:,}/year: "
                f"peak at {peak_rate:.0f}/month, {euro_billions(peak_npv)}"
            ),
        )

        mark_point(ax, peak_rate, peak_npv, color)

    add_zero_line(ax, all_npvs)

    ax.annotate(
        f"Airbus target:\n{target_rate:.0f}/month",
        xy=(target_rate, min(all_npvs)),
        xytext=(-6, 0),
        textcoords="offset points",
        ha="right",
        va="bottom",
        color=COLOR_TEXT,
        fontsize=9,
    )

    ax.set_ylim(top=max(all_npvs) * 1.3)
    ax.set_xlabel("Constant monthly production rate (aircraft)")
    ax.set_ylabel("NPV (€ billion)")

    # White background so the legend stays readable over the target line
    ax.legend(
        loc="upper left",
        fontsize=9,
        frameon=True,
        facecolor="white",
        edgecolor="none",
        framealpha=1,
    )

    add_titles(
        fig,
        headline=(
            f"The value-maximising rate moves from {peaks['downside']:.0f} to "
            f"{peaks['upside']:.0f} a month across the demand range"
        ),
        subtitle=(
            f"NPV, {modelled_period_text()}, by constant monthly "
            f"production rate for three demand levels"
        ),
    )

    save_figure(fig, "npv_vs_production_rate_by_demand.png")


# --------------------------------------------------
# Figure: Tornado chart of NPV sensitivity
# One assumption is moved to its low and high value
# while all others stay at their base value
# --------------------------------------------------

TORNADO_PARAMETERS = {
    "incremental_margin_per_aircraft": (
        "Margin per aircraft",
        "€{:.0f}m",
    ),
    "supply_chain_availability": (
        "Supply-chain availability",
        "{:.0%}",
    ),
    "baseline_monthly_rate": (
        "No-investment baseline rate",
        "{:g}/month",
    ),
    "ramp_investment": (
        "Ramp investment",
        "€{:,.0f}m",
    ),
    "discount_rate": (
        "Discount rate",
        "{:.0%}",
    ),
    "expedite_premium": (
        "Expedite premium",
        "{:.0%}",
    ),
}


def plot_npv_tornado():
    base = load_assumptions("base")
    downside = load_assumptions("downside")
    upside = load_assumptions("upside")

    base_npv = billions(run_ramp_case(TARGET_CASE, base)["npv"])

    rows = []

    for parameter, (label, value_format) in TORNADO_PARAMETERS.items():

        downside_case = dict(base)
        downside_case[parameter] = downside[parameter]

        upside_case = dict(base)
        upside_case[parameter] = upside[parameter]

        npv_at_downside = billions(
            run_ramp_case(TARGET_CASE, downside_case)["npv"]
        )
        npv_at_upside = billions(
            run_ramp_case(TARGET_CASE, upside_case)["npv"]
        )

        rows.append({
            "label": label,
            "base_text": value_format.format(base[parameter]),
            "npv_at_downside": npv_at_downside,
            "npv_at_upside": npv_at_upside,
            "downside_text": value_format.format(downside[parameter]),
            "upside_text": value_format.format(upside[parameter]),
            "swing": abs(npv_at_upside - npv_at_downside),
        })

    # Delivery demand is defined in demand.py rather than the
    # assumptions file, so it is added separately
    npv_at_downside = billions(
        run_ramp_case(TARGET_CASE, base, demand_case="downside")["npv"]
    )
    npv_at_upside = billions(
        run_ramp_case(TARGET_CASE, base, demand_case="upside")["npv"]
    )

    rows.append({
        "label": "Delivery demand",
        "base_text": f"{DEMAND_LEVELS['base']:,}/year",
        "npv_at_downside": npv_at_downside,
        "npv_at_upside": npv_at_upside,
        "downside_text": f"{DEMAND_LEVELS['downside']:,}/year",
        "upside_text": f"{DEMAND_LEVELS['upside']:,}/year",
        "swing": abs(npv_at_upside - npv_at_downside),
    })

    # Largest swing at the top
    rows.sort(key=lambda row: row["swing"])

    fig, ax = new_figure()

    # Extra room on the left for the labels and on top for the legend
    fig.subplots_adjust(left=0.29, right=0.85, top=0.77)

    for position, row in enumerate(rows):

        for npv_value, text, color in [
            (row["npv_at_downside"], row["downside_text"], COLOR_SECONDARY),
            (row["npv_at_upside"], row["upside_text"], COLOR_PRIMARY),
        ]:
            ax.barh(
                position,
                npv_value - base_npv,
                left=base_npv,
                height=0.5,
                color=color,
            )

            if npv_value >= base_npv:
                offset, alignment = 5, "left"
            else:
                offset, alignment = -5, "right"

            # Say so when a value leaves NPV unchanged, so the missing
            # bar is not read as an error
            if abs(npv_value - base_npv) < 0.005:
                text = f"{text} (no effect)"

            ax.annotate(
                text,
                xy=(npv_value, position),
                xytext=(offset, 0),
                textcoords="offset points",
                ha=alignment,
                va="center",
                color=COLOR_TEXT,
                fontsize=9,
            )

    ax.axvline(
        base_npv,
        color=COLOR_TEXT,
        linewidth=1,
    )

    all_values = [
        value
        for row in rows
        for value in (row["npv_at_downside"], row["npv_at_upside"])
    ]

    add_zero_line(ax, all_values, horizontal=False)

    # Room at both ends for the value labels
    padding = (max(all_values) - min(all_values)) * 0.2

    ax.set_xlim(
        min(all_values) - padding * 1.5,
        max(all_values) + padding * 1.3,
    )

    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(
        [row["label"] for row in rows],
        color=COLOR_TEXT,
    )

    # Base value of each assumption in its own muted column to the
    # right of the bars, so the reader can see downside, base and
    # upside without a separate table
    row_transform = ax.get_yaxis_transform()

    for position, row in enumerate(rows):
        ax.text(
            1.03,
            position,
            row["base_text"],
            transform=row_transform,
            ha="left",
            va="center",
            color=COLOR_TEXT_MUTED,
            fontsize=9,
        )

    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)

    ax.set_xlabel(
        f"NPV (€ billion). Vertical line: Base case, €{base_npv:.1f}bn"
    )

    legend = ax.legend(
        handles=[
            plt.Rectangle((0, 0), 1, 1, color=COLOR_SECONDARY),
            plt.Rectangle((0, 0), 1, 1, color=COLOR_PRIMARY),
        ],
        labels=[
            "Downside value",
            "Upside value",
        ],
        loc="lower right",
        bbox_to_anchor=(1.0, 1.0),
        ncol=2,
        fontsize=9,
    )

    # Heading for the base value column, placed level with the
    # legend text so the three headings sit on one line
    fig.canvas.draw()

    legend_text_box = legend.get_texts()[0].get_window_extent()

    heading_height = ax.transAxes.inverted().transform(
        (0, (legend_text_box.y0 + legend_text_box.y1) / 2)
    )[1]

    ax.text(
        1.03,
        heading_height,
        "Base value",
        transform=ax.transAxes,
        ha="left",
        va="center",
        color=COLOR_TEXT_MUTED,
        fontsize=9,
    )

    largest = rows[-1]

    add_titles(
        fig,
        headline=(
            f"{largest['label']} moves NPV the most"
        ),
        subtitle=(
            f"Target-case NPV, {modelled_period_text()}, when one "
            f"assumption moves to its downside or upside value"
        ),
    )

    save_figure(fig, "npv_tornado.png")


# --------------------------------------------------
# Figure: NPV vs supply-chain availability
# Availability is the share of the planned ramp that
# key suppliers can support
# --------------------------------------------------

def ramp_npv_at_availability(ramp_case, base_assumptions, availability):
    assumptions = dict(base_assumptions)
    assumptions["supply_chain_availability"] = availability

    return billions(run_ramp_case(ramp_case, assumptions)["npv"])


def break_even_availability(ramp_case, base_assumptions):
    """Availability at which the ramp NPV is zero, found by bisection."""
    low, high = 0.5, 1.0

    if ramp_npv_at_availability(ramp_case, base_assumptions, low) >= 0:
        return None

    if ramp_npv_at_availability(ramp_case, base_assumptions, high) < 0:
        return None

    for _ in range(40):
        middle = (low + high) / 2

        if ramp_npv_at_availability(ramp_case, base_assumptions, middle) < 0:
            low = middle
        else:
            high = middle

    return high


# All four ramp scenarios, and a simpler version with only the
# Airbus target and the slow ramp as the two extremes. The target
# case is listed last so that it is drawn on top.
AVAILABILITY_RAMPS_ALL = [
    ("slow", COLOR_QUATERNARY),
    ("gradual", COLOR_TERTIARY),
    ("moderate", COLOR_SECONDARY),
    ("target", COLOR_PRIMARY),
]

AVAILABILITY_RAMPS_SIMPLE = [
    ("slow", COLOR_SECONDARY),
    ("target", COLOR_PRIMARY),
]


def plot_npv_vs_supply_chain_availability(
    base_assumptions,
    ramp_styles,
    filename,
):
    percentages = [60 + 2.5 * step for step in range(17)]

    fig, ax = new_figure()

    all_npvs = []

    for ramp_case, color in ramp_styles:
        npvs = [
            ramp_npv_at_availability(
                ramp_case,
                base_assumptions,
                percentage / 100,
            )
            for percentage in percentages
        ]

        all_npvs.extend(npvs)

        ax.plot(
            percentages,
            npvs,
            color=color,
            label=RAMP_LABELS[ramp_case],
        )

    add_zero_line(ax, all_npvs)

    # Base case
    base_percentage = base_assumptions["supply_chain_availability"] * 100

    base_npv = ramp_npv_at_availability(
        TARGET_CASE,
        base_assumptions,
        base_percentage / 100,
    )

    mark_point(ax, base_percentage, base_npv)

    ax.annotate(
        f"Assumed availability: {base_percentage:.0f}%\n"
        f"{euro_billions(base_npv)}",
        xy=(base_percentage, base_npv),
        xytext=(-10, 6),
        textcoords="offset points",
        ha="right",
        va="bottom",
        color=COLOR_TEXT,
        fontsize=9,
    )

    # Break-even of the Airbus target case
    break_even = break_even_availability(TARGET_CASE, base_assumptions)

    if break_even is not None:
        break_even_percentage = break_even * 100

        mark_point(ax, break_even_percentage, 0)

        ax.annotate(
            f"Break-even: {break_even_percentage:.0f}%",
            xy=(break_even_percentage, 0),
            xytext=(10, -8),
            textcoords="offset points",
            ha="left",
            va="top",
            color=COLOR_TEXT,
            fontsize=9,
        )

    ax.set_xlabel(
        "Supply-chain availability "
        "(% of the planned ramp that suppliers can support)"
    )
    ax.set_ylabel("NPV (€ billion)")

    # Lines are drawn with the target case last so it sits on top;
    # the legend lists it first
    handles, labels = ax.get_legend_handles_labels()

    ax.legend(
        handles[::-1],
        labels[::-1],
        loc="upper left",
        fontsize=9,
    )

    if break_even is not None:
        headline = (
            f"The investment pays off only above about "
            f"{break_even_percentage:.0f}% supply-chain availability"
        )
    else:
        headline = "NPV depends on how well suppliers scale with the ramp"

    add_titles(
        fig,
        headline=headline,
        subtitle=(
            f"NPV, {modelled_period_text()}, by supply-chain availability. "
            f"Break-even shown for the Airbus target case"
        ),
    )

    save_figure(fig, filename)


# --------------------------------------------------
# Figure: NPV comparison by ramp scenario
# --------------------------------------------------

def plot_npv_by_ramp_scenario(ramp_results, base_assumptions):
    names = [RAMP_LABELS[name] for name in ramp_results]

    npvs = [
        billions(result["npv"])
        for result in ramp_results.values()
    ]

    extensions = [
        billions(result["extension_value"])
        for result in ramp_results.values()
    ]

    totals = [
        npv_value + extension
        for npv_value, extension in zip(npvs, extensions)
    ]

    expedite_costs = [
        billions(result["expedite_cost"])
        for result in ramp_results.values()
    ]

    first_year = int(
        ramp_results[TARGET_CASE]["annual_results"]["year"].iloc[0]
    )
    last_year = int(
        ramp_results[TARGET_CASE]["annual_results"]["year"].iloc[-1]
    )
    extension_years = int(base_assumptions["extended_life_years"])

    fig, ax = new_figure()

    # Darker segment: the modelled period. Lighter segment: the value
    # of the capacity continuing to earn for a fixed number of further
    # years, shown separately because it is an extrapolation.
    bars = ax.bar(
        names,
        npvs,
        width=0.35,
        color=COLOR_PRIMARY,
        label=f"{first_year} to {last_year}",
    )

    ax.bar(
        names,
        extensions,
        bottom=npvs,
        width=0.35,
        color=COLOR_PRIMARY_LIGHT,
        label=(
            f"{last_year + 1} to {last_year + extension_years} "
            f"(extended life)"
        ),
    )

    add_zero_line(ax, npvs + totals)

    for bar, npv_value, total in zip(bars, npvs, totals):
        centre = bar.get_x() + bar.get_width() / 2

        ax.annotate(
            euro_billions(npv_value),
            xy=(centre, npv_value),
            xytext=(0, -6),
            textcoords="offset points",
            ha="center",
            va="top",
            color="white",
            fontsize=10,
            fontweight="bold",
        )

        ax.annotate(
            euro_billions(total),
            xy=(centre, total),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            color=COLOR_TEXT,
            fontsize=10,
            fontweight="bold",
        )

    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(
        [
            f"{name}\nAssumed expedite\ncost €{expedite_cost:.1f}bn"
            for name, expedite_cost in zip(names, expedite_costs)
        ],
        color=COLOR_TEXT,
    )

    ax.set_ylim(top=max(totals) * 1.28)
    ax.set_ylabel("NPV (€ billion)")

    ax.legend(
        loc="upper right",
        ncol=2,
        fontsize=9,
    )

    best_index = npvs.index(max(npvs))
    sorted_npvs = sorted(npvs, reverse=True)
    lead = sorted_npvs[0] - sorted_npvs[1]

    add_titles(
        fig,
        headline=(
            f"{names[best_index]} creates the most value, "
            f"by €{lead:.1f}bn over the next best"
        ),
        subtitle=(
            "NPV by production ramp scenario. The lighter segment "
            "assumes the final year's cash flow continues"
        ),
    )

    save_figure(fig, "npv_by_ramp_scenario.png")


# --------------------------------------------------
# Figure: Airbus target case capacity, deliveries and demand
# --------------------------------------------------

def plot_target_case(ramp_results):
    df = ramp_results[TARGET_CASE]["annual_results"]

    fig, ax = new_figure()

    fig.subplots_adjust(right=0.80)

    final_year = df["year"].iloc[-1]
    final_demand = df["delivery_demand"].iloc[-1]
    final_deliveries = df["deliveries"].iloc[-1]
    final_capacity = df["production_capacity"].iloc[-1]

    # When capacity is the binding constraint in every year, deliveries
    # and capacity are the same line, so they are drawn and labelled once.
    capacity_equals_deliveries = (
        (df["production_capacity"] - df["deliveries"]).abs() < 1
    ).all()

    ax.plot(
        df["year"],
        df["delivery_demand"],
        color=COLOR_SECONDARY,
        label="Delivery demand",
    )

    end_labels = [(final_demand, f"Demand {final_demand:.0f}")]

    if capacity_equals_deliveries:
        ax.plot(
            df["year"],
            df["deliveries"],
            color=COLOR_PRIMARY,
            label="Deliveries (equal to production capacity)",
        )

        end_labels.append(
            (final_deliveries, f"Deliveries {final_deliveries:.0f}")
        )
    else:
        ax.plot(
            df["year"],
            df["production_capacity"],
            color=COLOR_TERTIARY,
            linestyle="--",
            label="Production capacity",
        )

        ax.plot(
            df["year"],
            df["deliveries"],
            color=COLOR_PRIMARY,
            label="Deliveries",
        )

        end_labels.append(
            (final_capacity, f"Capacity {final_capacity:.0f}")
        )
        end_labels.append(
            (final_deliveries, f"Deliveries {final_deliveries:.0f}")
        )

    for value, text in end_labels:
        ax.annotate(
            text,
            xy=(final_year, value),
            xytext=(8, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            color=COLOR_TEXT,
            fontsize=9,
        )

    ax.set_xticks(df["year"])
    ax.set_xlabel("Year")
    ax.set_ylabel("Aircraft per year")

    ax.legend(
        loc="lower right",
        fontsize=9,
    )

    capacity_bound_years = (
        df["production_capacity"] < df["delivery_demand"]
    ).sum()

    if capacity_bound_years == len(df):
        headline = (
            "Capacity, not demand, limits deliveries "
            "in every year of the Airbus target case"
        )
    else:
        headline = (
            f"Capacity limits deliveries in {capacity_bound_years} "
            f"of {len(df)} years of the Airbus target case"
        )

    add_titles(
        fig,
        headline=headline,
        subtitle=(
            "Airbus target case: annual delivery demand, production capacity "
            "and deliveries"
        ),
    )

    save_figure(fig, "target_case_deliveries_vs_demand.png")


# --------------------------------------------------
# Figure: Production ramp paths
# --------------------------------------------------

def plot_ramp_paths(reported, base_assumptions):
    target_rate = reported["target_monthly_rate_high"]
    actual_2025_rate = reported["a320_monthly_2025_average"]

    # Every path starts from the rate the existing system is assumed
    # to sustain with no further investment
    base_rate = base_assumptions["baseline_monthly_rate"]

    ramp_styles = [
        ("slow", COLOR_QUATERNARY),
        ("gradual", COLOR_TERTIARY),
        ("moderate", COLOR_SECONDARY),
        ("target", COLOR_PRIMARY),
    ]

    fig, ax = new_figure()

    ax.axhline(
        target_rate,
        color=COLOR_REFERENCE,
        linewidth=1,
    )

    target_years = {}

    for ramp_case, color in ramp_styles:
        ramp = get_production_ramp(ramp_case)

        years = [min(ramp) - 1] + list(ramp.keys())
        rates = [base_rate] + list(ramp.values())

        ax.plot(
            years,
            rates,
            color=color,
            label=RAMP_LABELS[ramp_case],
        )

        target_year = next(
            (
                year
                for year, rate in ramp.items()
                if rate >= target_rate
            ),
            None,
        )

        target_years[ramp_case] = target_year

        if target_year is not None:
            mark_point(ax, target_year, target_rate, color)

            ax.annotate(
                f"{target_year}",
                xy=(target_year, target_rate),
                xytext=(0, 9),
                textcoords="offset points",
                ha="center",
                va="bottom",
                color=COLOR_TEXT,
                fontsize=9,
            )

    first_year = years[0]

    ax.annotate(
        f"No-investment baseline: {base_rate:.0f}/month",
        xy=(first_year, base_rate),
        xytext=(10, -8),
        textcoords="offset points",
        ha="left",
        va="top",
        color=COLOR_TEXT,
        fontsize=9,
    )

    # Reported 2025 average, shown for reference only
    mark_point(ax, first_year, actual_2025_rate, COLOR_REFERENCE)

    ax.annotate(
        f"2025 actual average: {actual_2025_rate:.1f}/month",
        xy=(first_year, actual_2025_rate),
        xytext=(10, 0),
        textcoords="offset points",
        ha="left",
        va="center",
        color=COLOR_TEXT,
        fontsize=9,
    )

    ax.annotate(
        f"Airbus target: {target_rate:.0f}/month",
        xy=(years[-1], target_rate),
        xytext=(0, -8),
        textcoords="offset points",
        ha="right",
        va="top",
        color=COLOR_TEXT,
        fontsize=9,
    )

    ax.set_xticks(years)
    ax.set_ylim(
        bottom=min(base_rate, actual_2025_rate) - 4,
        top=target_rate * 1.08,
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Monthly production rate (aircraft)")

    # Lines are drawn with the target case last so it sits on top;
    # the legend lists it first
    handles, labels = ax.get_legend_handles_labels()

    ax.legend(
        handles[::-1],
        labels[::-1],
        loc="lower right",
        fontsize=9,
    )

    if target_years["target"] and target_years["slow"]:
        gap = target_years["slow"] - target_years["target"]

        headline = (
            f"The Airbus target reaches rate {target_rate:.0f} in "
            f"{target_years['target']}, {gap} years before the slow ramp"
        )
    else:
        headline = "The three ramps reach the target rate at different speeds"

    add_titles(
        fig,
        headline=headline,
        subtitle=(
            "Assumed monthly production rate by ramp scenario. "
            "Markers show when each reaches the target"
        ),
    )

    save_figure(fig, "ramp_paths.png")


# --------------------------------------------------
# Figure: Airbus target case cumulative cash flow
# Undiscounted, starting from the time-zero investment
# --------------------------------------------------

def plot_target_case_cumulative_cash_flow(ramp_results):
    result = ramp_results[TARGET_CASE]
    df = result["annual_results"]

    years = [df["year"].iloc[0] - 1] + list(df["year"])

    cumulative = [-result["upfront_investment"]]

    for net_cash_flow in df["net_cash_flow"]:
        cumulative.append(cumulative[-1] + net_cash_flow)

    cumulative = [billions(value) for value in cumulative]

    fig, ax = new_figure()

    ax.plot(years, cumulative, color=COLOR_PRIMARY)

    add_zero_line(ax, cumulative)

    # Deepest point of the investment phase
    trough_value = min(cumulative)
    trough_year = years[cumulative.index(trough_value)]

    mark_point(ax, trough_year, trough_value)

    ax.annotate(
        f"Lowest point: {trough_year}\n{euro_billions(trough_value)}",
        xy=(trough_year, trough_value),
        xytext=(10, -2),
        textcoords="offset points",
        ha="left",
        va="top",
        color=COLOR_TEXT,
        fontsize=9,
    )

    payback_year = result["payback_year"]

    if payback_year is not None:
        payback_value = cumulative[years.index(payback_year)]

        mark_point(ax, payback_year, payback_value)

        ax.annotate(
            f"Positive from {payback_year}",
            xy=(payback_year, payback_value),
            xytext=(-10, 6),
            textcoords="offset points",
            ha="right",
            va="bottom",
            color=COLOR_TEXT,
            fontsize=9,
        )

    final_value = cumulative[-1]

    ax.annotate(
        euro_billions(final_value),
        xy=(years[-1], final_value),
        xytext=(-8, 0),
        textcoords="offset points",
        ha="right",
        va="center",
        color=COLOR_TEXT,
        fontsize=9,
    )

    ax.set_ylim(bottom=trough_value - (final_value - trough_value) * 0.12)
    ax.set_xticks(years)
    ax.set_xticklabels(
        [f"End {years[0]}"] + [str(year) for year in years[1:]]
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative cash flow (€ billion)")

    if payback_year is not None:
        headline = (
            f"The Airbus target case is cash-negative until {payback_year}, "
            f"with a low point of {euro_billions(trough_value)}"
        )
    else:
        headline = (
            "The Airbus target case does not recover its investment "
            "within the model horizon"
        )

    add_titles(
        fig,
        headline=headline,
        subtitle=(
            "Airbus target case: cumulative incremental cash flow after "
            "investment and expedite costs, undiscounted"
        ),
    )

    save_figure(fig, "target_case_cumulative_cash_flow.png")


# --------------------------------------------------
# Figures: delays of the Airbus target case
#
# All three use the NPV including the extended life, so
# that a long delay is not penalised simply for pushing
# deliveries past the end of the modelled period.
# --------------------------------------------------

def delay_label(delay_years):
    if delay_years == 0:
        return "Airbus target"

    if delay_years == 1:
        return "1-year delay"

    return f"{delay_years}-year delay"


def valuation_period_text(ramp_results, base_assumptions):
    years = ramp_results[TARGET_CASE]["annual_results"]["year"]

    first_year = int(years.iloc[0])
    last_year = int(years.iloc[-1]) + int(
        base_assumptions["extended_life_years"]
    )

    return f"{first_year} to {last_year}"


def plot_npv_by_delay_unplanned(delays, period_text):
    npvs = billions(delays["unplanned_npv_with_extension"]).tolist()

    labels = [
        f"{delay_label(row.delay_years)}\n"
        f"({row.first_full_year_at_target_rate})"
        for row in delays.itertuples()
    ]

    fig, ax = new_figure()

    # Extra room below for the two-line scenario labels
    fig.subplots_adjust(bottom=0.22)

    bars = ax.bar(
        range(len(npvs)),
        npvs,
        width=0.5,
        color=[COLOR_PRIMARY] + [COLOR_SECONDARY] * (len(npvs) - 1),
    )

    add_zero_line(ax, npvs)

    for bar, npv_value in zip(bars, npvs):
        ax.annotate(
            euro_billions(npv_value),
            xy=(bar.get_x() + bar.get_width() / 2, max(npv_value, 0)),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            color=COLOR_TEXT,
            fontsize=10,
            fontweight="bold",
        )

    ax.set_xticks(range(len(npvs)))
    ax.set_xticklabels(labels, color=COLOR_TEXT, fontsize=9)

    ax.set_ylim(top=max(npvs) * 1.15)
    ax.set_xlabel("Scenario (first full year at rate 75 in brackets)")
    ax.set_ylabel("NPV (€ billion)")

    loss_per_year = (npvs[0] - npvs[-1]) / (len(npvs) - 1)

    add_titles(
        fig,
        headline=(
            f"Each year of unplanned delay costs about "
            f"€{loss_per_year:.1f}bn of NPV"
        ),
        subtitle=(
            f"NPV, {period_text}. Investment is paid on the target "
            f"schedule but the rate increases arrive late"
        ),
    )

    save_figure(fig, "npv_by_delay_unplanned.png")


def plot_npv_by_delay(delays, period_text):
    delay_years = delays["delay_years"].tolist()

    planned = billions(delays["planned_npv_with_extension"]).tolist()
    unplanned = billions(delays["unplanned_npv_with_extension"]).tolist()

    fig, ax = new_figure()

    fig.subplots_adjust(right=0.80)

    ax.plot(
        delay_years,
        planned,
        color=COLOR_TERTIARY,
        marker="o",
        markersize=6,
        label="Planned: investment deferred with the ramp",
    )

    ax.plot(
        delay_years,
        unplanned,
        color=COLOR_SECONDARY,
        marker="o",
        markersize=6,
        label="Unplanned: investment paid on the target schedule",
    )

    add_zero_line(ax, planned + unplanned)

    mark_point(ax, delay_years[0], planned[0])

    ax.annotate(
        f"Airbus target\n{euro_billions(planned[0])}",
        xy=(delay_years[0], planned[0]),
        xytext=(10, 2),
        textcoords="offset points",
        ha="left",
        va="bottom",
        color=COLOR_TEXT,
        fontsize=9,
    )

    for values in (planned, unplanned):
        ax.annotate(
            euro_billions(values[-1]),
            xy=(delay_years[-1], values[-1]),
            xytext=(8, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            color=COLOR_TEXT,
            fontsize=9,
        )

    ax.set_xticks(delay_years)
    ax.set_xticklabels(
        [
            "None" if years == 0 else str(years)
            for years in delay_years
        ]
    )

    ax.set_ylim(top=max(planned) * 1.15)
    ax.set_xlabel("Delay to the Airbus target case (years)")
    ax.set_ylabel("NPV (€ billion)")

    ax.legend(
        loc="lower left",
        fontsize=9,
    )

    largest_gap = planned[-1] - unplanned[-1]

    add_titles(
        fig,
        headline=(
            f"A delay costs up to €{largest_gap:.1f}bn more when the "
            f"capacity has already been paid for"
        ),
        subtitle=(
            f"NPV, {period_text}, by years of delay to the "
            f"Airbus target case"
        ),
    )

    save_figure(fig, "npv_by_delay.png")


def plot_npv_slower_ramp_vs_delay(ramp_results, delays, reported, period_text):
    target_rate = reported["target_monthly_rate_high"]

    # Pair each deliberately slower ramp with the unplanned delay of
    # the target case that reaches the target rate in the same year
    groups = []

    for ramp_case, result in ramp_results.items():
        if ramp_case == TARGET_CASE:
            continue

        year = first_full_year_at_rate(
            get_production_ramp(ramp_case),
            target_rate,
        )

        matching_delay = delays[
            delays["first_full_year_at_target_rate"] == year
        ]

        if matching_delay.empty:
            continue

        delay_row = matching_delay.iloc[0]

        groups.append({
            "year": year,
            "ramp_label": RAMP_LABELS[ramp_case],
            "ramp_npv": billions(result["npv_with_extension"]),
            "delay_label": delay_label(int(delay_row["delay_years"])),
            "delay_npv": billions(
                delay_row["unplanned_npv_with_extension"]
            ),
        })

    fig, ax = new_figure()

    # Extra room below for the three-line group labels
    fig.subplots_adjust(bottom=0.22)

    bar_width = 0.3

    for position, group in enumerate(groups):

        for offset, value, color in [
            (-bar_width / 2 - 0.01, group["ramp_npv"], COLOR_PRIMARY),
            (bar_width / 2 + 0.01, group["delay_npv"], COLOR_SECONDARY),
        ]:
            ax.bar(
                position + offset,
                value,
                width=bar_width,
                color=color,
            )

            ax.annotate(
                euro_billions(value),
                xy=(position + offset, value),
                xytext=(0, 5),
                textcoords="offset points",
                ha="center",
                va="bottom",
                color=COLOR_TEXT,
                fontsize=10,
                fontweight="bold",
            )

    all_values = [
        value
        for group in groups
        for value in (group["ramp_npv"], group["delay_npv"])
    ]

    add_zero_line(ax, all_values)

    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(
        [
            f"Rate 75 from {group['year']}\n"
            f"{group['ramp_label']}\n"
            f"vs {group['delay_label']}"
            for group in groups
        ],
        color=COLOR_TEXT,
    )

    ax.set_xlim(-0.6, len(groups) - 0.4)
    ax.set_ylim(top=max(all_values) * 1.25)
    ax.set_ylabel("NPV (€ billion)")

    ax.legend(
        handles=[
            plt.Rectangle((0, 0), 1, 1, color=COLOR_PRIMARY),
            plt.Rectangle((0, 0), 1, 1, color=COLOR_SECONDARY),
        ],
        labels=[
            "Deliberately slower ramp",
            "Airbus target, delayed (unplanned)",
        ],
        loc="upper right",
        ncol=2,
        fontsize=9,
    )

    gaps = [
        group["ramp_npv"] - group["delay_npv"]
        for group in groups
    ]

    if len(gaps) > 1:
        gap_text = f"€{min(gaps):.1f}bn to €{max(gaps):.1f}bn"
    else:
        gap_text = f"€{gaps[0]:.1f}bn"

    add_titles(
        fig,
        headline=(
            f"A deliberately slower ramp is worth {gap_text} more "
            f"than the target slipping"
        ),
        subtitle=(
            f"NPV, {period_text}, for scenarios that reach "
            f"rate {target_rate:.0f} in the same year"
        ),
    )

    save_figure(fig, "npv_slower_ramp_vs_delay.png")


# --------------------------------------------------
# Generate all figures
# --------------------------------------------------

def main():
    reported = load_input_values()
    base_assumptions = load_assumptions("base")
    ramp_results = ramp_cases()

    plot_ramp_paths(reported, base_assumptions)
    plot_target_case(ramp_results)
    plot_target_case_cumulative_cash_flow(ramp_results)
    plot_npv_by_ramp_scenario(ramp_results, base_assumptions)

    delays = delay_cases()
    period_text = valuation_period_text(ramp_results, base_assumptions)

    plot_npv_by_delay_unplanned(delays, period_text)
    plot_npv_by_delay(delays, period_text)
    plot_npv_slower_ramp_vs_delay(
        ramp_results,
        delays,
        reported,
        period_text,
    )
    plot_npv_vs_production_rate(reported)
    plot_npv_vs_production_rate_by_demand(reported)
    plot_npv_tornado()
    plot_npv_vs_supply_chain_availability(
        base_assumptions,
        AVAILABILITY_RAMPS_ALL,
        "npv_vs_supply_chain_availability.png",
    )
    plot_npv_vs_supply_chain_availability(
        base_assumptions,
        AVAILABILITY_RAMPS_SIMPLE,
        "npv_vs_supply_chain_availability_simple.png",
    )

    print(f"Figures saved in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
