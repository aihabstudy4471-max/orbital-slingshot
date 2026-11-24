"""Level checker: brute-forces shots to prove every level can be beaten.

    python tools/solve_levels.py          # check all levels
    python tools/solve_levels.py 3        # check level 3 only

For each level it prints how many shots win (a rough difficulty measure),
the best star count possible, and an example winning shot.
Uses the exact same physics as the game (classes.Probe.update).
"""
import math
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

from classes import Probe, build_level, MAX_LAUNCH_SPEED, FPS   # noqa: E402
from levels import LEVELS                                         # noqa: E402

SCREEN = (1000, 700)
ANGLE_STEP = 2          # degrees
POWERS = [p / 40 for p in range(6, 41)]   # 0.15 .. 1.0


def simulate(level_index, angle_deg, power):
    data = LEVELS[level_index]
    planets, target, stars = build_level(data)
    a = math.radians(angle_deg)
    speed = power * MAX_LAUNCH_SPEED
    probe = Probe(*data['start'], math.cos(a) * speed, math.sin(a) * speed)
    while probe.state == 'flying':
        probe.update(planets, target, stars, SCREEN, 1.0 / FPS)
    return probe.state, probe.stars_this_shot, angle_deg, power


def check(level_index):
    jobs = [(level_index, a, p) for a in range(0, 360, ANGLE_STEP) for p in POWERS]
    with Pool() as pool:
        results = pool.starmap(simulate, jobs)
    wins = [r for r in results if r[0] == 'won']
    best = max(wins, key=lambda r: r[1]) if wins else None
    name = LEVELS[level_index]['name']
    pct = 100 * len(wins) / len(results)
    if not best:
        print('Level %d %-18s  UNBEATABLE (0 winning shots)' % (level_index + 1, name))
        return False
    print('Level %d %-18s  %5.1f%% of shots win | best stars %d/%d | e.g. angle %d deg, power %.2f'
          % (level_index + 1, name, pct, best[1], len(LEVELS[level_index].get('stars', [])), best[2], best[3]))
    return True


if __name__ == '__main__':
    which = [int(a) - 1 for a in sys.argv[1:]] or range(len(LEVELS))
    ok = all([check(i) for i in which])
    sys.exit(0 if ok else 1)
