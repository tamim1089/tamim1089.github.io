def first_at_least(xs, target):
    """Index of the first element >= target in sorted xs, or len(xs) if none."""
    lo, hi = 0, len(xs) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if xs[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

print(first_at_least([1, 3, 5, 7], 5))   # 2, correct
print(first_at_least([1, 3, 5, 7], 4))   # 2, correct
print(first_at_least([1, 3, 5, 7], 9))   # should be 4
