"""Plain diagrams of the non-technical ideas in the post."""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from style import TEAL, RED, MID, INK, GOLD, PAPER, IMG

def box(ax, x, y, w, h, text, c=INK, fc=PAPER, fs=11):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", ec=c, fc=fc, lw=1.5))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK, wrap=True)

def arrow(ax, a, b, c=INK, ls="-"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=16, color=c, lw=1.5, ls=ls))

def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h)); ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off"); return fig, ax

# 1. Where help sits: the range between giving the answer and giving nothing
fig, ax = canvas(10, 2.6)
steps = ["nothing", "a question", "where to look", "a failing input", "a partial\nsolution", "the answer"]
for i, s in enumerate(steps):
    box(ax, 0.2 + i * 1.62, 1.0, 1.45, 0.9, s, c=TEAL if i < 4 else RED)
arrow(ax, (0.3, 0.55), (9.7, 0.55), c=MID)
ax.text(0.3, 0.2, "the learner does more", color=TEAL, fontsize=10)
ax.text(9.7, 0.2, "the helper does more", color=RED, fontsize=10, ha="right")
fig.savefig(IMG + "help-range.png"); plt.close(fig)

# 2. Where knowledge about a line of code lives
fig, ax = canvas(9, 3.2)
box(ax, 0.3, 1.9, 2.4, 0.9, "the code\nwhat it does", c=TEAL)
box(ax, 3.3, 1.9, 2.4, 0.9, "the history\nwho, when, what changed", c=GOLD)
box(ax, 6.3, 1.9, 2.4, 0.9, "people\nwhy", c=RED)
ax.text(4.5, 1.0, "each step to the right is harder to recover and easier to lose", ha="center", fontsize=11, color=INK)
arrow(ax, (0.5, 0.6), (8.5, 0.6), c=MID)
fig.savefig(IMG + "knowledge-location.png"); plt.close(fig)

# 3. Bainbridge's irony: automation takes the common work and leaves the rare, hard work
fig, axs = plt.subplots(1, 2, figsize=(9, 3.2), sharey=True)
for a, title, human in zip(axs, ["before automation", "after automation"], [[1, 1, 1], [0, 0, 1]]):
    labels = ["routine\n(daily)", "unusual\n(monthly)", "failure\n(yearly)"]
    cols = [TEAL if h else "#cfcfc8" for h in human]
    a.bar(labels, [8, 3, 1], color=cols)
    a.set_title(title, fontsize=12)
axs[0].set_ylabel("how often it happens"); axs[0].set_yticks([])
axs[1].text(2, 2.2, "the person's\nonly practice", ha="center", fontsize=10, color=RED)
fig.suptitle("green: work the person still does (schematic, not data)", fontsize=10, color=MID, y=1.02)
fig.savefig(IMG + "automation-irony.png"); plt.close(fig)

# 4. A bathtub: code flows in at the generation rate, understanding drains it at the assimilation rate
fig, ax = canvas(8, 3.6)
ax.add_patch(plt.Rectangle((2.5, 0.6), 3, 1.8, fill=False, ec=INK, lw=2))
ax.add_patch(plt.Rectangle((2.5, 0.6), 3, 1.1, color=RED, alpha=0.25))
ax.text(4, 1.15, "code nobody on the\nteam understands yet", ha="center", fontsize=10)
arrow(ax, (1.0, 3.2), (3.0, 2.5), c=RED); ax.text(0.2, 3.3, "new code in\n(generation rate)", fontsize=10)
arrow(ax, (5.0, 0.6), (6.8, 0.1), c=TEAL); ax.text(6.0, 0.9, "understood\n(assimilation rate)", fontsize=10)
fig.savefig(IMG + "bathtub.png"); plt.close(fig)
print("diagrams ok")
