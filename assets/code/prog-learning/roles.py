def summarize(temps):
    n = len(temps)             # fixed value
    total = 0                  # gatherer
    hottest = temps[0]         # most-wanted holder
    prev = None                # follower
    fell = False               # one-way flag
    for i in range(n):         # stepper
        t = temps[i]           # most-recent holder
        total += t
        if t > hottest:
            hottest = t
        if prev is not None and t < prev:
            fell = True
        prev = t
    return total / n, hottest, fell

print(summarize([21, 23, 22, 25, 24]))
