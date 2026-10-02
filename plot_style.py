# Shared report style for all figures.
# Used by plots.py (model-dependent figures) and
# fixed_plots.py (historical Airbus data figures).

from pathlib import Path

import matplotlib.pyplot as plt

OUTPUT_DIR = Path(__file__).parent / "outputs"

SOURCE_NOTE = (
    "Source: Own model. Illustrative assumptions, not Airbus data."
)

# --------------------------------------------------
# Shared report style
# --------------------------------------------------

FIGURE_SIZE = (8, 4.8)

COLOR_PRIMARY = "#2a78d6"
COLOR_SECONDARY = "#eb6834"
COLOR_TERTIARY = "#1baf7a"

COLOR_TEXT = "#0b0b0b"
COLOR_TEXT_MUTED = "#52514e"
COLOR_GRID = "#e4e3df"
COLOR_REFERENCE = "#8a8983"

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": COLOR_GRID,
    "axes.labelcolor": COLOR_TEXT_MUTED,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "axes.axisbelow": True,
    "grid.color": COLOR_GRID,
    "grid.linewidth": 0.8,
    "xtick.color": COLOR_TEXT_MUTED,
    "ytick.color": COLOR_TEXT_MUTED,
    "xtick.major.size": 0,
    "ytick.major.size": 0,
    "font.size": 10,
    "lines.linewidth": 2,
    "lines.solid_capstyle": "round",
    "legend.frameon": False,
})


def billions(value_in_millions):
    return value_in_millions / 1000


def euro_billions(value_in_billions):
    """Format a € billion value for labels, with a proper minus sign."""
    sign = "\u2212" if value_in_billions < 0 else ""

    return f"{sign}€{abs(value_in_billions):.1f}bn"


def new_figure():
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    # Leave room for the title block above and the source note below
    fig.subplots_adjust(
        left=0.10,
        right=0.95,
        top=0.82,
        bottom=0.17,
    )

    return fig, ax


def add_titles(fig, headline, subtitle):
    """Headline states the conclusion; subtitle says what is plotted."""
    fig.text(
        0.02,
        0.955,
        headline,
        fontsize=12.5,
        fontweight="bold",
        color=COLOR_TEXT,
        ha="left",
        va="top",
    )

    fig.text(
        0.02,
        0.895,
        subtitle,
        fontsize=10,
        color=COLOR_TEXT_MUTED,
        ha="left",
        va="top",
    )


def save_figure(fig, filename, source_note=SOURCE_NOTE):
    fig.text(
        0.02,
        0.02,
        source_note,
        fontsize=8,
        color=COLOR_TEXT_MUTED,
        ha="left",
        va="bottom",
    )

    OUTPUT_DIR.mkdir(exist_ok=True)

    fig.savefig(
        OUTPUT_DIR / filename,
        dpi=300,
    )

    plt.close(fig)


def mark_point(ax, x, y, color=COLOR_PRIMARY):
    """Marker with a white ring, used for the few points worth reading."""
    ax.plot(
        x,
        y,
        marker="o",
        markersize=8,
        color=color,
        markeredgecolor="white",
        markeredgewidth=2,
    )


def add_zero_line(ax, values, horizontal=True):
    """Draw a zero reference line only when the data crosses zero."""
    if min(values) < 0 < max(values):
        if horizontal:
            ax.axhline(0, color=COLOR_REFERENCE, linewidth=1)
        else:
            ax.axvline(0, color=COLOR_REFERENCE, linewidth=1)
