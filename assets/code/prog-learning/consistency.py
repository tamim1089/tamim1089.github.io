"""The productive-failure task, rebuilt with made-up numbers: which player is most consistent?
Kapur's students had to invent a measure before being taught standard deviation."""
import json, statistics as st

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
