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

BOSS LEVELS: same format, but no 'target' or 'stars'. Add 'probes' and a 'boss' section:
  probes   : how many probes you get before the fight restarts
  boss     :
      pos         : (x, y) centre point it hovers around (keep it on the right, x ~800)
      hp          : boss health. Eye hit = 1 damage
      hover_range : how far up/down it moves (pixels)
      hover_time  : seconds for one full up-and-down
      claw_every  : seconds between a claw starting to glow
      claw_window : seconds you have to hit the glowing claw before it attacks (-1 probe)
      claw_damage : damage for hitting a glowing claw
      mass        : boss gravity (0 = none, ~4000 = gentle pull)
      color       : optional skin colour (r, g, b) for the placeholder art
      eye_color   : optional iris colour (r, g, b)

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
    # ---- Level 6
    {
        'name': 'Gravity Well',
        'hint': 'Swing round the big one',
        'start': (100, 600),
        'target': (110, 110, 30),
        'planets': [
            {'pos': (340, 350), 'radius': 55, 'mass': 16000, 'color': (230, 120, 70)},
            {'pos': (110, 350), 'radius': 35, 'mass': 4000, 'color': (170, 170, 185)},
        ],
        'stars': [(496, 161), (660, 379), (375, 530)],
    },
    # ---- Level 7
    {
        'name': 'Figure Eight',
        'start': (870, 600),
        'target': (130, 110, 30),
        'planets': [
            {'pos': (350, 350), 'radius': 45, 'mass': 12000, 'color': (120, 220, 140)},
            {'pos': (650, 350), 'radius': 45, 'mass': 12000, 'color': (230, 120, 70)},
        ],
        'stars': [(889, 368), (478, 370), (101, 295)],
    },
    # ---- Level 8
    {
        'name': 'Heavy Metal',
        'hint': 'Small, but very heavy',
        'start': (100, 200),
        'target': (100, 500, 30),
        'planets': [
            {'pos': (520, 350), 'radius': 16, 'mass': 55000, 'color': (235, 235, 255)},
            {'pos': (100, 350), 'radius': 40, 'mass': 3000, 'color': (170, 170, 185)},
        ],
        'stars': [(450, 642), (762, 273), (303, 125)],
    },
    # ---- Level 9
    {
        'name': 'Dark Corridor',
        'hint': 'Two black holes. Good luck',
        'start': (100, 350),
        'target': (900, 350, 26),
        'planets': [
            {'pos': (380, 290), 'radius': 20, 'mass': 42000, 'color': (20, 10, 30), 'kind': 'blackhole'},
            {'pos': (620, 410), 'radius': 20, 'mass': 42000, 'color': (20, 10, 30), 'kind': 'blackhole'},
            {'pos': (500, 120), 'radius': 30, 'mass': 4000, 'color': (170, 170, 185)},
            {'pos': (500, 580), 'radius': 30, 'mass': 4000, 'color': (170, 170, 185)},
        ],
        'stars': [(452, 369), (795, 207), (927, 252)],
    },
    # ---- Level 10
    {
        'name': 'Asteroid Alley',
        'hint': 'Thread the needle',
        'start': (90, 350),
        'target': (910, 350, 30),
        'planets': [
            {'pos': (300, 285), 'radius': 22, 'mass': 2500, 'color': (170, 170, 185)},
            {'pos': (390, 420), 'radius': 24, 'mass': 2800, 'color': (170, 170, 185)},
            {'pos': (500, 300), 'radius': 22, 'mass': 2500, 'color': (170, 170, 185)},
            {'pos': (610, 425), 'radius': 26, 'mass': 3000, 'color': (170, 170, 185)},
            {'pos': (720, 290), 'radius': 22, 'mass': 2500, 'color': (170, 170, 185)},
        ],
        'stars': [(308, 258), (548, 459), (784, 458)],
    },
    # ---- Level 11
    {
        'name': 'Clockwork',
        'hint': 'Time it right',
        'start': (90, 350),
        'target': (910, 350, 30),
        'planets': [
            {'pos': (500, 350), 'radius': 40, 'mass': 9000, 'color': (240, 200, 90)},
            {'pos': (660, 350), 'radius': 28, 'mass': 5000, 'color': (80, 200, 200), 'orbit': (500, 350, 160, 10.0)},
            {'pos': (420, 489), 'radius': 28, 'mass': 5000, 'color': (80, 200, 200), 'orbit': (500, 350, 160, 10.0)},
            {'pos': (420, 211), 'radius': 28, 'mass': 5000, 'color': (80, 200, 200), 'orbit': (500, 350, 160, 10.0)},
        ],
        'stars': [(265, 167), (509, 86), (768, 181)],
    },
    # ---- Level 12
    {
        'name': 'Pinball',
        'start': (90, 350),
        'target': (910, 350, 30),
        'planets': [
            {'pos': (320, 200), 'radius': 26, 'mass': 3500, 'color': (120, 220, 140)},
            {'pos': (320, 500), 'radius': 26, 'mass': 3500, 'color': (120, 220, 140)},
            {'pos': (500, 350), 'radius': 30, 'mass': 4500, 'color': (90, 150, 255)},
            {'pos': (680, 200), 'radius': 26, 'mass': 3500, 'color': (120, 220, 140)},
            {'pos': (680, 500), 'radius': 26, 'mass': 3500, 'color': (120, 220, 140)},
            {'pos': (500, 110), 'radius': 22, 'mass': 3000, 'color': (240, 200, 90)},
            {'pos': (500, 590), 'radius': 22, 'mass': 3000, 'color': (240, 200, 90)},
        ],
        'stars': [(195, 509), (452, 511), (729, 398)],
    },
    # ---- Level 13
    {
        'name': 'Long Way Round',
        'hint': 'Straight is not an option',
        'start': (140, 350),
        'target': (880, 350, 28),
        'planets': [
            {'pos': (520, 350), 'radius': 115, 'mass': 22000, 'color': (220, 80, 70)},
            {'pos': (520, 160), 'radius': 18, 'mass': 1500, 'color': (170, 170, 185), 'orbit': (520, 350, 190, 8.0)},
        ],
        'stars': [(301, 179), (521, 115), (752, 195)],
    },
    # ---- Level 14
    {
        'name': 'The Needle',
        'start': (100, 600),
        'target': (900, 110, 30),
        'planets': [
            {'pos': (500, 160), 'radius': 100, 'mass': 14000, 'color': (80, 200, 200)},
            {'pos': (500, 540), 'radius': 100, 'mass': 14000, 'color': (200, 110, 230)},
        ],
        'stars': [(239, 452), (594, 333), (848, 218)],
    },
    # ---- Level 15
    {
        'name': 'Binary Star',
        'hint': 'Two worlds, one dance',
        'start': (100, 520),
        'target': (900, 180, 30),
        'planets': [
            {'pos': (590, 350), 'radius': 34, 'mass': 7000, 'color': (240, 200, 90), 'orbit': (500, 350, 90, 6.0)},
            {'pos': (410, 350), 'radius': 34, 'mass': 7000, 'color': (240, 120, 170), 'orbit': (500, 350, 90, 6.0)},
        ],
        'stars': [(366, 588), (634, 536), (824, 361)],
    },
    # ---- Level 16
    {
        'name': 'Crossfire',
        'start': (100, 600),
        'target': (900, 100, 30),
        'planets': [
            {'pos': (550, 350), 'radius': 32, 'mass': 7000, 'color': (220, 80, 70), 'orbit': (400, 350, 150, 6.0)},
            {'pos': (450, 350), 'radius': 32, 'mass': 7000, 'color': (90, 150, 255), 'orbit': (600, 350, 150, -6.0)},
        ],
        'stars': [(246, 621), (476, 482), (682, 212)],
    },
    # ---- Level 17
    {
        'name': 'Moonfall',
        'hint': 'Watch the moons',
        'start': (100, 600),
        'target': (900, 100, 30),
        'planets': [
            {'pos': (500, 350), 'radius': 50, 'mass': 12000, 'color': (90, 150, 255)},
            {'pos': (630, 350), 'radius': 16, 'mass': 1800, 'color': (170, 170, 185), 'orbit': (500, 350, 130, 5.0)},
            {'pos': (300, 350), 'radius': 20, 'mass': 2200, 'color': (170, 220, 255), 'orbit': (500, 350, 200, 9.0)},
        ],
        'stars': [(199, 330), (410, 110), (695, 85)],
    },
    # ---- Level 18
    {
        'name': 'Singularity',
        'hint': 'Everything falls in eventually',
        'start': (100, 600),
        'target': (900, 100, 30),
        'planets': [
            {'pos': (500, 350), 'radius': 20, 'mass': 48000, 'color': (20, 10, 30), 'kind': 'blackhole'},
            {'pos': (660, 350), 'radius': 20, 'mass': 2500, 'color': (170, 170, 185), 'orbit': (500, 350, 160, 6.0)},
            {'pos': (260, 350), 'radius': 24, 'mass': 3000, 'color': (170, 220, 255), 'orbit': (500, 350, 240, -9.0)},
        ],
        'stars': [(180, 304), (398, 103), (681, 56)],
    },
    # ---- Level 19
    {
        'name': 'Labyrinth',
        'hint': 'Down, then up',
        'start': (100, 350),
        'target': (900, 350, 30),
        'planets': [
            {'pos': (330, 90), 'radius': 48, 'mass': 6000, 'color': (200, 110, 230)},
            {'pos': (330, 215), 'radius': 48, 'mass': 6000, 'color': (200, 110, 230)},
            {'pos': (330, 340), 'radius': 48, 'mass': 6000, 'color': (200, 110, 230)},
            {'pos': (330, 465), 'radius': 48, 'mass': 6000, 'color': (200, 110, 230)},
            {'pos': (650, 610), 'radius': 48, 'mass': 6000, 'color': (80, 200, 200)},
            {'pos': (650, 485), 'radius': 48, 'mass': 6000, 'color': (80, 200, 200)},
            {'pos': (650, 360), 'radius': 48, 'mass': 6000, 'color': (80, 200, 200)},
            {'pos': (650, 235), 'radius': 48, 'mass': 6000, 'color': (80, 200, 200)},
        ],
        'stars': [(272, 532), (563, 226), (839, 188)],
    },
    # ---- Level 20
    {
        'name': 'Grand Tour',
        'hint': 'The final test',
        'start': (90, 120),
        'target': (910, 610, 24),
        'planets': [
            {'pos': (480, 320), 'radius': 20, 'mass': 40000, 'color': (20, 10, 30), 'kind': 'blackhole'},
            {'pos': (230, 470), 'radius': 45, 'mass': 10000, 'color': (120, 220, 140)},
            {'pos': (650, 320), 'radius': 18, 'mass': 2200, 'color': (170, 170, 185), 'orbit': (480, 320, 170, 7.0)},
            {'pos': (480, 560), 'radius': 22, 'mass': 2600, 'color': (170, 220, 255), 'orbit': (480, 320, 240, -10.0)},
            {'pos': (790, 470), 'radius': 48, 'mass': 12000, 'color': (230, 120, 70)},
            {'pos': (740, 130), 'radius': 34, 'mass': 6000, 'color': (90, 150, 255)},
            {'pos': (900, 400), 'radius': 26, 'mass': 3500, 'color': (240, 120, 170)},
        ],
        'stars': [(233, 339), (451, 567), (703, 645)],
    },

    # ================================================================== BOSSES
    # Boss levels go at the bottom. Same format, plus 'probes' and a 'boss' section.
    # ---- Boss 1
    {
        'name': 'The Watcher',
        'hint': 'Hit the eye! When a claw glows, hit it fast for big damage',
        'start': (100, 350),
        'probes': 11,
        'planets': [
            {'pos': (420, 190), 'radius': 45, 'mass': 9000, 'color': (90, 150, 255)},
            {'pos': (440, 520), 'radius': 40, 'mass': 8000, 'color': (230, 120, 70)},
        ],
        'boss': {
            'pos': (800, 350),
            'hp': 5,
            'hover_range': 110,
            'hover_time': 5.0,
            'claw_every': 8.0,
            'claw_window': 4.0,
            'claw_damage': 2,
            'mass': 4000,
        },
    },
    # ---- Boss 2
    {
        'name': 'The Crimson Maw',
        'hint': 'It moves faster. So should you',
        'start': (100, 350),
        'probes': 10,
        'planets': [
            {'pos': (400, 170), 'radius': 40, 'mass': 9000, 'color': (230, 120, 70)},
            {'pos': (420, 530), 'radius': 40, 'mass': 9000, 'color': (240, 200, 90)},
            {'pos': (560, 260), 'radius': 18, 'mass': 2000, 'color': (170, 170, 185), 'orbit': (560, 350, 90, 5.0)},
        ],
        'boss': {
            'pos': (800, 350),
            'hp': 6,
            'hover_range': 130,
            'hover_time': 4.2,
            'claw_every': 7.0,
            'claw_window': 3.5,
            'claw_damage': 2,
            'mass': 5000,
            'color': (200, 60, 60),
            'eye_color': (255, 200, 40),
        },
    },
    # ---- Boss 3
    {
        'name': 'The Frost Seer',
        'hint': 'Its moons guard it',
        'start': (100, 350),
        'probes': 11,
        'planets': [
            {'pos': (590, 350), 'radius': 24, 'mass': 4000, 'color': (170, 220, 255), 'orbit': (450, 350, 140, 8.0)},
            {'pos': (380, 471), 'radius': 24, 'mass': 4000, 'color': (170, 220, 255), 'orbit': (450, 350, 140, 8.0)},
            {'pos': (380, 229), 'radius': 24, 'mass': 4000, 'color': (170, 220, 255), 'orbit': (450, 350, 140, 8.0)},
        ],
        'boss': {
            'pos': (800, 350),
            'hp': 7,
            'hover_range': 150,
            'hover_time': 3.6,
            'claw_every': 6.5,
            'claw_window': 3.0,
            'claw_damage': 2,
            'mass': 5000,
            'color': (120, 190, 230),
            'eye_color': (40, 80, 200),
        },
    },
    # ---- Boss 4
    {
        'name': 'The Void Lord',
        'hint': 'It hides behind a black hole',
        'start': (100, 350),
        'probes': 12,
        'planets': [
            {'pos': (470, 300), 'radius': 18, 'mass': 22000, 'color': (20, 10, 30), 'kind': 'blackhole'},
            {'pos': (300, 130), 'radius': 35, 'mass': 6000, 'color': (200, 110, 230)},
            {'pos': (300, 570), 'radius': 35, 'mass': 6000, 'color': (200, 110, 230)},
        ],
        'boss': {
            'pos': (800, 350),
            'hp': 8,
            'hover_range': 160,
            'hover_time': 3.2,
            'claw_every': 6.0,
            'claw_window': 2.6,
            'claw_damage': 2,
            'mass': 6000,
            'color': (130, 70, 190),
            'eye_color': (60, 255, 180),
        },
    },
    # ---- Boss 5
    {
        'name': 'The Solar Tyrant',
        'hint': 'The final boss. Everything you have learned',
        'start': (100, 350),
        'probes': 13,
        'planets': [
            {'pos': (460, 350), 'radius': 16, 'mass': 26000, 'color': (20, 10, 30), 'kind': 'blackhole'},
            {'pos': (610, 350), 'radius': 18, 'mass': 2200, 'color': (170, 170, 185), 'orbit': (460, 350, 150, 6.0)},
            {'pos': (230, 350), 'radius': 22, 'mass': 2600, 'color': (240, 200, 90), 'orbit': (460, 350, 230, -9.0)},
            {'pos': (250, 140), 'radius': 30, 'mass': 5000, 'color': (220, 80, 70)},
        ],
        'boss': {
            'pos': (800, 350),
            'hp': 9,
            'hover_range': 170,
            'hover_time': 2.8,
            'claw_every': 5.5,
            'claw_window': 2.3,
            'claw_damage': 2,
            'mass': 7000,
            'color': (235, 150, 40),
            'eye_color': (150, 0, 20),
        },
    },
]
