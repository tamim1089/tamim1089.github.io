"""Figures for the CCA post from the batched experiment results."""
import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
S = Path(__file__).parent; OUT = Path("/home/hex/tamim1089.github.io/assets/img/cca"); OUT.mkdir(exist_ok=True)
TEAL, RED, MID, INK, GOLD, BG = "#0a7c5c", "#c0392b", "#666660", "#111118", "#b8860b", "#f0efe9"
plt.rcParams.update({"font.family": "serif", "font.size": 10, "axes.edgecolor": MID, "axes.labelcolor": INK,
                     "xtick.color": MID, "ytick.color": MID, "axes.spines.top": False, "axes.spines.right": False})
D = json.load(open(S / "cca_results/synthetic.json")); ev = D["eval_every"]; runs = D["runs"]; Tmax = D["T_max"]
t_axis = np.arange(1, Tmax // ev + 1) * ev
def T_at(traj, tau):
    idx = np.nonzero(np.array(traj) < tau)[0]; return (idx[0] + 1) * ev if len(idx) else np.inf
def t_frac(traj, q):
    tr = np.array(traj); e = tr - tr.min(); idx = np.nonzero(e <= (1 - q) * e[0])[0]; return (idx[0] + 1) * ev if len(idx) else np.inf
DG = ["sin", "exp", "cubic", "tanh2", "square", "linear"]
LAB = {"sin": r"$\sin X$", "exp": r"$e^{0.5X}$", "cubic": r"$X^3$", "tanh2": r"$\tanh 2X$", "square": r"$X^2$", "linear": r"$2X$"}

# ── Fig A: mean loss curves, both directions, sigma=0.1 ─────────────────────
fig, axes = plt.subplots(2, 3, figsize=(11, 6.2), sharex=True)
for ax, dgp in zip(axes.flat, DG):
    rs = [r for r in runs if r["dgp"] == dgp and r["sigma"] == 0.1]
    F = np.array([r["fwd"] for r in rs]); R = np.array([r["rev"] for r in rs])
    for arr, c, lab in [(F, TEAL, "cause → effect"), (R, RED, "effect → cause")]:
        med = np.median(arr, 0); lo, hi = np.percentile(arr, [25, 75], 0)
        ax.plot(t_axis, med, color=c, lw=2, label=lab); ax.fill_between(t_axis, lo, hi, color=c, alpha=.15)
    ax.axhline(0.05, color=MID, ls=":", lw=1); ax.text(Tmax * 0.98, 0.055, r"$\tau=0.05$", ha="right", va="bottom", fontsize=8, color=MID)
    ax.set_yscale("log"); ax.set_xscale("log"); ax.set_title(LAB[dgp] + r" $+\,\varepsilon,\ \sigma_\varepsilon=0.1$", fontsize=10)
    ax.set_ylim(3e-3, 2)
for ax in axes[1]: ax.set_xlabel("optimizer step")
for ax in axes[:, 0]: ax.set_ylabel("held-out MSE (z-scored)")
axes[0, 0].legend(frameon=False, fontsize=9, loc="lower left")
fig.suptitle("The anticausal network descends faster and stops higher (median and IQR over 10 seeds)", fontsize=11, color=INK)
fig.tight_layout(); fig.savefig(OUT / "exp_loss_curves.png", dpi=170); plt.close(fig)

# ── Fig B: time to 90% of own descent, forward vs reverse ────────────────────
fig, ax = plt.subplots(figsize=(6.2, 5.6))
mk = {0.1: "o", 0.316: "s", 1.0: "^"}
cols = {"sin": TEAL, "exp": GOLD, "cubic": RED, "tanh2": "#2e75b6", "linear": MID}
for dgp in ["sin", "exp", "cubic", "tanh2", "linear"]:
    for s in [0.1, 0.316, 1.0]:
        rs = [r for r in runs if r["dgp"] == dgp and r["sigma"] == s]
        tf = np.array([t_frac(r["fwd"], .9) for r in rs]); trv = np.array([t_frac(r["rev"], .9) for r in rs])
        ok = np.isfinite(tf) & np.isfinite(trv)
        ax.scatter(tf[ok], trv[ok], marker=mk[s], s=34, color=cols[dgp], alpha=.75, edgecolor="white", lw=.5,
                   label=f"{LAB[dgp]}" if s == 0.1 else None)
lim = [5, 2000]; ax.plot(lim, lim, color=MID, lw=1, ls="--"); ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel(r"$t_{90}$, cause → effect  (steps to cover 90% of own descent)"); ax.set_ylabel(r"$t_{90}$, effect → cause")
ax.text(6, 380, "above diagonal:\ncause direction faster", fontsize=9, color=MID); ax.text(120, 6, "below diagonal: effect direction faster", fontsize=9, color=MID)
h, l = ax.get_legend_handles_labels()
from matplotlib.lines import Line2D
h += [Line2D([], [], marker=m, color=INK, ls="", ms=6) for m in mk.values()]; l += [rf"$\sigma_\varepsilon={s}$" for s in mk]
ax.legend(h, l, frameon=False, fontsize=8, ncol=2, loc="upper left")
fig.tight_layout(); fig.savefig(OUT / "exp_t90_scatter.png", dpi=170); plt.close(fig)

# ── Fig C: decision of the threshold rule as a function of tau ───────────────
taus = np.logspace(-2.3, 0, 60)
fig, axes = plt.subplots(1, 5, figsize=(13, 3.1), sharey=True)
for ax, dgp in zip(axes, ["sin", "exp", "cubic", "tanh2", "square"]):
    rs = [r for r in runs if r["dgp"] == dgp and r["sigma"] == 0.1]
    corr, wrong, abst = [], [], []
    for tau in taus:
        tf = np.array([min(T_at(r["fwd"], tau), Tmax) for r in rs]); trv = np.array([min(T_at(r["rev"], tau), Tmax) for r in rs])
        corr.append(np.mean(tf < trv)); wrong.append(np.mean(tf > trv)); abst.append(np.mean(tf == trv))
    ax.stackplot(taus, corr, abst, wrong, colors=[TEAL, BG, RED], labels=["correct", "tie / abstain", "wrong"], alpha=.9)
    Lf = np.mean([min(r["fwd"]) for r in rs]); Lr = np.mean([min(r["rev"]) for r in rs])
    ax.axvline(Lf, color=TEAL, lw=1, ls="--"); ax.axvline(Lr, color=RED, lw=1, ls="--"); ax.axvline(0.05, color=INK, lw=1, ls=":")
    ax.set_xscale("log"); ax.set_title(LAB[dgp], fontsize=10); ax.set_xlabel(r"threshold $\tau$"); ax.set_ylim(0, 1)
axes[0].set_ylabel("fraction of seeds"); axes[0].legend(frameon=False, fontsize=8, loc="lower left")
fig.suptitle(r"What the rule $\mathrm{sign}(T_{\mathrm{fwd}}-T_{\mathrm{rev}})$ answers as $\tau$ moves  (dashed: the two floors; dotted: $\tau=0.05$)", fontsize=10, color=INK)
fig.tight_layout(); fig.savefig(OUT / "exp_tau_sweep.png", dpi=170); plt.close(fig)
print("wrote", [p.name for p in OUT.glob("exp_*.png")])
