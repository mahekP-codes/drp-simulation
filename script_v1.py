import random
from dataclasses import dataclass
from typing import List, Tuple

# ----------------------------
# Riffle shuffle (GSR model)
# ----------------------------

@dataclass
class ShuffleStep:
    cut_size_left: int
    interleave_pattern: str  # e.g., "LLRLRR..."
    before: List[int]
    after: List[int]

def gsr_riffle_shuffle(deck: List[int], rng: random.Random) -> Tuple[List[int], int, str]:
    """
    One Gilbert–Shannon–Reeds riffle shuffle:
    - Cut size L ~ Bin(n, 1/2)
    - Interleave by dropping from L/R proportional to remaining sizes
    Returns (new_deck, cut_size_left, pattern_string)
    """
    n = len(deck)

    # Cut: L ~ Binomial(n, 1/2) by counting coin flips
    L = sum(rng.getrandbits(1) for _ in range(n))
    left = deck[:L]
    right = deck[L:]

    # Interleave
    out = []
    pattern = []
    i = j = 0
    while i < len(left) or j < len(right):
        if i == len(left):
            out.append(right[j]); j += 1
            pattern.append("R")
        elif j == len(right):
            out.append(left[i]); i += 1
            pattern.append("L")
        else:
            rem_left = len(left) - i
            rem_right = len(right) - j
            if rng.random() < rem_left / (rem_left + rem_right):
                out.append(left[i]); i += 1
                pattern.append("L")
            else:
                out.append(right[j]); j += 1
                pattern.append("R")

    return out, L, "".join(pattern)

# ----------------------------
# Friendly "how mixed?" stats
# ----------------------------

def average_displacement(deck: List[int]) -> float:
    """
    Average distance each card moved from its original position.
    Card labels are 1..n and we assume original order [1,2,...,n].
    """
    pos = {card: i for i, card in enumerate(deck)}
    n = len(deck)
    total = 0
    for card in range(1, n + 1):
        original = card - 1
        total += abs(pos[card] - original)
    return total / n

def ordered_adjacent_pairs(deck: List[int]) -> int:
    """
    Counts how many adjacent pairs are still in increasing order (like ... 7,8 ...).
    In the perfectly ordered deck, this is n-1. As it mixes, this tends to drop.
    """
    count = 0
    for i in range(len(deck) - 1):
        if deck[i + 1] == deck[i] + 1:
            count += 1
    return count

def position_table(deck: List[int]) -> str:
    """
    Returns a neat table showing positions (1..n) and which card is there.
    """
    n = len(deck)
    pos_line = "Position: " + " ".join(f"{i:>3}" for i in range(1, n + 1))
    card_line = "Card:     " + " ".join(f"{c:>3}" for c in deck)
    return pos_line + "\n" + card_line

def tracked_cards_line(deck: List[int], tracked: List[int]) -> str:
    pos = {card: i + 1 for i, card in enumerate(deck)}  # 1-indexed for humans
    return "Tracked cards positions: " + ", ".join(f"{c}→{pos[c]}" for c in tracked)

# ----------------------------
# Markov chain demo runner
# ----------------------------

def run_demo(n: int = 10, shuffles: int = 6, seed: int = 42, tracked: List[int] = None) -> List[ShuffleStep]:
    """
    Runs a chain starting from identity permutation [1..n],
    applying riffle shuffle shuffles times, recording each step.
    """
    if tracked is None:
        tracked = [1, n // 2, n]  # easy-to-follow examples

    rng = random.Random(seed)
    deck = list(range(1, n + 1))
    steps: List[ShuffleStep] = []

    for _ in range(shuffles):
        before = deck[:]
        deck, cut_L, pattern = gsr_riffle_shuffle(deck, rng)
        steps.append(ShuffleStep(cut_L, pattern, before, deck[:]))

    # Print a friendly report
    print("\n" + "=" * 60)
    print("RIFFLE SHUFFLE AS A MARKOV CHAIN (small deck demo)")
    print("=" * 60)
    print(f"Deck size: {n} cards (labels 1..{n})")
    print(f"Shuffles: {shuffles}")
    print(f"Random seed: {seed} (so you can reproduce the same run)")
    print("\nInterpretation:")
    print("- A 'state' is the entire order of the deck (a permutation).")
    print("- Each riffle shuffle is one Markov step: next state depends only on current state.\n")

    # Initial state
    deck0 = list(range(1, n + 1))
    print("STEP 0 (start state):")
    print(position_table(deck0))
    print(tracked_cards_line(deck0, tracked))
    print(f"How mixed? avg displacement = {average_displacement(deck0):.2f}, "
          f"adjacent ordered pairs = {ordered_adjacent_pairs(deck0)} / {n-1}")
    print("-" * 60)

    # Each shuffle
    current = deck0[:]
    for t, st in enumerate(steps, start=1):
        current = st.after
        left = st.cut_size_left
        right = n - left
        print(f"STEP {t} (after shuffle #{t}):")
        print(f"Cut: left pile size = {left}, right pile size = {right}")
        print(f"Interleave pattern (L/R drops): {st.interleave_pattern}")
        print(position_table(current))
        print(tracked_cards_line(current, tracked))
        print(f"How mixed? avg displacement = {average_displacement(current):.2f}, "
              f"adjacent ordered pairs = {ordered_adjacent_pairs(current)} / {n-1}")
        print("-" * 60)

    print("\nTip:")
    print("- Try changing shuffles to 1..8 and watch how the 'how mixed' numbers change.")
    print("- For a real 52-card deck, the same idea applies, but you can’t list all 52! states.\n")

    return steps

if __name__ == "__main__":
    # Easy knobs to tweak:
    # - n: number of cards in the demo deck
    # - shuffles: number of riffle shuffles (often people talk about ~6-8 for 52 cards)
    # - seed: makes the run reproducible
    run_demo(n=10, shuffles=6, seed=random.randint(0, 100), tracked=[1, 5, 10])