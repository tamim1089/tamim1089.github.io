"""The productive-failure task, rebuilt with made-up numbers: which player is most consistent?
Kapur's students had to invent a measure before being taught standard deviation."""
import json, statistics as st
import matplotlib.pyplot as plt
from style import TEAL, RED, MID, INK, GOLD, IMG

points = {  # points per game, six games (constructed data)
    "Ana":   [14, 15, 15, 16, 15, 15],
    "Bilal": [8, 22, 15, 15, 15, 15],
    "Chen":  [10, 12, 14, 16, 18, 20],
}

def measures(xs):
    m = st.mean(xs)
    return {
        "range": max(xs) - min(xs),
        "sum of deviations": sum(x - m for x in xs),
        "mean abs deviation": round(sum(abs(x - m) for x in xs) / len(xs), 2),
        "standard deviation": round(st.pstdev(xs), 2),
    }

out = {p: measures(xs) for p, xs in points.items()}
print(f"{'':7}{'range':>7}{'sum dev':>9}{'MAD':>7}{'SD':>7}")
for p, r in out.items():
    print(f"{p:7}{r['range']:>7}{r['sum of deviations']:>9}{r['mean abs deviation']:>7}{r['standard deviation']:>7}")
json.dump({"points": points, "measures": out}, open("consistency.json", "w"), indent=1)

fig, ax = plt.subplots(figsize=(7, 2.8))
for row, (p, xs) in enumerate(points.items()):
    ax.scatter(xs, [row] * len(xs), s=60, color=[TEAL, GOLD, RED][row], zorder=3)
    ax.plot([st.mean(xs)] * 2, [row - 0.3, row + 0.3], color=INK, lw=1)
ax.set_yticks(range(3), list(points)); ax.invert_yaxis()
ax.set_xlabel("points per game (the vertical tick is each player's mean)")
ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
fig.savefig(IMG + "consistency.png")
