# Riffle Shuffle Markov Chain Simulation (52 cards)

This project simulates **riffle shuffles** (the classic “riffle/ripple” shuffle) as a **Markov chain** on deck orderings.

A **state** is the full ordering of the deck (a permutation).  
Each riffle shuffle is one **Markov step**: the next ordering depends only on the current ordering.

## What this shows

For a 52-card deck, there are `52!` possible orderings, so we **cannot** list or store a probability for every ordering.

Instead, this simulation demonstrates mixing using **per-shuffle statistics** that are easy to interpret:

- **Example top 10 cards (one run)**  
  A human-readable “snapshot” of what the deck looks like after each shuffle.

- **Average rising sequences (runs)**  
  A classic diagnostic for riffle shuffles. A “run” starts each time the permutation descends.
  Runs = 1 + (# of descents).

- **Average fixed points**  
  How many cards stayed in their original position. A random permutation has ~1 fixed point on average.

- **Tracked-card position TV distance vs uniform**  
  For a chosen card `c`, we estimate the distribution of its position after `k` shuffles:
  - perfectly uniform would be `1/52` in each position
  - we compute **Total Variation (TV) distance** between the observed position distribution and uniform

  Important: this TV distance is for the observable “position of card c”, **not** for the full distribution over all `52!` permutations.

## Why TV distance?

Total variation distance between two distributions `P` and `U` on the same finite set is:

`TV(P, U) = (1/2) * sum_x |P(x) - U(x)|`

Interpretation:
- `TV = 0` means the distributions match
- larger TV means they are easier to distinguish

Here we use TV on **position distributions** (e.g., “where does card 1 land?”) so it’s computable and intuitive.

## Setup

Requires Python 3.9+ (standard library only).

## Run

```bash
python riffle_stats.py