from fractions import Fraction
from collections import defaultdict
import random

MULT = {0: Fraction(1, 4), 1: Fraction(11, 20), 2: Fraction(1), 3: Fraction(3), 4: Fraction(5)}

def run(*blocks):
    """ Run-length helper: run((0, 22), (1, 2)) -> [0]*22 + [1]*2. """
    return [s for s, k in blocks for _ in range(k)]


# Reel 1 and Reel 3 (35 stops each), Reel 2 (38 stops)
REEL_OUTER = run((0, 21), (1, 2), (2, 2), (3, 2), (4, 8))
REEL_MIDDLE = run((0, 24), (1, 2), (2, 4), (3, 2), (4, 6))
REELS = [REEL_OUTER, REEL_MIDDLE, REEL_OUTER]


def screen(reels, stops):
    """ 3x3 grid [row][col] for the given stop positions. """
    return [[reels[c][(stops[c] + r) % len(reels[c])] for c in range(3)] for r in range(3)]


def payout(g):
    """ Payout as a multiple of bet, plus which patterns hit. """
    s = g[1][1]
    # every pattern contains the centre cell
    sq = lambda r, c: g[r][c] == g[r][c + 1] == g[r + 1][c] == g[r + 1][c + 1] == s
    # 4.1, 4.2, 4.3, 4.4
    hits = [sq(0, 0), sq(0, 1), sq(1, 0), sq(1, 1)]
    full = all(x == s for row in g for x in row)
    m = MULT[s]
    if full:
        # full screen: x5 only, 2x2 not stacked
        return m * 5, s, hits, full
    return m * sum(hits), s, hits, full


def exact(reels):
    L = [len(r) for r in reels]
    total = L[0] * L[1] * L[2]
    pay_sum, wins = Fraction(0), 0
    by_sym = defaultdict(lambda: [Fraction(0), 0])
    big_wins = 0

    for i in range(L[0]):
        for j in range(L[1]):
            for k in range(L[2]):
                pay, sym, _, _ = payout(screen(reels, (i, j, k)))
                if pay:
                    pay_sum += pay
                    wins += 1
                    by_sym[sym][0] += pay
                    by_sym[sym][1] += 1
                    if pay >= 1:
                        big_wins += 1

    return pay_sum / total, Fraction(wins, total), Fraction(big_wins, total), by_sym, total


def simulate(reels, n=2_000_000, seed=42, bet=100):
    rng = random.Random(seed)
    L = [len(r) for r in reels]
    paid = wins = 0.0

    for _ in range(n):
        p = payout(screen(reels, [rng.randrange(x) for x in L]))[0]
        paid += float(p) * bet
        wins += p > 0

    return paid / (n * bet), wins / n


PATTERN_NAMES = ("4.1 top-left 2x2", "4.2 top-right 2x2", "4.3 bottom-left 2x2", "4.4 bottom-right 2x2")


def spin(bet=100, reels=REELS, rng=None, show=True):
    """
    Spin once: pick a random stop on each reel, print the 3x3 screen and the result.

    Returns a dict with the stops, grid, winning patterns and payout (in bet units, e.g. 25.0 for bet=100).
    Winning cells are marked with [ ] in the printed screen.
    """
    rng = rng or random
    stops = [rng.randrange(len(r)) for r in reels]
    g = screen(reels, stops)
    mult, s, hits, full = payout(g)
    win = bet * float(mult)

    if full:
        patterns = ["4.5 full screen"]
        cells = {(r, c) for r in range(3) for c in range(3)}
    else:
        patterns = [name for name, h in zip(PATTERN_NAMES, hits) if h]
        corners = [(0, 0), (0, 1), (1, 0), (1, 1)]
        cells = {(r + dr, c + dc) for (r, c), h in zip(corners, hits) if h
                 for dr in (0, 1) for dc in (0, 1)}

    if show:
        line = "+-----+-----+-----+"
        print(f"Stops: {stops}")
        print(line)
        for r in range(3):
            row = "|".join(f"[{g[r][c]}]".center(5) if (r, c) in cells else f"{g[r][c]}".center(5)
                           for c in range(3))
            print(f"|{row}|")
            print(line)
        if patterns:
            note = " (x5)" if full else f" x {len(patterns)} pattern(s)"
            print(f"WIN  symbol {s} (x{float(MULT[s])}){note}: {', '.join(patterns)}")
        else:
            print("No Win")
        print(f"Bet {bet} ->  Payout {win:g} (net {win - bet:+g})")

    return {"stops": stops, "grid": g, "symbol": s, "patterns": patterns, "payout": win}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "spin":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        for i in range(n):
            if n > 1:
                print(f"\n=== Spin {i + 1} ===")
            spin()
        sys.exit()

    for name, r in zip(("Reel 1", "Reel 2", "Reel 3"), REELS):
        print(f"{name} ({len(r)} stops): {r}")
    rtp, win, big, by_sym, total = exact(REELS)
    print(f"\nTotal combinations : {total}")
    print(f"Exact RTP          : {rtp}  = {float(rtp):.10f}")
    print(f"Exact win rate     : {win}  = {float(win):.6%}")
    print(f"P(payout >= bet)   : {float(big):.4%}")
    print("\nPer-symbol breakdown (RTP contribution / hit frequency):")

    for s in sorted(by_sym):
        p, c = by_sym[s]
        print(f"  symbol {s} (x{float(MULT[s])}): RTP {float(p / total):.4%}  hits {c / total:.4%}")
    assert rtp == Fraction(95, 100), "RTP is not exactly 0.95"
    assert win >= Fraction(55, 100), "win rate below 55%"
    print("\nExact checks passed: RTP == 0.95, win rate >= 55%")

    sim_rtp, sim_win = simulate(REELS)
    print(f"Monte Carlo (2M spins, bet 100): RTP {sim_rtp:.4f}, win rate {sim_win:.4%}")
