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
  Boss levels live in the SAME list (they have a `'boss'` section, no `'target'`/`'stars'`).
  The user wants it kept this way – no separate boss file.
- `level_select.py` – level select grid. Every level is playable (no locking, user's choice).
  Normal levels and boss levels (any level with `'boss'`) get separate rows. Stars are kept in
  memory only – no save file yet (user said not yet).
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
`title` -> `select` (level grid) -> `aim` -> `flying` -> `won` (next level) / `crashed` (auto reset
after a delay) -> `finished` after the last level. Boss levels add `boss_failed` (out of probes).
Esc: level -> select -> title -> quit.

## Boss fight
- `Boss` class in classes.py: hovers up/down, circle hitboxes (eye in front, body behind, two claws).
- Eye hit = 1 damage. A claw glows every `claw_every` s; hit it within `claw_window` s for
  `claw_damage`, or it attacks and you lose a probe. Body / non-glowing claw = probe destroyed.
- Limited `probes` per fight; run out -> `boss_failed` -> click to restart the fight.
- Boss has weak gravity (`mass`, default 4000). Same alien every boss level, made harder via numbers.
- Art: separate pieces in assets/boss/ (see assets/README.md); placeholder shapes until then.
- Boss levels are NOT deterministic (boss moves while aiming) – that's intended.
  The solver checks the eye can be hit with the boss frozen at its centre point.

## Controls
Mouse drag from anywhere = pull back + release. R = reset shot. Enter/Space/click = continue.
Esc = back. Debug: F1 = show full predicted path, F2 = skip level (user's keyboard has no F-keys
without Fn – they may rebind these to letters).

## Working with the user
- The user is learning; they want to understand the code and write some of it themselves.
  Explain where things go, and offer "fill in the blanks" versions when they ask.
- They added the gravity number label + `draw_gravity_rings` (their own values) in main.py.

## Status / TODO
- [x] Day 1 prototype: launching, gravity, collisions, win/lose, stars, 5 test levels, solver
- [x] Gravity number on planets + gravity rings (user)
- [x] Level select screen (all unlocked, in-memory stars)
- [x] Boss fight: "The Watcher" (Level 6), placeholder art
- [ ] More levels (aim for 12-15 normal + ~3 bosses; user wanted 20 + 5, scope warning given)
- [ ] Saving best stars to a file (later)
- [ ] Drop in designer's art + sounds + music (see assets/README.md)
- [ ] Polish: menus, transitions, juice
- [ ] Build/package for submission (leave the last day free for this)

Update this file at the end of each session with what changed and what's next.
