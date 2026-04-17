from __future__ import annotations

from matplotlib.axes import Axes


def apply_exec_dark_style(ax: Axes) -> None:
    """
    Polishes a Matplotlib Axes to match the executive dark theme.
    Keep this lightweight (no extra deps / global style mutation).
    """
    # Transparent plot area so Streamlit background shows through
    ax.set_facecolor((0, 0, 0, 0))
    # Also make the figure patch transparent (Streamlit renders the figure, not just the Axes)
    if getattr(ax, "figure", None) is not None:
        ax.figure.set_facecolor((0, 0, 0, 0))

    # Ticks / labels
    # Make axes readable on dark background (bigger + higher contrast)
    tick_color = "#f1f5f9"
    label_color = "#f1f5f9"
    ax.tick_params(axis="both", which="both", colors=tick_color, labelsize=13)
    ax.xaxis.label.set_color("#e5e7eb")
    ax.yaxis.label.set_color("#e5e7eb")
    ax.xaxis.label.set_color(label_color)
    ax.yaxis.label.set_color(label_color)
    ax.xaxis.label.set_size(14)
    ax.yaxis.label.set_size(14)
    ax.title.set_color("#ffffff")
    ax.title.set_size(16)

    # Scientific notation / offset text (e.g., "1e6") can be hard to read on dark bg
    try:
        ax.xaxis.get_offset_text().set_color(tick_color)
        ax.yaxis.get_offset_text().set_color(tick_color)
        ax.xaxis.get_offset_text().set_size(12)
        ax.yaxis.get_offset_text().set_size(12)
    except Exception:
        pass

    # Gridlines
    ax.grid(axis="y", linestyle="--", alpha=0.22, color="#94a3b8")

    # Spines
    for spine in ax.spines.values():
        spine.set_color((1, 1, 1, 0.10))

