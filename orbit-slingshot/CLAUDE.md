# Orbit Slingshot – project notes for Claude

## Context
- **Game jam entry**, theme: **"Out of this world"**. About one week total (started 2026-11-23).
- Team: **1 programmer** (me, the user) + **1 graphic designer**. Keep code simple and readable –
  the user is the only coder and needs to understand everything.
- Genre: Angry Birds-style physics puzzle. Launch a probe from a start point to reach a target;
  planets pull the probe with gravity so you curve around them instead of flying straight.
- Tech: **Python + pygame** (pygame 2.x). Window 1000x700, 60 FPS.
- Reference: my earlier pygame fighting game `A-Fighter` (in my other repo, `projects/A-Fighter`)
  uses a similar style – asset helpers with missing-file fallbacks, an `FX` class for particles/shake,
  main file + separate classes file.

## Files
- `main.py` – window, asset loading, `Game` class (states, input, drawing), main loop. Run this.
- `classes.py` – physics + game objects (`Planet`, `Target`, `Star`, `Probe`, `FX`). No window code,
  so it can be imported by tools.
- `levels.py` – all level data as plain dicts (format documented at the top of the file).
- `tools/solve_levels.py` – brute-forces shots to check every level is beatable and all stars are
  reachable. **Run after editing levels.**
- `assets/` – art/sound from the designer. Everything is optional; missing files fall back to drawn
  shapes. Expected filenames are in `assets/README.md`.

## How the physics works
- Each planet pulls with `a = G * mass / d^2` (`gravity_at` in classes.py), with `SOFTENING` so
  close passes don't explode.
- Fixed timestep: `SUBSTEPS` (4) physics steps per frame, semi-implicit Euler. Never tie physics to
  real frame time – the same shot must always give the same result (fairness + solver accuracy).
- Moving planets (`orbit` in level data) are frozen while aiming and only move after launch, for the
  same reason.
- The game and the solver both use `Probe.update()` – keep it that way so the solver stays truthful.
- Tuning constants are at the top of `classes.py` (launch speed, drag distance, flight time limit)
  and `main.py` (`PREVIEW_FRAMES` = how much of the aiming path is shown).

## Game states (Game.state in main.py)
`title` -> `aim` -> `flying` -> `won` (next level) / `crashed` (auto reset after a delay) ->
`finished` after the last level.

## Controls
Mouse drag from anywhere = pull back + release. R = reset shot. Enter/Space/click = continue.
Esc = title/quit. Debug: F1 = show full predicted path, F2 = skip level.

## Status / TODO
- [x] Day 1 prototype: launching, gravity, collisions, win/lose, stars, 5 test levels, solver
- [ ] Pick the "twist" mechanic (ideas: mid-flight fuel boost, repelling planets, wormholes,
      asteroid belts, multiple probes per level)
- [ ] More levels (aim for 12-20), ramping difficulty
- [ ] Level select screen + saving best stars to a file
- [ ] Drop in designer's art + sounds + music (see assets/README.md)
- [ ] Polish: menus, transitions, juice
- [ ] Build/package for submission (leave the last day free for this)

Update this file at the end of each session with what changed and what's next.
