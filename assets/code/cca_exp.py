"""CCA experiments, batched: R independent MLPs trained at once (stacked parameters, one Adam; equivalent
to R separate runs since Adam is elementwise and the losses are independent). Records the full held-out
loss trajectory of every run so any threshold rule can be evaluated afterwards.
Usage: python cca_exp.py synthetic|tuebingen"""
import sys, json, time, urllib.request
import numpy as np, torch
from pathlib import Path

torch.set_num_threads(4)
OUT = Path(__file__).parent / "cca_results"; OUT.mkdir(exist_ok=True)
H = 64

def init_params(seeds):
    R = len(seeds)
    P = {k: torch.empty(s) for k, s in {"W1": (R, 1, H), "b1": (R, H), "W2": (R, H, H), "b2": (R, H), "W3": (R, H, 1), "b3": (R, 1)}.items()}
    with torch.no_grad():
        for r, s in enumerate(seeds):                  # same init as torch.nn.Linear (kaiming-uniform) per seed
            torch.manual_seed(int(s))
            l1 = torch.nn.Linear(1, H); l2 = torch.nn.Linear(H, H); l3 = torch.nn.Linear(H, 1)
            P["W1"][r] = l1.weight.T; P["b1"][r] = l1.bias; P["W2"][r] = l2.weight.T; P["b2"][r] = l2.bias; P["W3"][r] = l3.weight.T; P["b3"][r] = l3.bias
    return {k: v.detach().clone().requires_grad_(True) for k, v in P.items()}

def forward(P, x):                                     # x: [R, B, 1]
    h = torch.tanh(torch.bmm(x, P["W1"]) + P["b1"][:, None, :])
    h = torch.tanh(torch.bmm(h, P["W2"]) + P["b2"][:, None, :])
    return torch.bmm(h, P["W3"]) + P["b3"][:, None, :]

def train_batched(Xtr, Ytr, ntr, Xte, Yte, mte, seeds, T_max, eval_every=5, lr=1e-3, batch=128, gen_seed=0):
    """Xtr/Ytr: [R, Ntr_max] zero-padded, ntr: [R] valid train counts; Xte/Yte/mte: [R, Nte_max] with mask.
    Returns trajectories [R, T_max//eval_every] of held-out MSE."""
    R = Xtr.shape[0]
    P = init_params(seeds); opt = torch.optim.Adam(P.values(), lr=lr)
    g = torch.Generator().manual_seed(gen_seed)
    ntr_t = torch.tensor(ntr, dtype=torch.float32)[:, None]
    traj = torch.zeros(R, T_max // eval_every)
    xte, yte = Xte[..., None], Yte[..., None]; msum = mte.sum(1)
    for t in range(1, T_max + 1):
        idx = (torch.rand(R, batch, generator=g) * ntr_t).long()
        xb = torch.gather(Xtr, 1, idx)[..., None]; yb = torch.gather(Ytr, 1, idx)[..., None]
        loss = ((forward(P, xb) - yb) ** 2).mean(dim=(1, 2)).sum()
        opt.zero_grad(); loss.backward(); opt.step()
        if t % eval_every == 0:
            with torch.no_grad():
                se = ((forward(P, xte) - yte) ** 2)[..., 0] * mte
                traj[:, t // eval_every - 1] = se.sum(1) / msum
    return traj.numpy()

def prepare(runs, seeds, T_max, tag):
    """runs: list of (x, y) numpy pairs, one per direction-run. Builds padded z-scored tensors and trains."""
    R = len(runs); ntr = np.array([int(0.8 * len(x)) for x, _ in runs]); nte = np.array([len(x) - k for (x, _), k in zip(runs, ntr)])
    Xtr = torch.zeros(R, ntr.max()); Ytr = torch.zeros(R, ntr.max()); Xte = torch.zeros(R, nte.max()); Yte = torch.zeros(R, nte.max()); mte = torch.zeros(R, nte.max())
    for r, ((x, y), s) in enumerate(zip(runs, seeds)):
        rng = np.random.default_rng(int(s) + 12345); idx = rng.permutation(len(x)); tr, te = idx[:ntr[r]], idx[ntr[r]:]
        mx, sx = x[tr].mean(), x[tr].std() + 1e-12; my, sy = y[tr].mean(), y[tr].std() + 1e-12
        Xtr[r, :ntr[r]] = torch.tensor((x[tr] - mx) / sx); Ytr[r, :ntr[r]] = torch.tensor((y[tr] - my) / sy)
        Xte[r, :nte[r]] = torch.tensor((x[te] - mx) / sx); Yte[r, :nte[r]] = torch.tensor((y[te] - my) / sy); mte[r, :nte[r]] = 1
    t0 = time.time(); traj = train_batched(Xtr, Ytr, ntr, Xte, Yte, mte, seeds, T_max)
    print(f"[{tag}] trained {R} runs x {T_max} steps in {time.time()-t0:.0f}s", flush=True)
    return traj

# ── synthetic ─────────────────────────────────────────────────────────────────
def synthetic():
    dgps = {"sin": np.sin, "exp": lambda x: np.exp(0.5 * x), "cubic": lambda x: x ** 3,
            "tanh2": lambda x: np.tanh(2 * x), "square": lambda x: x ** 2, "linear": lambda x: 2 * x}
    sigmas = [0.1, 0.316, 1.0]; seeds = list(range(10)); T_max = 3000; n = 1000
    meta, runs, rseeds = [], [], []
    for name, f in dgps.items():
        for s in sigmas:
            for seed in seeds:
                rng = np.random.default_rng(1000 * seed + 7); x = rng.standard_normal(n); y = f(x) + s * rng.standard_normal(n)
                meta.append(dict(dgp=name, sigma=s, seed=seed)); runs += [(x, y), (y, x)]; rseeds += [seed, seed]
    traj = prepare(runs, rseeds, T_max, "synthetic")
    for i, m in enumerate(meta): m["fwd"] = traj[2 * i].tolist(); m["rev"] = traj[2 * i + 1].tolist()
    json.dump(dict(eval_every=5, T_max=T_max, runs=meta), open(OUT / "synthetic.json", "w"))

# ── Tübingen ──────────────────────────────────────────────────────────────────
BASE = "https://webdav.tuebingen.mpg.de/cause-effect/"
EXCLUDE = {52, 53, 54, 55, 71, 105}   # multivariate pairs, excluded by Mooij et al. 2016

def load_tuebingen():
    d = OUT / "tcep"; d.mkdir(exist_ok=True); meta_p = d / "pairmeta.txt"
    if not meta_p.exists(): urllib.request.urlretrieve(BASE + "pairmeta.txt", meta_p)
    pairs = []
    for line in meta_p.read_text().split("\n"):
        if not line.strip(): continue
        pid, cs, ce, es, ee, w = line.split(); pid = int(pid)
        if pid in EXCLUDE: continue
        p = d / f"pair{pid:04d}.txt"
        if not p.exists(): urllib.request.urlretrieve(BASE + p.name, p)
        arr = np.loadtxt(p) if "," not in p.read_text()[:200] else np.loadtxt(p, delimiter=",")
        if arr.ndim != 2 or arr.shape[1] < 2: continue
        pairs.append(dict(pid=pid, weight=float(w), cause=arr[:, int(cs) - 1].astype(float), effect=arr[:, int(es) - 1].astype(float)))
    return pairs

def tuebingen():
    pairs = load_tuebingen(); print(f"loaded {len(pairs)} pairs", flush=True)
    seeds = [0, 1, 2]; T_max = 4000; nmax = 2000
    meta, runs, rseeds = [], [], []
    for p in pairs:
        for seed in seeds:
            rng = np.random.default_rng(10_000 * p["pid"] + seed); c, e = p["cause"], p["effect"]
            if len(c) > nmax: sel = rng.choice(len(c), nmax, replace=False); c, e = c[sel], e[sel]
            flip = bool(rng.integers(2)); a, b = (e, c) if flip else (c, e)   # method never sees which column is the cause
            meta.append(dict(pid=p["pid"], weight=p["weight"], seed=seed, truth_ab=(not flip), n=int(len(c))))
            runs += [(a, b), (b, a)]; rseeds += [seed, seed]
    traj = prepare(runs, rseeds, T_max, "tuebingen")
    for i, m in enumerate(meta): m["fwd"] = traj[2 * i].tolist(); m["rev"] = traj[2 * i + 1].tolist()
    json.dump(dict(eval_every=5, T_max=T_max, runs=meta), open(OUT / "tuebingen.json", "w"))

if __name__ == "__main__":
    {"synthetic": synthetic, "tuebingen": tuebingen}[sys.argv[1]]()
