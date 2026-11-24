"""Level data. Add a new level by adding a dict to LEVELS.

Screen is 1000 x 700. Coordinates are pixels, (0, 0) is top-left.

  start    : where the probe launches from
  target   : (x, y, radius) - reach this to win
  planets  : list of planets
      pos    : (x, y)
      radius : size in pixels (also the crash hitbox)
      mass   : gravity strength. ~8000 gentle, ~15000 strong, 40000+ black hole
      color  : (r, g, b) used when there's no sprite
      kind   : 'planet' (default) or 'blackhole'
      sprite : optional image name in assets/planets/ (e.g. 'lava' -> assets/planets/lava.png)
      orbit  : optional moving planet: (centre_x, centre_y, orbit_radius, seconds_per_lap)
  stars    : optional collectibles [(x, y), ...] - 3 per level for the star rating
  hint     : optional text shown at the bottom of the screen

Run  python tools/solve_levels.py  after editing to check every level can be beaten.
"""

LEVELS = [
    {
        'name': 'First Contact',
        'hint': 'Drag back from the probe and release to launch',
        'start': (130, 350),
        'target': (870, 350, 40),
        'planets': [
            {'pos': (500, 350), 'radius': 55, 'mass': 9000, 'color': (90, 150, 255)},
        ],
        'stars': [(500, 210), (660, 250), (330, 250)],
    },
    {
        'name': 'Around the Bend',
        'hint': 'Gravity bends your path - use it',
        'start': (120, 580),
        'target': (130, 140, 32),
        'planets': [
            {'pos': (420, 360), 'radius': 60, 'mass': 14000, 'color': (230, 120, 70)},
            {'pos': (150, 360), 'radius': 30, 'mass': 3000, 'color': (150, 150, 170)},
        ],
        'stars': [(600, 470), (620, 260), (400, 160)],
    },
    {
        'name': 'Twin Worlds',
        'start': (100, 120),
        'target': (900, 600, 30),
        'planets': [
            {'pos': (380, 330), 'radius': 50, 'mass': 11000, 'color': (120, 220, 140)},
            {'pos': (640, 400), 'radius': 50, 'mass': 11000, 'color': (200, 110, 230)},
        ],
        'stars': [(510, 360), (300, 200), (780, 520)],
    },
    {
        'name': 'Moon Run',
        'hint': 'Some things move...',
        'start': (110, 600),
        'target': (880, 120, 30),
        'planets': [
            {'pos': (500, 380), 'radius': 60, 'mass': 13000, 'color': (90, 170, 220)},
            {'pos': (690, 380), 'radius': 20, 'mass': 2500, 'color': (210, 210, 220),
             'orbit': (500, 380, 190, 7.0)},
        ],
        'stars': [(340, 599), (702, 490), (861, 314)],
    },
    {
        'name': 'Event Horizon',
        'hint': "Don't get too close to the black hole",
        'start': (100, 350),
        'target': (900, 350, 30),
        'planets': [
            {'pos': (500, 350), 'radius': 22, 'mass': 42000, 'color': (20, 10, 30), 'kind': 'blackhole'},
            {'pos': (500, 110), 'radius': 35, 'mass': 5000, 'color': (240, 200, 90)},
            {'pos': (500, 590), 'radius': 35, 'mass': 5000, 'color': (240, 200, 90)},
        ],
        'stars': [(330, 230), (500, 470), (680, 230)],
    },
]
