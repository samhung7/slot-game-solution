## Summay

This project designs a set of 3 reels with **RTP exactly 19/20 - 0.95** and a **win rate of 2819/4655 ≈ 60.56**. Both values are verified by exact enumeration of all 46,550 stop combinations and cross-checked with a 2-million-spin Monte Carlo simulation.

- **Reel 1 and Reel 3** (35 stops each): 0x21, 1x2, 2x2, 3x2, 4x8
- **Reel 2 (38 stops): 0x24, 1x2, 2x4, 3x2, 4x6

The design follows a "many small wins + few big wins" pattern:

- Symbol 0 appears in about 53% of spins and carries the win rate.
- Symbol 4 appears in about 6% of spins but contributes more than half of the RTP.

The exact RTP comes from solving a linear congruence, not from trial-and-error approximation.

## Problem Interpretation

The task is to produce the symbol layout of 3 reels such that the machine satisfies RTP = 0.95 and win rate >= 55%.

| Item | Description |
| --- | --- |
| Reel model | Each column is an independent circular reel. Every stop position is equally likely. A stop shows 3 consecutive symbols, wrapping from the end back to the start. |
| Winning patterns | Four 2x2 squares (4.1 top-left, 4.2 top-right, 4.3 bottom-left, 4.4 bottom-right) and the full 3x3 screen (4.5). |
| 2x2 payout | Each 2x2 hit pays bet x multiplier. Multiple 2x2 hits in one spin add up. |
| Full-screen payout | Not stacked: a full screen pays only bet x multiplier x 5. The four 2x2 squares it contains are not paid on top. |
| Win definition | A spin counts as a win if its payout is greater than 0. This includes small wins that pay less than the bet. |
| RTP | Theoretical value, computed exactly with fractions. With a bet of 100, the expected return is 95. |

Multipliers: `{0: 0.25, 1: 0.55, 2: 1, 3: 3, 4: 5}`.

## Derivation

### Key obseration: every pattern contains the center cell

All four 2x2 squares and the full screen include the center cell. So all winning patterns in a single spin must be the same symbol *s*: the symbol in the center cell. Each symbol can therefore be analyzed separately and the results summed.

### Window categories per reel

For reel *i* (i = 1, 2, 3) and symbol *s*, classify the visible 3-cell window (top, middle, bottom) into three categories:

- **a_i(s)**: probability that all three cells are *s*
- **u_i(s)**: probability that top and middle are *s*, and bottom is not
- **d_i(s)**: probability that middle and bottom are *s*, and top is not

Define three derived quantities:

- **U_i = a_i + u_i**: top and middle are *s*
- **D_i = a_i + d_i**: middle and bottom are *s*
- **q_i = a_i + u_i + d_i**: at least one vertical pair of *s*

The reels are independent, so:

- P(4.1) = U_1⋅U_2
- P(4.2) = U_2⋅U_3
- P(4.3) = U_1⋅U_2
- P(4.4) = U_2⋅U_3
- P(4.5) = a_1⋅a_2⋅a_3

### RTP formula

When the full screen hits, all four 2x2 squares hit as well. Without stacking, the full screen pays 5m. This equals the four 2x2 squares' 4m plus an extra 1m. With m_s as the multiplier of symbol *s*.

$$
\mathrm{RTP} = \sum_{s=0}^{4} m_s \left( U_1U_2 + U_2U_3 + D_1D_2 + D_2D_3 + a_1a_2a_3 \right)
$$

### Win-rate formula

Split by the state of the middle reel:

- **Middle reel in category A**: any vertical pair of *s* on either side reel produces a win.
- **Middle reel in category U**: only the two top 2x2 squares can hit.
- **Middle reel in category D**: only the two bottom 2x2 squares can hit.

$$
P(\text{win}) = \sum_{s=0}^{4} \Big[ a_2\big(1-(1-q_1)(1-q_3)\big) + u_2\big(1-(1-U_1)(1-U_3)\big) + d_2\big(1-(1-D_1)(1-D_3)\big) \Big]
$$

### From reel layout to window probabilities

Consider a run of k consecutive *s* symbols on a reel (k >= 2), where both neighbors are not *s*. That run contributes:

- k − 2 windows of category A
- 1 window of category U
- 1 window of category D

A single isolated stop (k = 1) contributes no winning window. Dividing by the reel length L gives the probabilities. The whole problem therefore reduces to choosing the run length of each symbol on each reel.

## Solution Method

The two constraints pull against each other. The win rate must be at least 55%, but the total return is only 95%. So the average payout per winning spin cannot exceed about 0.95 / 0.55 ≈ 1.73 x bet.

The approach has three parts:

1. The low-multiplier symbol 0 generates many small wins.
2. High-multiplier symbols make up the remaining RTP.
3. A linear congruence pins the RTP to exactly 0.95.

### Feasibility: symbol 0 alone is not enough

Let ρ be the density of 0 on the outer reels. Each 0 A-window on the middle reel contributes roughly 0.25 × (4ρ + ρ²) to RTP. Reaching 0.95 with symbol 0 alone requires ρ ≈ 0.79 or higher. That design has three problems:

- The outer reels become almost all 0.
- The middle reel grows to 800+ stops.
- The win rate rises to about 96%, which is unrealistic.

The solution instead places **long runs of symbol 4 on all three reels**. Symbol 4 has a multiplier of 5, and its probabilities multiply across reels, so it contributes a lot of RTP. This lowers the density of 0 to about 60%, which is still enough to sustain the win rate.

### Exact solution: a linear congruence on the middle reel

Random search almost never lands on an RTP of exactly 0.95. The RTP denominator is on the order of 19 x L_1 x L_3.

The key insight: once the outer reels are fixed, RTP is **linear** in the counts of each window type on the middle reel. Let:

- n + 2 be the length of the middle reel's 0 run
- B be the total length of the remaining runs plus padding stops

Then there exist rationals α₀ and C, depending only on the outer reels, such that:

$$
L_2 \cdot \mathrm{RTP} = \alpha_0 \, n + C, \qquad L_2 = n + 2 + B
$$

Setting RTP = 19/20 imposes two requirements:

- (α₀ n + C) × 20/19 must be an integer L_2.
- L₂ must be at least n + 2 plus the other run lengths. Any gap is filled with single, non-paying padding stops.

This is a linear congruence in n of the form A·n + B ≡ 0 (mod M). The smallest valid n follows directly from a modular inverse.

### Search procedure

1. Randomly generate many outer-reel candidates: a 0 run of length 12–30, one run each of symbols 1–4, and allow long runs of 3 and 4.
2. For each outer-reel candidate, enumerate run-length combinations for symbols 1–4 on the middle reel.
3. Solve the congruence for n. Keep only solutions where the padding count is >= 0 and the win rate is >= 55%.
4. Across 5,658 outer-reel candidates, the search found 541 exact solutions. The chosen solution has a short total length and a comfortable win-rate margin.

## Final Reel Configuration

Reel 1 and Reel 3 are identical (35 stops each). Reel 2 has 38 stops. Total combinations: 35 × 38 × 35 = 46,550.

Each reel joins its runs end to end in a circle. Adjacent runs always have different symbols, so no runs accidentally merge into a longer run.

| Symbol (multiplier) | Reel 1 stops | Reel 2 stops | Reel 3 stops |
| --- | --- | --- | --- |
| 0 (×0.25) | 21 | 24 | 21 |
| 1 (×0.55) | 2 | 2 | 2 |
| 2 (×1) | 2 | 4 | 2 |
| 3 (×3) | 2 | 2 | 2 |
| 4 (×5) | 8 | 6 | 8 |
| **Total** | **35** | **38** | **35** |

Full sequences:

```
Reel 1 / Reel 3 = [0]*21 + [1]*2 + [2]*2 + [3]*2 + [4]*8
Reel 2          = [0]*24 + [1]*2 + [2]*4 + [3]*2 + [4]*6
```

## Verification Results

Both constraints hold. Exact enumeration gives RTP = 19/20 = 0.95 and a win rate of ≈ 60.56%, which is >= 55%.

The verification is independent of the derivation above. It does not use the formulas. Instead it:

- generates each of the 46,550 screens one by one
- checks all five patterns directly
- uses Python's `Fraction` for exact arithmetic

| Metric | Exact enumeration | Monte Carlo (2M spins, bet 100) |
| --- | --- | --- |
| RTP | 19/20 = 0.9500000000 | 0.9477 |
| Win rate (payout > 0) | 2819/4655 ≈ 60.5585% | 60.6024% |
| P(payout ≥ bet) | 24.40% | — |

The Monte Carlo results match the theoretical values within sampling error.

### Contribution by symbol

| Symbol (multiplier) | RTP contribution | Hit frequency |
| --- | --- | --- |
| 0 (×0.25) | 38.85% | 52.93% |
| 1 (×0.55) | 0.17% | 0.30% |
| 2 (×1) | 0.90% | 0.88% |
| 3 (×3) | 0.90% | 0.30% |
| 4 (×5) | 54.18% | 6.16% |
| **Total** | **95.00%** | **60.56%** |

Symbol 0 appears in about 53% of spins and carries the win rate. Each hit returns only 0.25× (a single 2×2) up to 1.25× (full screen), so most of these are "wins" that still lose money.

Symbol 4 appears in only about 6% of spins but contributes more than half of the RTP. It acts as the big win.

## Code and Reproduction

The verification script is `solution.py`. It uses only the Python standard library and runs in about 8 seconds:

```
python3 solution.py
```

| Function | Purpose |
| --- | --- |
| `run()` | Builds a reel sequence from (symbol, count) pairs |
| `screen()` | Produces the 3×3 screen for given stop positions on the three reels, with circular indexing |
| `payout()` | Checks patterns 4.1–4.5 and returns the payout multiple. A full screen pays only 5×, with no stacking. |
| `exact()` | Enumerates all 46,550 combinations and computes RTP, win rate, and per-symbol contributions exactly with `Fraction` |
| `simulate()` | Monte Carlo simulation (default: 2M spins, seed 42, bet 100) |
| `spin()` | Spins the machine once, prints the 3×3 screen with winning cells in `[ ]`, the patterns hit and the payout, and returns the result as a dict |

The verification run ends with `assert` checks that RTP == 95/100 and win rate ≥ 55/100. It raises an error if either condition fails.

### Playing a spin

```
python3 solution.py spin      # one spin
python3 solution.py spin 5    # five spins
```

Example output:

```
Stops: [16, 32, 31]
+-----+-----+-----+
|  0  | [4] | [4] |
+-----+-----+-----+
|  0  | [4] | [4] |
+-----+-----+-----+
|  0  | [4] | [4] |
+-----+-----+-----+
WIN  symbol 4 (x5.0) x 2 pattern(s): 4.2 top-right 2x2, 4.4 bottom-right 2x2
Bet 100  ->  Payout 1000  (net +900)
```

`spin()` can also be called from Python. Pass `bet=` to change the stake, `rng=random.Random(seed)` for a repeatable result, or `show=False` to get only the returned dict.
