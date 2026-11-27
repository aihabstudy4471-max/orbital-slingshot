# Assets guide (for the designer)

Drop files in here with these names and the game picks them up automatically.
Anything missing just gets drawn as a simple shape, so add things whenever they're ready.
PNG with transparency is best for sprites. **Use .ogg for sounds and music** (the web version
needs it; .wav and .mp3 can fail in some browsers). The file extension doesn't matter as long as the
name matches (`probe.png` and `probe.jpg` both work).

| File | What it is | Size it gets drawn at |
|---|---|---|
| `probe.png` | The probe. **Draw it pointing right** – the game rotates it to face where it's flying | 24 x 24 |
| `target.png` | The goal / landing zone | 80 x 80 |
| `star.png` | Collectible star | 26 x 26 |
| `background.png` | Full-screen background (replaces the generated starfield) | 1000 x 700 |
| `planets/<name>.png` | Planet images. A level chooses one with `'sprite': '<name>'` in levels.py | planet diameter (40–130px) |
| `boss/boss_body.png` | Alien body + tentacles, NO eye or claws. Eye sits at the front-left | ~280 x 280 |
| `boss/boss_eye.png` / `boss/boss_eye_hurt.png` | The big eye (weak spot) + flash version when hit | 110 x 110 |
| `boss/boss_claw.png` / `boss/boss_claw_glow.png` | ONE claw pointing left (top claw) + glowing version. Code flips it for the bottom claw | 90 x 90 |
| `fonts/main.ttf` | Font for all text | – |
| `music.ogg` | Looping background music | – |
| `sfx/launch.ogg` | Probe launched | – |
| `sfx/crash.ogg` | Probe hits a planet | – |
| `sfx/win.ogg` | Target reached | – |
| `sfx/star.ogg` | Star collected | – |
| `sfx/boss_hit.ogg` | Boss eye / claw hit | – |
| `sfx/boss_attack.ogg` | Boss attacks (claw timer ran out) | – |
| `sfx/claw_glow.ogg` | A claw starts glowing | – |

Placeholder sounds
- `sfx/*.ogg` and `music.ogg` are currently computer-generated placeholders made by
  `python tools/make_placeholder_sounds.py`. Just overwrite them with real sounds (same names).
  Re-running the script won't touch files that already exist (unless you add `--force`).

Tips
- Draw at 2–4x the listed size; the game scales it down smoothly.
- Planets are round hitboxes, so keep planet art filling a circle (rings can stick out a bit).
- Keep the background dark and low-detail so the probe and its trail stay easy to see.
