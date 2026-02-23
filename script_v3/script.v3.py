import random
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Tuple

# =========================
# Riffle shuffle (GSR)
# =========================

def gsr_riffle_shuffle(deck: List[int], rng: random.Random) -> List[int]:
    """
    One Gilbert–Shannon–Reeds riffle shuffle:
      1) Cut size L ~ Bin(n, 1/2)
      2) Interleave by dropping from L/R proportional to remaining sizes
    """
    n = len(deck)
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
# Stats / diagnostics
# =========================

def rising_sequences(deck: List[int]) -> int:
    """
    Number of rising sequences (a.k.a. runs) in the permutation.
    Count 1 + number of descents (places where deck[i] > deck[i+1]).
    This is a classic riffle-shuffle diagnostic (Bayer–Diaconis context).
    """
    runs = 1
    for i in range(len(deck) - 1):
        if deck[i] > deck[i + 1]:
            runs += 1
    return runs

def fixed_points(deck: List[int]) -> int:
    """
    Number of cards that stayed in their original position.
    With labels 1..n and original order [1,2,...,n], a fixed point means deck[pos] == pos+1.
    """
    return sum(1 for i, c in enumerate(deck) if c == i + 1)

def top_k_cards(deck: List[int], k: int = 10) -> List[int]:
    return deck[:k]

def total_variation_from_uniform(dist: List[float]) -> float:
    """
    TV distance between a distribution on {1..n} (given as probabilities) and uniform on {1..n}.
    This is NOT TV on permutations; it's TV on an observable like "position of a tracked card".
    """
    n = len(dist)
    u = 1.0 / n
    return 0.5 * sum(abs(p - u) for p in dist)

def normalize_counter(cnt: Counter, n: int) -> List[float]:
    """
    Convert Counter of outcomes in {1..n} (1-indexed) into probability list of length n.
    """
    total = sum(cnt.values())
    if total == 0:
        return [0.0] * n
    return [cnt[i] / total for i in range(1, n + 1)]

def summarize_position_dist(dist: List[float], shown: int = 5) -> str:
    """
    Summarize a position distribution by showing top 'shown' positions by probability.
    Positions are 1..n.
    """
    indexed = list(enumerate(dist, start=1))
    indexed.sort(key=lambda x: x[1], reverse=True)
    top = indexed[:shown]
    return ", ".join([f"pos {pos}: {p:.3f}" for pos, p in top])

# =========================
# Simulation runner
# =========================

@dataclass
class PerShuffleStats:
    shuffle_num: int
    avg_runs: float
    avg_fixed_points: float
    tracked_tv: Dict[int, float]         # card -> TV distance of its position distribution vs uniform
    tracked_top_positions: Dict[int, str] # card -> short summary of position distribution
    example_top10: List[int]             # from one representative run

def simulate(
    n: int = 52,
    shuffles: int = 8,
    trials: int = 20000,
    tracked_cards: List[int] = None,
    seed: int = 42,
    show_example_seed: int = 123,
) -> List[PerShuffleStats]:
    """
    Runs Monte Carlo simulation of riffle shuffles.
    Produces per-shuffle statistics so users can see how things change each shuffle.
    """
    if tracked_cards is None:
        tracked_cards = [1, 26, 52]  # easy defaults

    rng = random.Random(seed)

    # For per-shuffle aggregation:
    runs_sum = [0] * (shuffles + 1)
    fixed_sum = [0] * (shuffles + 1)
    pos_counts: Dict[int, List[Counter]] = {c: [Counter() for _ in range(shuffles + 1)] for c in tracked_cards}

    # Representative example run (separate RNG so it is stable/reproducible)
    ex_rng = random.Random(show_example_seed)
    ex_deck = list(range(1, n + 1))
    ex_top10_by_shuffle = [top_k_cards(ex_deck, 10)]
    for _ in range(shuffles):
        ex_deck = gsr_riffle_shuffle(ex_deck, ex_rng)
        ex_top10_by_shuffle.append(top_k_cards(ex_deck, 10))

    # Monte Carlo trials
    for _ in range(trials):
        deck = list(range(1, n + 1))

        # shuffle 0 stats
        runs_sum[0] += rising_sequences(deck)
        fixed_sum[0] += fixed_points(deck)
        for c in tracked_cards:
            pos = deck.index(c) + 1
            pos_counts[c][0][pos] += 1

        for k in range(1, shuffles + 1):
            deck = gsr_riffle_shuffle(deck, rng)

            runs_sum[k] += rising_sequences(deck)
            fixed_sum[k] += fixed_points(deck)

            for c in tracked_cards:
                pos = deck.index(c) + 1
                pos_counts[c][k][pos] += 1

    # Build report objects
    out: List[PerShuffleStats] = []
    for k in range(shuffles + 1):
        tracked_tv: Dict[int, float] = {}
        tracked_top: Dict[int, str] = {}
        for c in tracked_cards:
            dist = normalize_counter(pos_counts[c][k], n)
            tracked_tv[c] = total_variation_from_uniform(dist)
            tracked_top[c] = summarize_position_dist(dist, shown=5)

        out.append(
            PerShuffleStats(
                shuffle_num=k,
                avg_runs=runs_sum[k] / trials,
                avg_fixed_points=fixed_sum[k] / trials,
                tracked_tv=tracked_tv,
                tracked_top_positions=tracked_top,
                example_top10=ex_top10_by_shuffle[k],
            )
        )
    return out

def print_report(stats: List[PerShuffleStats], tracked_cards: List[int], n: int) -> None:
    print("\n" + "=" * 72)
    print("RIFFLE SHUFFLE MIXING DEMO (52-card simulation)")
    print("=" * 72)
    print(f"Deck size: {n}")
    print("What you're looking at per shuffle:")
    print("- Avg rising sequences (runs): closer to random tends to increase vs ordered")
    print("- Avg fixed points: drops quickly from 52 toward ~1 (random perms have ~1 fixed point on average)")
    print("- Tracked-card position distribution TV distance vs uniform: 0 means 'looks uniform'")
    print("  (This TV is for the observable 'position of card c', not for all 52! permutations.)")

    print("\nTracked cards:", ", ".join(map(str, tracked_cards)))
    print("-" * 72)

    for s in stats:
        k = s.shuffle_num
        print(f"Shuffle {k}:")
        print(f"  Example top 10 cards (one run): {s.example_top10}")
        print(f"  Avg rising sequences (runs): {s.avg_runs:.2f}")
        print(f"  Avg fixed points: {s.avg_fixed_points:.2f}")

        for c in tracked_cards:
            tv = s.tracked_tv[c]
            tops = s.tracked_top_positions[c]
            print(f"  Card {c} position TV vs uniform: {tv:.3f} | most likely positions: {tops}")

        print("-" * 72)

def main():
    # Edit these knobs:
    n = 52
    shuffles = 8
    trials = 20000          # increase for smoother curves; decrease if slow
    tracked_cards = [1, 26, 52]
    seed = 42

    stats = simulate(
        n=n,
        shuffles=shuffles,
        trials=trials,
        tracked_cards=tracked_cards,
        seed=seed,
        show_example_seed=123
    )
    print_report(stats, tracked_cards, n)

if __name__ == "__main__":
    main()