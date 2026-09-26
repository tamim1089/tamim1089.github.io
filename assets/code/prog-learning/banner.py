"""Banner: SICP box-and-pointer notation. Two names bound to one list (teal),
and the copy a beginner imagines (red, dashed, faint)."""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from style import TEAL, RED, IMG

BG, FG = "#111118", "#f0efe9"
plt.rcParams["savefig.bbox"] = "standard"  # keep the exact 16:9 canvas
fig = plt.figure(figsize=(16, 9), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis("off")
fig.patch.set_facecolor(BG)

def chain(x0, y, alpha=1.0, ls="-", color=FG, lw=4):
    w, h = 1.5, 0.75
    for k in range(3):
        x = x0 + k * 2.6
        for dx in (0, w / 2):
            ax.add_patch(Rectangle((x + dx, y), w / 2, h, fill=False, ec=color, lw=lw, ls=ls, alpha=alpha))
        ax.add_patch(FancyArrowPatch((x + w / 4, y + h / 2), (x + w / 4, y - 0.9), arrowstyle="-|>",
                                     mutation_scale=22, color=color, lw=lw - 1, ls=ls, alpha=alpha))
        ax.scatter([x + w / 4], [y - 1.12], s=160, color=color, alpha=alpha)
        if k < 2:
            ax.add_patch(FancyArrowPatch((x + 3 * w / 4, y + h / 2), (x + 2.6, y + h / 2), arrowstyle="-|>",
                                         mutation_scale=22, color=color, lw=lw - 1, ls=ls, alpha=alpha))
        else:  # nil: the diagonal slash in the last cdr
            ax.plot([x + w / 2, x + w], [y, y + h], color=color, lw=lw - 1, ls=ls, alpha=alpha)
    return x0, y, h

x0, y, h = chain(6.5, 5.5)
for label, ly in (("a", 7.5), ("b", 4.1)):
    ax.text(3.1, ly, label, color=FG, fontsize=64, family="serif", style="italic", ha="center", va="center")
    for glow in (14, 9):
        ax.add_patch(FancyArrowPatch((3.7, ly), (x0 - 0.05, y + h / 2), connectionstyle="arc3,rad=%s" % (-0.18 if ly > 5 else 0.18),
                                     arrowstyle="-", color=TEAL, lw=glow, alpha=0.08))
    ax.add_patch(FancyArrowPatch((3.7, ly), (x0 - 0.05, y + h / 2), connectionstyle="arc3,rad=%s" % (-0.18 if ly > 5 else 0.18),
                                 arrowstyle="-|>", mutation_scale=34, color=TEAL, lw=6))
chain(6.5, 2.2, alpha=0.45, ls=(0, (4, 3)), color=RED, lw=3)
ax.add_patch(FancyArrowPatch((3.7, 3.8), (6.4, 2.6), connectionstyle="arc3,rad=0.2", arrowstyle="-|>",
                             mutation_scale=26, color=RED, lw=3, ls=(0, (5, 4))))
fig.savefig(IMG + "banner.png", facecolor=BG, dpi=100, bbox_inches=None)
# thumbnail check copy
fig.savefig("/tmp/claude-1000/-home-hex-tamim1089-github-io/49e9fb27-3eb4-43cf-bb20-d546b4a84d9f/scratchpad/banner_thumb.png", facecolor=BG, dpi=27.5, bbox_inches=None)
