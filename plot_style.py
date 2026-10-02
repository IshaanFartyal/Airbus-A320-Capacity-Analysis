# Shared report style for all figures.
# Used by plots.py (model-dependent figures) and
# fixed_plots.py (historical Airbus data figures).

from pathlib import Path

import matplotlib.pyplot as plt

OUTPUT_DIR = Path(__file__).parent / "outputs"

# Clean copies of every figure for the written report: no headline,
# subtitle or source note, because the report caption carries those
REPORT_DIR = OUTPUT_DIR / "report"
REPORT_SUFFIX = "_report"

# Marks the text that is left out of the report copy
STANDALONE_ONLY = "standalone_only"

SOURCE_NOTE = (
    "Source: Own model. Illustrative assumptions, not Airbus data."
)

# --------------------------------------------------
# Shared report style
# --------------------------------------------------

FIGURE_SIZE = (8, 4.8)

COLOR_PRIMARY = "#2a78d6"
COLOR_PRIMARY_LIGHT = "#a9c9ef"
COLOR_SECONDARY = "#eb6834"
COLOR_TERTIARY = "#1baf7a"
COLOR_QUATERNARY = "#eda100"

COLOR_TEXT = "#0b0b0b"
COLOR_TEXT_MUTED = "#52514e"
COLOR_GRID = "#e4e3df"
COLOR_REFERENCE = "#8a8983"

plt.rcParams.update({
    # DejaVu Sans ships with matplotlib, so figures render the same
    # on every machine
    "font.family": "DejaVu Sans",
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
    # A value that rounds to zero is shown without a minus sign
    if round(value_in_billions, 1) == 0:
        value_in_billions = 0

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


def shrink_to_fit(fig, text, minimum_font_size=8):
    """Reduce a title's font size until it fits within the figure width."""
    available_width = fig.get_window_extent().width * 0.97

    fig.canvas.draw()

    while (
        text.get_window_extent().x1 > available_width
        and text.get_fontsize() > minimum_font_size
    ):
        text.set_fontsize(text.get_fontsize() - 0.5)
        fig.canvas.draw()


def add_titles(fig, headline, subtitle):
    """Headline states the conclusion; subtitle says what is plotted."""
    headline_text = fig.text(
        0.02,
        0.955,
        headline,
        fontsize=12.5,
        fontweight="bold",
        color=COLOR_TEXT,
        ha="left",
        va="top",
    )

    subtitle_text = fig.text(
        0.02,
        0.895,
        subtitle,
        fontsize=10,
        color=COLOR_TEXT_MUTED,
        ha="left",
        va="top",
    )

    # Long titles are shrunk slightly rather than running off the figure
    shrink_to_fit(fig, headline_text)
    shrink_to_fit(fig, subtitle_text)

    headline_text.set_gid(STANDALONE_ONLY)
    subtitle_text.set_gid(STANDALONE_ONLY)


def save_figure(fig, filename, source_note=SOURCE_NOTE):
    """Save two copies: a standalone figure and a clean one for the report.

    outputs/<name>.png               headline, subtitle and source note
    outputs/report/<name>_report.png the plot only, cropped to its content
    """
    source_text = fig.text(
        0.02,
        0.02,
        source_note,
        fontsize=8,
        color=COLOR_TEXT_MUTED,
        ha="left",
        va="bottom",
    )
    source_text.set_gid(STANDALONE_ONLY)

    OUTPUT_DIR.mkdir(exist_ok=True)

    fig.savefig(
        OUTPUT_DIR / filename,
        dpi=300,
    )

    # Report copy: hide the title block and source note, then crop
    for text in fig.texts:
        if text.get_gid() == STANDALONE_ONLY:
            text.set_visible(False)

    REPORT_DIR.mkdir(exist_ok=True)

    report_filename = (
        Path(filename).stem + REPORT_SUFFIX + Path(filename).suffix
    )

    fig.savefig(
        REPORT_DIR / report_filename,
        dpi=300,
        bbox_inches="tight",
        pad_inches=0.1,
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
