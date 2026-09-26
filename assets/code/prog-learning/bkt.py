"""Bayesian knowledge tracing (Corbett and Anderson): one skill, four parameters.
The parameter values here are illustrative, not fitted to any data."""
import json
import matplotlib.pyplot as plt
from style import TEAL, RED, MID, INK, IMG

L0, T, G, S = 0.2, 0.15, 0.2, 0.1   # known at start, learn per step, guess, slip

def trace(answers):
    p, out = L0, []
    for correct in answers:
        if correct:   # P(known | correct)
            p = p * (1 - S) / (p * (1 - S) + (1 - p) * G)
        else:         # P(known | wrong)
            p = p * S / (p * S + (1 - p) * (1 - G))
        p = p + (1 - p) * T   # chance to learn from this step
        out.append(round(p, 3))
    return out

learners = {
    "struggles, then gets it": [0, 0, 1, 0, 1, 1, 1, 1],
    "right every time": [1, 1, 1, 1, 1, 1, 1, 1],
}
res = {name: trace(a) for name, a in learners.items()}
for name, ps in res.items():
    first = next((i + 1 for i, p in enumerate(ps) if p >= 0.95), None)
    print(f"{name:26} {ps}  mastered at attempt {first}")
json.dump(res, open("bkt.json", "w"), indent=1)

fig, ax = plt.subplots(figsize=(7, 3.4))
for (name, ps), c in zip(res.items(), [TEAL, RED]):
    ax.plot(range(1, len(ps) + 1), ps, marker="o", color=c, label=name)
ax.axhline(0.95, color=MID, ls="--", lw=1)
ax.text(1, 0.965, "mastery threshold, 0.95", va="bottom", color=MID, fontsize=10)
ax.set_xlabel("attempt"); ax.set_ylabel("estimated P(skill known)")
ax.set_ylim(0, 1.02); ax.legend(frameon=False, loc="lower right")
fig.savefig(IMG + "bkt.png")
