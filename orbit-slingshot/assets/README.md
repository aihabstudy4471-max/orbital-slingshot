# Assets guide (for the designer)

Drop files in here with these names and the game picks them up automatically.
Anything missing just gets drawn as a simple shape, so add things whenever they're ready.
PNG with transparency is best for sprites. The file extension doesn't matter as long as the
name matches (`probe.png` and `probe.jpg` both work).

| File | What it is | Size it gets drawn at |
|---|---|---|
| `probe.png` | The probe. **Draw it pointing right** – the game rotates it to face where it's flying | 24 x 24 |
| `target.png` | The goal / landing zone | 80 x 80 |
| `star.png` | Collectible star | 26 x 26 |
| `background.png` | Full-screen background (replaces the generated starfield) | 1000 x 700 |
| `planets/<name>.png` | Planet images. A level chooses one with `'sprite': '<name>'` in levels.py | planet diameter (40–130px) |
| `fonts/main.ttf` | Font for all text | – |
| `music.ogg` | Looping background music | – |
| `sfx/launch.wav` | Probe launched | – |
| `sfx/crash.wav` | Probe hits a planet | – |
| `sfx/win.wav` | Target reached | – |
| `sfx/star.wav` | Star collected | – |

Tips
- Draw at 2–4x the listed size; the game scales it down smoothly.
- Planets are round hitboxes, so keep planet art filling a circle (rings can stick out a bit).
- Keep the background dark and low-detail so the probe and its trail stay easy to see.
