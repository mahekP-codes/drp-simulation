import csv
import random
from collections import Counter
from math import factorial, log2
from typing import List, Tuple
import matplotlib.pyplot as plt


# -----------------------------
# One Markov step = one shuffle
# -----------------------------
def gsr_riffle_shuffle(deck: List[int], rng: random.Random) -> List[int]:
    n = len(deck)
    L = sum(rng.getrandbits(1) for _ in range(n))
    left = deck[:L]
    right = deck[L:]

    out = []
    i = j = 0
    while i < len(left) or j < len(right):
        if i == len(left):
            out.append(right[j])
            j += 1
        elif j == len(right):
            out.append(left[i])
            i += 1
        else:
            remL = len(left) - i
            remR = len(right) - j
            if rng.random() < remL / (remL + remR):
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
    return out


# -----------------------------
# Empirical distribution π_k
# -----------------------------
def empirical_distribution_after_k(n: int, k: int, trials: int, rng: random.Random) -> Counter:
    counts = Counter()
    start = list(range(1, n + 1))
    for _ in range(trials):
        deck = start[:]
        for _ in range(k):
            deck = gsr_riffle_shuffle(deck, rng)
        counts[tuple(deck)] += 1
    return counts


def top_states(counts: Counter, trials: int, top: int = 10) -> List[Tuple[Tuple[int, ...], float]]:
    items = [(state, c / trials) for state, c in counts.items()]
    items.sort(key=lambda t: t[1], reverse=True)
    return items[:top]


# -----------------------------
# Simple per-shuffle “stats”
# -----------------------------
def shannon_entropy_bits(counts: Counter, trials: int) -> float:
    H = 0.0
    for c in counts.values():
        p = c / trials
        H -= p * log2(p)
    return H


def marginal_position_distribution(counts: Counter, trials: int, card: int, n: int) -> List[float]:
    pos_counts = [0] * n
    for state, c in counts.items():
        pos = state.index(card)
        pos_counts[pos] += c
    return [x / trials for x in pos_counts]


def l1_distance_to_uniform_full_space(counts: Counter, trials: int, n: int) -> float:
    N = factorial(n)
    u = 1.0 / N
    seen = len(counts)
    missing = N - seen

    s = 0.0
    for c in counts.values():
        p = c / trials
        s += abs(p - u)
    s += missing * u
    return s


def tv_distance_to_uniform_full_space(counts: Counter, trials: int, n: int) -> float:
    return 0.5 * l1_distance_to_uniform_full_space(counts, trials, n)


def export_full_distribution_csv(counts: Counter, trials: int, k: int, filename: str) -> None:
    rows = [(state, c / trials) for state, c in counts.items()]
    rows.sort(key=lambda t: t[1], reverse=True)

    with open(filename, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["k", "ordering", "empirical_probability"])
        for state, p in rows:
            w.writerow([k, " ".join(map(str, state)), f"{p:.12f}"])


# -----------------------------
# Main report + graph
# -----------------------------
def run_report(
    n: int = 8,
    max_shuffles: int = 8,
    trials: int = 50_000,
    seed: int = 42,
    top: int = 10,
    tracked_card: int = 1,
    export_csv: bool = False,
) -> None:
    rng = random.Random(seed)

    total_states = factorial(n)
    uniform_prob = 1.0 / total_states

    print("\n" + "=" * 86)
    print("MARKOV CHAIN DEMO: RIFFLE SHUFFLE ON PERMUTATIONS")
    print("=" * 86)
    print(f"State space: all orderings of {n} cards (|S| = {n}! = {total_states:,}).")
    print(f"Uniform benchmark: each ordering would have probability 1/{total_states:,} ≈ {uniform_prob:.8f}")
    print(f"Trials per k: {trials:,} | Seed: {seed}")
    print(f"Tracked marginal: position distribution of card {tracked_card}")
    print("Per k, we print summaries of the empirical distribution π_k over states.\n")

    k_values = []
    tv_values = []

    for k in range(max_shuffles + 1):
        counts = empirical_distribution_after_k(n=n, k=k, trials=trials, rng=rng)

        distinct = len(counts)
        mass_top10 = sum(p for _, p in top_states(counts, trials, top=min(top, distinct)))
        p_identity = counts[tuple(range(1, n + 1))] / trials
        H = shannon_entropy_bits(counts, trials)
        l1 = l1_distance_to_uniform_full_space(counts, trials, n)
        tv = 0.5 * l1

        marg = marginal_position_distribution(counts, trials, tracked_card, n)
        marg_str = " ".join(f"{p:.3f}" for p in marg)

        print("-" * 86)
        print(f"k = {k} shuffle(s)")
        print(f"  Distinct orderings seen: {distinct:,} / {total_states:,}")
        print(f"  P(identity ordering) ≈ {p_identity:.6f}")
        print(f"  Top-{min(top, distinct)} probability mass ≈ {mass_top10:.3f}")
        print(f"  Entropy H(π_k) ≈ {H:.2f} bits (max possible is log2({n}!) ≈ {log2(total_states):.2f})")
        print(f"  L1 distance to uniform ≈ {l1:.6f}")
        print(f"  TV distance to uniform ≈ {tv:.6f}")
        print(f"  Marginal: P(card {tracked_card} at position 1..{n}) =")
        print(f"    {marg_str}")

        print(f"  Most likely orderings (top {min(top, distinct)}):")
        for state, p in top_states(counts, trials, top=min(top, distinct)):
            print(f"    P({state}) ≈ {p:.6f}")

        if export_csv:
            fname = f"empirical_pi_k_{k}.csv"
            export_full_distribution_csv(counts, trials, k, fname)
            print(f"  Wrote: {fname}")

        k_values.append(k)
        tv_values.append(tv)

    # -----------------------------
    # Plot after all computations
    # -----------------------------
    plt.figure(figsize=(8, 5))
    plt.plot(k_values, tv_values, marker="o")
    plt.xlabel("Number of shuffles")
    plt.ylabel("TV distance")
    plt.title(f"TV Distance to Uniform vs Number of Shuffles (n={n})")
    plt.grid(True)

    plt.savefig("tv_distance_plot.png", dpi=300, bbox_inches="tight")
    print("\nSaved graph as tv_distance_plot.png")

    plt.show()
    input("Press Enter to close the graph...")

    print("\nDone.\n")


if __name__ == "__main__":
    run_report(
        n=9,
        max_shuffles=8,
        trials=50000000,
        seed=42,
        top=10,
        tracked_card=1,
        export_csv=False,
    )
