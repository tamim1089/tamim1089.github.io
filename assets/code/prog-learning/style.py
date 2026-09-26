"""Shared figure style for the post (site palette, serif, no top/right spines)."""
import matplotlib as mpl
TEAL, RED, MID, INK, GOLD, PAPER = "#0a7c5c", "#c0392b", "#666660", "#111118", "#b8860b", "#f0efe9"
mpl.rcParams.update({
    "font.family": "serif", "font.serif": ["IBM Plex Serif", "DejaVu Serif"],
    "font.size": 12, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.facecolor": PAPER,
    "savefig.dpi": 200, "savefig.bbox": "tight",
})
IMG = "../../img/prog-learning/"
