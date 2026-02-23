import random
import itertools
from collections import Counter

# --------------------
# Riffle shuffle
# --------------------

def riffle(deck, rng):
    n = len(deck)

    # binomial cut
    L = sum(rng.getrandbits(1) for _ in range(n))
    left = deck[:L]
    right = deck[L:]

    out = []
    i = j = 0
    while i < len(left) or j < len(right):
        if i == len(left):
            out.append(right[j]); j+=1
        elif j == len(right):
            out.append(left[i]); i+=1
        else:
            remL = len(left)-i
            remR = len(right)-j
            if rng.random() < remL/(remL+remR):
                out.append(left[i]); i+=1
            else:
                out.append(right[j]); j+=1
    return out

# --------------------
# total variation distance
# --------------------

def total_variation(empirical_counts, n, trials):
    """
    empirical_counts: Counter of permutations
    """
    all_states = list(itertools.permutations(range(1,n+1)))
    uniform_prob = 1/len(all_states)

    tv = 0
    for s in all_states:
        p_emp = empirical_counts[s]/trials
        tv += abs(p_emp - uniform_prob)

    return 0.5*tv

# --------------------
# experiment
# --------------------

def experiment(n=5, max_shuffles=8, trials=50000, seed=0):
    rng = random.Random(seed)

    for k in range(max_shuffles+1):

        counts = Counter()

        for _ in range(trials):
            deck = list(range(1,n+1))

            for _ in range(k):
                deck = riffle(deck, rng)

            counts[tuple(deck)] += 1

        tv = total_variation(counts, n, trials)

        print(f"{k} shuffles -> TV distance = {tv:.4f}")

if __name__ == "__main__":
    experiment(n=5, trials=30000)