import random
from collections import Counter
from dataclasses import dataclass
from math import factorial
from typing import List, Tuple


# =========================
# Riffle shuffle (GSR)
# =========================
def gsr_riffle_shuffle(deck: List[int], rng: random.Random) -> List[int]:
    n = len(deck)
    # Cut size L ~ Bin(n, 1/2)
    L = sum(rng.getrandbits(1) for _ in range(n))
    left = deck[:L]
    right = deck[L:]

    out = []
    i = j = 0
    while i < len(left) or j < len(right):
        if i == len(left):
            out.append(right[j]); j += 1
        elif j == len(right):
            out.append(left[i]); i += 1
        else:
            remL = len(left) - i
            remR = len(right) - j
            if rng.random() < remL / (remL + remR):
                out.append(left[i]); i += 1
            else:
                out.append(right[j]); j += 1
    return out


# =========================
# Diagnostics (easy to explain)
# =========================
def rising_sequences(deck: List[int]) -> int:
    # runs = 1 + number of descents
    runs = 1
    for i in range(len(deck) - 1):
        if deck[i] > deck[i + 1]:
            runs += 1
    return runs

def fixed_points(deck: List[int]) -> int:
    return sum(1 for i, c in enumerate(deck) if c == i + 1)

def avg_displacement(deck: List[int]) -> float:
    pos = {c: i for i, c in enumerate(deck)}
    n = len(deck)
    return sum(abs(pos[c] - (c - 1)) for c in range(1, n + 1)) / n

def top_k_probabilities(counts: Counter, trials: int, k: int = 8) -> List[Tuple[Tuple[int, ...], float]]:
    items = [(perm, c / trials) for perm, c in counts.items()]
    items.sort(key=lambda x: x[1], reverse=True)
    return items[:k]


# =========================
# TV distance over ALL permutations S_n
# =========================
def tv_distance_full_space(counts: Counter, trials: int, n: int) -> float:
    """
    TV(P, U) where:
      P = empirical distribution from simulation
      U = uniform distribution over ALL n! permutations

    No need to iterate over all n! permutations:
    unseen permutations contribute |0 - 1/n!| each.
    """
    N = factorial(n)
    u = 1.0 / N

    seen = len(counts)
    missing = N - seen

    s = 0.0
    for c in counts.values():
        p = c / trials
        s += abs(p - u)

    s += missing * u  # unseen states
    return 0.5 * s


# =========================
# Per-shuffle simulation + reporting
# =========================
@dataclass
class ShuffleReport:
    k: int
    tv_full: float
    avg_runs: float
    avg_fixed: float
    avg_disp: float
    top_perms: List[Tuple[Tuple[int, ...], float]]
    example_deck: Tuple[int, ...]


def simulate_per_shuffle(
    n: int = 8,
    shuffles: int = 8,
    trials: int = 100_000,
    seed: int = 42,
    topk: int = 8,
    example_seed: int = 123,
) -> List[ShuffleReport]:
    rng = random.Random(seed)

    # one reproducible example trajectory (for non-technical viewers)
    ex_rng = random.Random(example_seed)
    ex_deck = list(range(1, n + 1))
    example_by_k = [tuple(ex_deck)]
    for _ in range(shuffles):
        ex_deck = gsr_riffle_shuffle(ex_deck, ex_rng)
        example_by_k.append(tuple(ex_deck))

    reports: List[ShuffleReport] = []

    # fresh Monte Carlo for each k (simpler to explain; independent estimate each k)
    for k in range(shuffles + 1):
        counts = Counter()
        runs_sum = 0
        fixed_sum = 0
        disp_sum = 0.0

        for _ in range(trials):
            deck = list(range(1, n + 1))
            for _ in range(k):
                deck = gsr_riffle_shuffle(deck, rng)

            t = tuple(deck)
            counts[t] += 1
            runs_sum += rising_sequences(deck)
            fixed_sum += fixed_points(deck)
            disp_sum += avg_displacement(deck)

        tv = tv_distance_full_space(counts, trials, n)
        top_perms = top_k_probabilities(counts, trials, k=topk)

        reports.append(
            ShuffleReport(
                k=k,
                tv_full=tv,
                avg_runs=runs_sum / trials,
                avg_fixed=fixed_sum / trials,
                avg_disp=disp_sum / trials,
                top_perms=top_perms,
                example_deck=example_by_k[k],
            )
        )

    return reports


def print_reports(reports: List[ShuffleReport], n: int, trials: int) -> None:
    N = factorial(n)
    u = 1.0 / N

    print("\n" + "=" * 78)
    print("RIFFLE SHUFFLE MARKOV CHAIN (n=8) — EMPIRICAL DIST vs UNIFORM + TV DIST")
    print("=" * 78)
    print(f"Deck size: {n} cards | State space size: {n}! = {N:,} permutations")
    print(f"Trials per shuffle count: {trials:,}")
    print(f"Uniform probability of any ordering: 1/{N:,} ≈ {u:.8f}")
    print("\nTV distance here is over ALL permutations in S_8.")
    print("TV close to 0 means 'hard to distinguish from uniform randomness'.\n")

    for r in reports:
        print("-" * 78)
        print(f"After {r.k} shuffle(s):")
        print(f"  Example ordering (one run): {r.example_deck}")
        print(f"  TV distance to uniform (full space): {r.tv_full:.4f}")
        print(f"  Avg rising sequences (runs): {r.avg_runs:.2f}")
        print(f"  Avg fixed points: {r.avg_fixed:.2f}")
        print(f"  Avg displacement from start: {r.avg_disp:.2f}")

        print(f"  Most common orderings (empirical distribution top {len(r.top_perms)}):")
        for perm, p in r.top_perms:
            print(f"    P({perm}) ≈ {p:.6f}")

    print("\nDone.\n")


def main():
    # knobs
    n = 8
    shuffles = 8
    trials = 100_000   # try 50_000 for faster, 200_000 for smoother
    seed = 42

    reports = simulate_per_shuffle(
        n=n,
        shuffles=shuffles,
        trials=trials,
        seed=seed,
        topk=8,
        example_seed=123,
    )
    print_reports(reports, n=n, trials=trials)


if __name__ == "__main__":
    main()