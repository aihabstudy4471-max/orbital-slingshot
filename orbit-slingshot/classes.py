"""Game objects + physics for Orbit Slingshot.

Nothing in here opens a window, so levels can be tested/solved without
running the game (see tools/solve_levels.py).
"""
import math
import random
import pygame

# ------------------------------------------------------------------ physics tuning
FPS = 60
SUBSTEPS = 4                    # physics steps per frame (smaller steps = more accurate orbits)
PHYS_DT = 1.0 / (FPS * SUBSTEPS)
G = 1000.0                      # gravity constant - planet 'mass' values are tuned around this
SOFTENING = 14.0                # stops gravity blowing up on very close passes
MAX_LAUNCH_SPEED = 520.0        # pixels per second at full pull
MAX_DRAG = 160.0                # pixels of mouse drag for full power
MAX_FLIGHT_TIME = 25.0          # seconds before a shot counts as lost
OUT_OF_BOUNDS = 300             # how far off-screen the probe can go before it's lost

PROBE_RADIUS = 6
STAR_RADIUS = 13


def gravity_at(x, y, planets):
    """Total acceleration on a point from every planet (Newton: a = G*m / d^2)."""
    ax = ay = 0.0
    for p in planets:
        dx = p.x - x
        dy = p.y - y
        d2 = dx * dx + dy * dy + SOFTENING * SOFTENING
        inv = G * p.mass / (d2 * math.sqrt(d2))     # G*m/d^2, times (dx/d) gives the x part
        ax += dx * inv
        ay += dy * inv
    return ax, ay


def launch_velocity(origin, mouse):
    """Slingshot: pull back from the launcher, probe flies the opposite way."""
    dx = origin[0] - mouse[0]
    dy = origin[1] - mouse[1]
    dist = math.hypot(dx, dy)
    if dist < 1:
        return 0.0, 0.0, 0.0
    power = min(dist, MAX_DRAG) / MAX_DRAG
    speed = power * MAX_LAUNCH_SPEED
    return dx / dist * speed, dy / dist * speed, power


# ------------------------------------------------------------------ level objects
class Planet():
    def __init__(self, x, y, radius, mass, color=(90, 140, 255), kind='planet', sprite=None, orbit=None):
        self.x, self.y = x, y
        self.radius = radius
        self.mass = mass
        self.color = color
        self.kind = kind            # 'planet' or 'blackhole' (draws differently)
        self.sprite = sprite        # optional image name in assets/planets/
        self.image = None           # filled in by the game if the sprite file exists
        # optional moving planet: (centre_x, centre_y, orbit_radius, seconds_per_lap)
        self.orbit = orbit
        self.angle = 0.0
        if orbit:
            self.angle = math.atan2(y - orbit[1], x - orbit[0])
        self.start_angle = self.angle

    def reset(self):
        self.angle = self.start_angle
        self.update_orbit(0)

    def update_orbit(self, dt):
        if not self.orbit:
            return
        cx, cy, r, period = self.orbit
        self.angle += dt * 2 * math.pi / period
        self.x = cx + math.cos(self.angle) * r
        self.y = cy + math.sin(self.angle) * r

    def hits(self, x, y, r):
        return math.hypot(self.x - x, self.y - y) < self.radius + r


class Target():
    def __init__(self, x, y, radius=30):
        self.x, self.y, self.radius = x, y, radius

    def hits(self, x, y, r):
        return math.hypot(self.x - x, self.y - y) < self.radius + r


class Star():
    """Optional collectible - grab them on the way for a better rating."""
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.collected = False


class Probe():
    def __init__(self, x, y, vx, vy):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.time = 0.0
        self.trail = [(x, y)]
        self.state = 'flying'       # 'flying', 'won', 'crashed', 'lost'
        self.hit_planet = None
        self.boss_part = None
        self.stars_this_shot = 0

    def update(self, planets, target, stars, bounds, frame_dt=1.0 / FPS, move_planets=True, boss=None):
        """Advance one frame. Same code is used by the game AND the level solver.
        On boss levels target is None and boss is a Boss."""
        if self.state != 'flying':
            return self.state
        w, h = bounds
        pulls = planets + [boss] if boss else planets      # the boss has gravity too
        for _ in range(SUBSTEPS):
            if move_planets:
                for p in planets:
                    p.update_orbit(PHYS_DT)
            ax, ay = gravity_at(self.x, self.y, pulls)
            # semi-implicit Euler: update velocity first, then position (keeps orbits stable)
            self.vx += ax * PHYS_DT
            self.vy += ay * PHYS_DT
            self.x += self.vx * PHYS_DT
            self.y += self.vy * PHYS_DT
            self.time += PHYS_DT

            for s in stars:
                if not s.collected and math.hypot(s.x - self.x, s.y - self.y) < STAR_RADIUS + PROBE_RADIUS:
                    s.collected = True
                    self.stars_this_shot += 1
            for p in planets:
                if p.hits(self.x, self.y, PROBE_RADIUS):
                    self.state = 'crashed'
                    self.hit_planet = p
                    return self.state
            if boss:
                part = boss.hit_part(self.x, self.y, PROBE_RADIUS)
                if part:
                    self.state = 'hit_boss'
                    self.boss_part = part           # 'eye', 'claw' (glowing) or 'body'
                    return self.state
            if target and target.hits(self.x, self.y, PROBE_RADIUS):
                self.state = 'won'
                return self.state
            if (self.x < -OUT_OF_BOUNDS or self.x > w + OUT_OF_BOUNDS or
                    self.y < -OUT_OF_BOUNDS or self.y > h + OUT_OF_BOUNDS or
                    self.time > MAX_FLIGHT_TIME):
                self.state = 'lost'
                return self.state

        self.trail.append((self.x, self.y))
        if len(self.trail) > 240:
            self.trail.pop(0)
        return self.state


def predict_path(origin, vx, vy, planets, frames):
    """Dots for the aiming preview. Planets are treated as frozen (cheap + still helpful)."""
    x, y = origin
    points = []
    for f in range(frames):
        for _ in range(SUBSTEPS):
            ax, ay = gravity_at(x, y, planets)
            vx += ax * PHYS_DT
            vy += ay * PHYS_DT
            x += vx * PHYS_DT
            y += vy * PHYS_DT
            if any(p.hits(x, y, PROBE_RADIUS) for p in planets):
                return points
        if f % 3 == 0:
            points.append((x, y))
    return points


def build_level(data):
    """Turn a level dict from levels.py into objects."""
    planets = [Planet(*p['pos'], p['radius'], p['mass'],
                      color=p.get('color', (90, 140, 255)),
                      kind=p.get('kind', 'planet'),
                      sprite=p.get('sprite'),
                      orbit=p.get('orbit'))
               for p in data['planets']]
    target = Target(*data['target']) if 'target' in data else None     # boss levels have no target
    stars = [Star(*s) for s in data.get('stars', [])]
    return planets, target, stars


# ------------------------------------------------------------------ boss
class Boss():
    """The alien boss. Settings come from the 'boss' section of a level in levels.py.

    Hitboxes are circles, positioned relative to the boss's centre (x, y):
      eye   - the weak spot, sticks out at the front (left) of the body
      body  - behind the eye. Hitting it destroys the probe
      claws - one above, one below. Hitting one only does damage while it GLOWS
    """
    BODY_OFFSET = (40, 0)
    BODY_RADIUS = 110
    EYE_OFFSET = (-40, -10)
    EYE_RADIUS = 55
    CLAW_OFFSETS = [(-150, -115), (-150, 115)]      # top claw, bottom claw
    CLAW_RADIUS = 30

    def __init__(self, data):
        self.home_x, self.home_y = data['pos']
        self.max_hp = data.get('hp', 6)
        self.hover_range = data.get('hover_range', 120)
        self.hover_time = data.get('hover_time', 4.0)
        self.claw_every = data.get('claw_every', 7.0)
        self.claw_window = data.get('claw_window', 3.0)
        self.claw_damage = data.get('claw_damage', 3)
        self.eye_damage = data.get('eye_damage', 1)
        self.mass = data.get('mass', 4000)            # gravity strength, 0 = no pull
        self.color = tuple(data.get('color', (60, 165, 100)))       # skin colour (placeholder art)
        self.eye_color = tuple(data.get('eye_color', (180, 20, 35)))  # iris colour (placeholder art)
        self.reset()

    def reset(self):
        self.hp = self.max_hp
        self.time = 0.0
        self.x, self.y = self.home_x, self.home_y
        self.claw_timer = self.claw_every   # seconds until a claw starts glowing
        self.glowing = None                 # None, 0 (top claw) or 1 (bottom claw)
        self.glow_left = 0.0                # seconds left to hit the glowing claw
        self.hurt_flash = 0.0               # eye flashes after being hit
        self.attack_flash = 0.0             # claw swipe effect after an attack

    def update(self, dt):
        """Call once per frame. Returns 'glow' when a claw lights up, 'attack' when the
        player was too slow, otherwise None."""
        self.time += dt
        self.y = self.home_y + math.sin(self.time * 2 * math.pi / self.hover_time) * self.hover_range
        self.hurt_flash = max(0.0, self.hurt_flash - dt)
        self.attack_flash = max(0.0, self.attack_flash - dt)

        if self.glowing is None:
            self.claw_timer -= dt
            if self.claw_timer <= 0:
                self.glowing = random.choice([0, 1])
                self.glow_left = self.claw_window
                return 'glow'
        else:
            self.glow_left -= dt
            if self.glow_left <= 0:
                self.attack_flash = 0.6
                self.stop_glow()
                return 'attack'
        return None

    def stop_glow(self):
        self.glowing = None
        self.claw_timer = self.claw_every

    def part_pos(self, offset):
        return self.x + offset[0], self.y + offset[1]

    def eye_pos(self):
        return self.part_pos(self.EYE_OFFSET)

    def claw_pos(self, i):
        return self.part_pos(self.CLAW_OFFSETS[i])

    def body_pos(self):
        return self.part_pos(self.BODY_OFFSET)

    def hit_part(self, x, y, r):
        """Which part (if any) a circle at (x, y) with radius r touches."""
        def touching(pos, radius):
            return math.hypot(pos[0] - x, pos[1] - y) < radius + r
        if self.glowing is not None and touching(self.claw_pos(self.glowing), self.CLAW_RADIUS + 6):
            return 'claw'           # +6 = a little generous, it's a timed bonus
        if touching(self.eye_pos(), self.EYE_RADIUS):
            return 'eye'
        if any(touching(self.claw_pos(i), self.CLAW_RADIUS) for i in range(2)):
            return 'body'           # non-glowing claws are just solid
        if touching(self.body_pos(), self.BODY_RADIUS):
            return 'body'
        return None

    def hits(self, x, y, r):
        """Lets the aiming preview treat the boss like a planet (stops the dots at it)."""
        return self.hit_part(x, y, r) is not None

    def take_hit(self, part):
        """Damage the boss. Returns the damage done."""
        damage = self.claw_damage if part == 'claw' else self.eye_damage
        self.hp = max(0, self.hp - damage)
        self.hurt_flash = 0.4
        if part == 'claw':
            self.stop_glow()
        return damage


# ------------------------------------------------------------------ effects (no art needed)
def make_glow(color, radius):
    surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -2):
        alpha = int(70 * (1 - r / radius) ** 2)
        pygame.draw.circle(surf, (*color, alpha), (radius, radius), r)
    return surf


class FX():
    """Particles + screen shake + floating text."""
    def __init__(self, font):
        self.font = font
        self.particles = []
        self.texts = []
        self.shake_power = 0.0

    def burst(self, x, y, color, count=25, speed=5):
        for _ in range(count):
            a = random.uniform(0, math.tau)
            s = random.uniform(1, speed)
            life = random.randint(20, 45)
            self.particles.append([x, y, math.cos(a) * s, math.sin(a) * s, life, life, color,
                                   random.randint(2, 4)])

    def text(self, x, y, txt, color=(255, 255, 255)):
        self.texts.append([x, y, txt, color, 60])

    def shake(self, power):
        self.shake_power = max(self.shake_power, power)

    def offset(self):
        if self.shake_power < 0.5:
            return 0, 0
        p = int(self.shake_power)
        return random.randint(-p, p), random.randint(-p, p)

    def update(self):
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]
            p[2] *= 0.96
            p[3] *= 0.96
            p[4] -= 1
        self.particles = [p for p in self.particles if p[4] > 0]
        for t in self.texts:
            t[1] -= 0.8
            t[4] -= 1
        self.texts = [t for t in self.texts if t[4] > 0]
        self.shake_power *= 0.88

    def draw(self, surface):
        for x, y, _, _, life, max_life, color, size in self.particles:
            fade = life / max_life
            c = tuple(int(v * fade) for v in color)
            pygame.draw.circle(surface, c, (int(x), int(y)), max(1, int(size * fade + 0.5)))
        for x, y, txt, color, life in self.texts:
            img = self.font.render(txt, True, color)
            img.set_alpha(min(255, life * 8))
            surface.blit(img, img.get_rect(center=(x, y)))
