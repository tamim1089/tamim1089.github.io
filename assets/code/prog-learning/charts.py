"""Charts redrawn from numbers the papers report (no data of our own)."""
import matplotlib.pyplot as plt
from style import TEAL, RED, MID, INK, GOLD, IMG

# Kapur (2014), study 1: posttest scores out of 10
fig, ax = plt.subplots(figsize=(6.5, 3.4))
parts, pf, di = ["procedure", "concepts", "transfer"], [9.24, 6.33, 5.37], [9.47, 3.84, 3.11]
x = range(3)
ax.bar([i - 0.19 for i in x], pf, 0.36, color=TEAL, label="failed first, then taught")
ax.bar([i + 0.19 for i in x], di, 0.36, color=MID, label="taught first, then practiced")
for i in x:
    ax.text(i - 0.19, pf[i] + 0.15, pf[i], ha="center", fontsize=10)
    ax.text(i + 0.19, di[i] + 0.15, di[i], ha="center", fontsize=10)
ax.set_xticks(list(x), parts); ax.set_ylim(0, 10.5); ax.set_ylabel("posttest score (out of 10)")
ax.legend(frameon=False, loc="upper right", fontsize=10)
fig.savefig(IMG + "kapur2014.png")

# METR (2025): change in task completion time with AI; negative means faster
fig, ax = plt.subplots(figsize=(7, 3.2))
rows = [("economists' forecast", -39, None), ("ML experts' forecast", -38, None),
        ("developers' forecast", -24, None), ("developers' estimate afterwards", -20, None),
        ("measured", 19, (2, 39))]
for y, (label, v, ci) in enumerate(rows):
    c = RED if ci else MID
    if ci:
        ax.plot(ci, [y, y], color=c, lw=2.5)
    ax.scatter([v], [y], s=70, color=c, zorder=3)
ax.axvline(0, color=INK, lw=0.8)
ax.set_yticks(range(len(rows)), [r[0] for r in rows]); ax.invert_yaxis()
ax.set_xlabel("change in completion time with AI (%)     faster  ←   →  slower")
ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
fig.savefig(IMG + "metr2025.png")
