# Trace this by hand before running it: what do the two prints show?
def reset(board):
    board = [0, 0, 0]

def clear(board):
    board[:] = [0, 0, 0]

b = [1, 2, 3]
reset(b)
print(b)
clear(b)
print(b)
