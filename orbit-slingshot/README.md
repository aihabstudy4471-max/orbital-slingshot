# Orbit Slingshot

A space physics puzzle game made for a game jam (theme: *Out of this world*).
Launch your probe and use the gravity of planets to slingshot it into the target.

## Run it

```bash
pip install pygame
python main.py
```

## Controls

| Input | Action |
|---|---|
| Click + drag, release | Pull back and launch the probe |
| R | Reset the shot |
| Enter / Space / Click | Continue |
| Esc | Back to title / quit |

## Making levels

Levels live in `levels.py` (the format is explained at the top of that file).
After changing them, check they can all be beaten:

```bash
python tools/solve_levels.py
```
