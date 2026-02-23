# Riffle Shuffle Markov Chain Demo (n = 8)

This project simulates riffle shuffling as a Markov chain on permutations.

## What “state” means
A state is the entire ordering of the deck (a permutation).
For n = 8, there are 8! = 40,320 possible orderings.

## What the script measures (matches the meeting notes)

For each shuffle count k = 0..K:

1) **Empirical distribution over orderings**
- Run many trials.
- Count how often each permutation appears.
- Estimate P_k(σ) ≈ count(σ)/trials.

2) **Uniform distribution over orderings**
- In a perfectly random deck, every ordering has probability:
  U(σ) = 1 / 8!.

3) **Total Variation (TV) distance**
We compute TV distance over the full permutation space S_8:

TV(P_k, U) = (1/2) * Σ_{σ in S_8} |P_k(σ) - U(σ)|

Interpretation:
- TV = 0 means P_k matches uniform randomness.
- Larger TV means the shuffled distribution is easier to distinguish from uniform.

Implementation note:
We do NOT loop over all 8! permutations to compute TV.
Unseen permutations have empirical probability 0, so each contributes |0 - 1/8!|.

## Extra per-shuffle stats (easy to explain)
The script also prints:
- Example ordering (one run)
- Average rising sequences (runs) = 1 + (# descents)
- Average fixed points
- Average displacement from the original ordering
- Most common orderings (top of the empirical distribution)

## Run

Python 3.9+ (standard library only)

```bash
python riffle_tv_8.py