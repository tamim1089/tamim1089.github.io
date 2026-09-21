"""How much of Malimg accuracy is the dataset?  Three classifiers, two splits, one leakage check.

  size_knn     : 1-NN on (width, height) only. Byteplot width is a function of file size, so this measures how
                 much "family" is just "file size".
  pixels32_knn : 1-NN on the 32x32 downsampled image (1024 numbers).
  resnet       : the tutorial's model: ImageNet ResNet50, frozen, linear head, 75x75 input. The backbone is run
                 once and its 2048-d features cached, which is identical to training the head with the backbone frozen.

  random  split: stratified 80/20 over images (what the tutorial does).
  grouped split: near-duplicate groups (identical 8x8 average-hash) kept on one side of the split.

Usage: python malimg_exp.py <malimg_root_with_family_folders> <out_dir>
"""
import sys, json, hashlib, time, collections
from pathlib import Path
import numpy as np, torch
from PIL import Image
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split, GroupShuffleSplit
from sklearn.metrics import accuracy_score, f1_score

ROOT, OUT = Path(sys.argv[1]), Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
torch.set_num_threads(6); rng = np.random.default_rng(0)

# ── 1. inventory ──────────────────────────────────────────────────────────────
t0 = time.time()
paths = sorted(p for p in ROOT.rglob("*.png"))
fam = np.array([p.parent.name for p in paths]); families = sorted(set(fam)); y = np.array([families.index(f) for f in fam])
dims, ahash, md5, pix32, im75 = [], [], [], [], []
for p in paths:
    im = Image.open(p).convert("L"); w, h = im.size; dims.append((w, h))
    md5.append(hashlib.md5(p.read_bytes()).hexdigest())
    small = np.asarray(im.resize((8, 8), Image.BILINEAR), dtype=np.float32); ahash.append((small > small.mean()).tobytes())
    pix32.append(np.asarray(im.resize((32, 32), Image.BILINEAR), dtype=np.float32).ravel() / 255.0)
    im75.append(np.asarray(im.resize((75, 75), Image.BILINEAR), dtype=np.float32) / 255.0)
dims = np.array(dims, dtype=np.float32); pix32 = np.stack(pix32); im75 = np.stack(im75)
print(f"loaded {len(paths)} images, {len(families)} families in {time.time()-t0:.0f}s", flush=True)

# near-duplicate groups: identical average hash => same group
gid = {}; groups = np.array([gid.setdefault(a, len(gid)) for a in ahash])
exact_dupes = len(md5) - len(set(md5)); n_groups = len(gid)
sizes = collections.Counter(groups.tolist()); singletons = sum(1 for g, c in sizes.items() if c == 1)
print(f"exact duplicate files: {exact_dupes}; near-duplicate groups: {n_groups} (singletons {singletons})", flush=True)

# ── 2. ResNet50 features, frozen backbone (run once) ──────────────────────────
import torchvision
net = torchvision.models.resnet50(weights=torchvision.models.ResNet50_Weights.IMAGENET1K_V1); net.fc = torch.nn.Identity(); net.eval()
mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1); std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
feats = []
with torch.no_grad():
    for i in range(0, len(im75), 128):
        x = torch.tensor(im75[i:i + 128])[:, None].repeat(1, 3, 1, 1); x = (x - mean) / std
        feats.append(net(x).numpy())
feats = np.concatenate(feats); print(f"resnet50 features {feats.shape} in {time.time()-t0:.0f}s", flush=True)

# ── 3. splits ─────────────────────────────────────────────────────────────────
idx = np.arange(len(y))
tr_r, te_r = train_test_split(idx, test_size=0.2, random_state=0, stratify=y)
tr_g, te_g = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=0).split(idx, y, groups))
def leakage(tr, te):  # fraction of test images whose near-duplicate group also appears in train
    trg = set(groups[tr]); return float(np.mean([groups[i] in trg for i in te]))
splits = {"random": (tr_r, te_r), "grouped": (tr_g, te_g)}
print(f"random split: {leakage(tr_r, te_r)*100:.1f}% of test images have a near-duplicate in train; grouped: {leakage(tr_g, te_g)*100:.1f}%", flush=True)

# ── 4. classifiers ────────────────────────────────────────────────────────────
def knn(X, tr, te, k=1):
    m = KNeighborsClassifier(n_neighbors=k).fit(X[tr], y[tr]); return m.predict(X[te])
def linear_head(X, tr, te, epochs=40):
    Xt = torch.tensor(X); mu, sd = Xt[tr].mean(0), Xt[tr].std(0) + 1e-6; Xt = (Xt - mu) / sd
    head = torch.nn.Linear(X.shape[1], len(families)); opt = torch.optim.Adam(head.parameters(), lr=1e-3)
    yt = torch.tensor(y); g = torch.Generator().manual_seed(0)
    for _ in range(epochs):
        for b in torch.randperm(len(tr), generator=g).split(64):
            bi = torch.tensor(tr)[b]; loss = torch.nn.functional.cross_entropy(head(Xt[bi]), yt[bi]); opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad(): return head(Xt[te]).argmax(1).numpy()
methods = {"size_knn": lambda tr, te: knn(dims, tr, te), "pixels32_knn": lambda tr, te: knn(pix32, tr, te), "resnet": lambda tr, te: linear_head(feats, tr, te)}

res = {"n_images": int(len(y)), "n_families": len(families), "families": families, "family_counts": {f: int((fam == f).sum()) for f in families},
       "exact_duplicate_files": int(exact_dupes), "near_duplicate_groups": int(n_groups), "singleton_groups": int(singletons),
       "leakage_random": leakage(tr_r, te_r), "leakage_grouped": leakage(tr_g, te_g)}
for sname, (tr, te) in splits.items():
    res[sname] = {"n_train": int(len(tr)), "n_test": int(len(te)), "majority": float(np.mean(y[te] == np.bincount(y[tr]).argmax()))}
    for mname, fn in methods.items():
        pred = fn(tr, te)
        r = {"accuracy": float(accuracy_score(y[te], pred)), "macro_f1": float(f1_score(y[te], pred, average="macro")),
             "per_family_accuracy": {families[c]: float(np.mean(pred[y[te] == c] == c)) for c in range(len(families)) if (y[te] == c).any()}}
        res[sname][mname] = r; print(f"{sname:8s} {mname:13s} acc {r['accuracy']*100:5.1f}%  macro-F1 {r['macro_f1']:.3f}", flush=True)
# distinct (width,height) shapes per family: how far size alone identifies a family
res["shapes_per_family"] = {f: int(len({tuple(d) for d in dims[fam == f].astype(int).tolist()})) for f in families}
json.dump(res, open(OUT / "malimg_summary.json", "w"), indent=1)
print(f"done in {time.time()-t0:.0f}s -> {OUT/'malimg_summary.json'}")
