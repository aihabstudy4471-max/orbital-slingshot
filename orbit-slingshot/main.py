"""Orbit Slingshot - launch the probe, use planet gravity to reach the target.

Controls
  Mouse drag   pull back from the probe and release to launch
  R            reset the current shot
  Enter/Space  next level (after winning)
  Esc          back to title / quit
  F1           (debug) show the full predicted path
  F2           (debug) skip to next level
"""
import math
import os
import random
import pygame

pygame.init()

from classes import (Probe, build_level, launch_velocity, predict_path, make_glow, FX,
                     FPS, MAX_DRAG, PROBE_RADIUS, STAR_RADIUS)
from levels import LEVELS

from level_select import LevelSelect
# ------------------------------------------------------------------ window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Orbit Slingshot')
canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))   # draw here, then blit with screen shake
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
GREY = (150, 155, 175)
YELLOW = (255, 220, 70)
CYAN = (90, 230, 255)
RED = (255, 80, 80)
BG = (8, 8, 20)

PREVIEW_FRAMES = 40             # how far ahead the aiming dots go (frames). Bigger = easier
CRASH_DELAY = 70                # frames to wait after a crash before you can shoot again


# ------------------------------------------------------------------ assets (all optional)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def asset(*parts):
    """Find a file in assets/ with or without its extension. Returns None if missing."""
    path = os.path.join(BASE_DIR, 'assets', *parts)
    for ext in ('', '.png', '.jpg', '.wav', '.ogg', '.mp3', '.ttf', '.otf'):
        if os.path.isfile(path + ext):
            return path + ext
    return None


def load_image(*parts, size=None):
    path = asset(*parts)
    if not path:
        return None
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(img, size) if size else img


class NullSound():
    def play(self, *args, **kwargs):
        pass


def load_sound(*parts, volume=0.6):
    path = asset(*parts)
    if not path:
        return NullSound()
    try:
        s = pygame.mixer.Sound(path)
        s.set_volume(volume)
        return s
    except pygame.error:
        return NullSound()


def load_font(name, size):
    path = asset('fonts', name)
    return pygame.font.Font(path, size) if path else pygame.font.SysFont('arial', size, bold=True)


big_font = load_font('main', 64)
mid_font = load_font('main', 32)
small_font = load_font('main', 20)

# art from the designer goes in assets/ - anything missing falls back to drawn shapes
probe_img = load_image('probe', size=(PROBE_RADIUS * 4, PROBE_RADIUS * 4))
target_img = load_image('target', size=(80, 80))
star_img = load_image('star', size=(STAR_RADIUS * 2, STAR_RADIUS * 2))
background_img = load_image('background', size=(SCREEN_WIDTH, SCREEN_HEIGHT))

sounds = {
    'launch': load_sound('sfx', 'launch'),
    'crash': load_sound('sfx', 'crash'),
    'win': load_sound('sfx', 'win'),
    'star': load_sound('sfx', 'star'),
}
music = asset('music')
if music:
    try:
        pygame.mixer.music.load(music)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass


# ------------------------------------------------------------------ background
def make_starfield(seed):
    rnd = random.Random(seed)
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surf.fill(BG)
    for _ in range(220):
        b = rnd.randint(60, 220)
        surf.set_at((rnd.randrange(SCREEN_WIDTH), rnd.randrange(SCREEN_HEIGHT)), (b, b, min(255, b + 30)))
    for _ in range(25):
        b = rnd.randint(150, 255)
        pygame.draw.circle(surf, (b, b, b), (rnd.randrange(SCREEN_WIDTH), rnd.randrange(SCREEN_HEIGHT)), 1)
    return surf


def draw_star_shape(surf, x, y, radius, color, spin=0.0, width=0):
    pts = []
    for i in range(10):
        a = spin - math.pi / 2 + i * math.pi / 5
        r = radius if i % 2 == 0 else radius * 0.45
        pts.append((x + math.cos(a) * r, y + math.sin(a) * r))
    pygame.draw.polygon(surf, color, pts, width)


# ------------------------------------------------------------------ game state
class Game():
    def __init__(self):
        self.state = 'title'        # 'title', 'aim', 'flying', 'crashed', 'won', 'finished'
        self.level_index = 0
        self.best_stars = [0] * len(LEVELS)
        self.fx = FX(mid_font)
        self.show_full_path = False
        self.glow_cache = {}
        self.load_level(0)
        self.state = 'title'
        self.select = LevelSelect(LEVELS, (big_font, mid_font, small_font), (SCREEN_WIDTH, SCREEN_HEIGHT))

    # ---------------------------------------------------------- level flow
    def load_level(self, index):
        self.level_index = index
        self.data = LEVELS[index]
        self.planets, self.target, self.stars = build_level(self.data)
        for p in self.planets:
            if p.sprite:
                p.image = load_image('planets', p.sprite, size=(p.radius * 2, p.radius * 2))
        self.start = self.data['start']
        self.background = background_img or make_starfield(index)
        self.shots = 0
        self.fx = FX(mid_font)      # clear leftover particles from the last level
        self.reset_shot()

    def reset_shot(self):
        for p in self.planets:
            p.reset()
        for s in self.stars:
            s.collected = False
        self.probe = None
        self.dragging = False
        self.timer = 0
        self.state = 'aim'

    def next_level(self):
        if self.level_index + 1 < len(LEVELS):
            self.load_level(self.level_index + 1)
        else:
            self.state = 'finished'

    # ---------------------------------------------------------- input
    def handle_event(self, event):
        if self.state == 'select':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = 'select'
                return True
            chosen = self.select.handle_event(event)
            if chosen is not None:
                self.load_level(chosen)
            return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == 'title':
                    return False
                self.state = 'title'
            elif event.key == pygame.K_F1:
                self.show_full_path = not self.show_full_path
            elif event.key == pygame.K_F2 and self.state != 'title':
                self.next_level()
            elif event.key == pygame.K_r and self.state in ('flying', 'crashed', 'aim'):
                self.reset_shot()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.on_confirm()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == 'aim':
                self.dragging = True
            elif self.state in ('title', 'won', 'finished'):
                self.on_confirm()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.state == 'aim' and self.dragging:
                self.dragging = False
                self.launch(pygame.mouse.get_pos())
        return True

    def on_confirm(self):
        if self.state == 'title':
            self.state = 'select'
        elif self.state == 'won':
            self.next_level()
        elif self.state == 'finished':
            self.state = 'select'

    def launch(self, mouse):
        vx, vy, power = launch_velocity(self.start, mouse)
        if power < 0.08:            # tiny drag = probably a misclick, ignore it
            return
        self.probe = Probe(*self.start, vx, vy)
        self.shots += 1
        self.state = 'flying'
        sounds['launch'].play()
        self.fx.burst(*self.start, CYAN, count=12, speed=3)

    # ---------------------------------------------------------- update
    def update(self):
        self.fx.update()
        # moving planets are frozen while aiming and only move once launched,
        # so the same shot always does the same thing (and matches the level solver)
        if self.state == 'flying':
            before = self.probe.stars_this_shot
            result = self.probe.update(self.planets, self.target, self.stars, (SCREEN_WIDTH, SCREEN_HEIGHT))
            if self.probe.stars_this_shot > before:
                sounds['star'].play()
                self.fx.text(self.probe.x, self.probe.y - 20, '+1', YELLOW)
                self.fx.burst(self.probe.x, self.probe.y, YELLOW, count=10, speed=3)
            if result == 'crashed':
                sounds['crash'].play()
                self.fx.burst(self.probe.x, self.probe.y, (255, 150, 60), count=40, speed=6)
                self.fx.shake(10)
                self.state = 'crashed'
                self.timer = CRASH_DELAY
            elif result == 'lost':
                self.fx.text(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 'Lost in space...', GREY)
                self.state = 'crashed'
                self.timer = CRASH_DELAY // 2
            elif result == 'won':
                sounds['win'].play()
                self.fx.burst(self.target.x, self.target.y, CYAN, count=60, speed=7)
                self.fx.shake(6)
                got = self.probe.stars_this_shot
                self.best_stars[self.level_index] = max(self.best_stars[self.level_index], got)
                self.state = 'won'
                self.select.record_win(self.level_index, got)

        elif self.state == 'crashed':
            self.timer -= 1
            if self.timer <= 0:
                self.reset_shot()

    # ---------------------------------------------------------- drawing
    def glow(self, color, radius):
        key = (color, radius)
        if key not in self.glow_cache:
            self.glow_cache[key] = make_glow(color, radius)
        return self.glow_cache[key]


    def draw_gravity_rings(self, surf, p):
        """Rings that flow in towards the planet. Stronger gravity = rings closer together."""
        t = pygame.time.get_ticks() / 1000          

        
        spacing = 30000 / p.mass     
        speed = 50                
        max_dist = 50            
        brightness = 0.5          
        thickness = 1        
        # ------------------------------------------------------------------

        spacing = max(8, spacing)   
        ring_count = math.ceil(max_dist / spacing)
        period = ring_count * spacing   

      
        base = (150, 60, 200) if p.kind == 'blackhole' else p.color

        for i in range(ring_count):
            dist = period - (t * speed + i * spacing) % period
            if dist > max_dist:
                continue            

            fade = 1 - dist / max_dist      
            color = tuple(int(c * fade * brightness) for c in base)
            pygame.draw.circle(surf, color, (int(p.x), int(p.y)), int(p.radius + dist), thickness)
   
    def draw_planet(self, surf, p):
        x, y = int(p.x), int(p.y)
        if p.orbit:
            pygame.draw.circle(surf, (40, 40, 70), (int(p.orbit[0]), int(p.orbit[1])), int(p.orbit[2]), 1)
        self.draw_gravity_rings(surf, p)
        if p.image:
            surf.blit(p.image, p.image.get_rect(center=(x, y)))
            return
        if p.kind == 'blackhole':
            t = pygame.time.get_ticks() / 1000
            for i in range(5):      # swirling accretion rings
                r = p.radius + 8 + i * 9 + int(3 * math.sin(t * 3 + i))
                pygame.draw.circle(surf, (150 - i * 25, 60, 200 - i * 30), (x, y), r, 2)
            pygame.draw.circle(surf, (0, 0, 0), (x, y), p.radius)
            return
        g = self.glow(p.color, int(p.radius * 1.6))
        surf.blit(g, g.get_rect(center=(x, y)))
        # simple shading: dark base, lit circle nudged up-left, small highlight
        dark = tuple(int(c * 0.55) for c in p.color)
        light = tuple(min(255, int(c * 1.25) + 20) for c in p.color)
        pygame.draw.circle(surf, dark, (x, y), p.radius)
        off = int(p.radius * 0.15)
        pygame.draw.circle(surf, p.color, (x - off, y - off), p.radius - off)
        pygame.draw.circle(surf, light, (x - p.radius // 3, y - p.radius // 3), max(2, p.radius // 5))
        label = small_font.render(str(p.mass // 100), True, WHITE)
        surf.blit(label, label.get_rect(center=(x, y)))

    def draw_target(self, surf):
        t = pygame.time.get_ticks() / 1000
        x, y, r = int(self.target.x), int(self.target.y), self.target.radius
        if target_img:
            surf.blit(target_img, target_img.get_rect(center=(x, y)))
            return
        g = self.glow(CYAN, r * 2)
        surf.blit(g, g.get_rect(center=(x, y)))
        pulse = int(4 * math.sin(t * 4))
        pygame.draw.circle(surf, CYAN, (x, y), r + pulse, 3)
        pygame.draw.circle(surf, CYAN, (x, y), max(4, r // 2 - pulse), 2)

    def draw_star(self, surf, s):
        if s.collected:
            return
        if star_img:
            surf.blit(star_img, star_img.get_rect(center=(int(s.x), int(s.y))))
            return
        draw_star_shape(surf, s.x, s.y, STAR_RADIUS, YELLOW, pygame.time.get_ticks() / 1000)

    def draw_probe(self, surf, x, y, vx=1.0, vy=0.0):
        if probe_img:
            angle = -math.degrees(math.atan2(vy, vx))
            img = pygame.transform.rotate(probe_img, angle)
            surf.blit(img, img.get_rect(center=(int(x), int(y))))
        else:
            pygame.draw.circle(surf, WHITE, (int(x), int(y)), PROBE_RADIUS)
            pygame.draw.circle(surf, CYAN, (int(x), int(y)), PROBE_RADIUS, 2)

    def draw_trail(self, surf, trail):
        n = len(trail)
        for i in range(1, n):
            fade = i / n
            c = (int(90 * fade), int(230 * fade), int(255 * fade))
            pygame.draw.line(surf, c, trail[i - 1], trail[i], 2)

    def draw_aim(self, surf):
        mouse = pygame.mouse.get_pos()
        vx, vy, power = launch_velocity(self.start, mouse)
        # rubber band
        dx, dy = mouse[0] - self.start[0], mouse[1] - self.start[1]
        d = math.hypot(dx, dy)
        if d > MAX_DRAG:
            dx, dy = dx / d * MAX_DRAG, dy / d * MAX_DRAG
        band_end = (self.start[0] + dx, self.start[1] + dy)
        pygame.draw.line(surf, (120, 120, 150), self.start, band_end, 2)
        # trajectory preview
        frames = 600 if self.show_full_path else PREVIEW_FRAMES
        for i, pt in enumerate(predict_path(self.start, vx, vy, self.planets, frames)):
            fade = 1 - i / (frames / 3 + 1) if not self.show_full_path else 0.7
            c = int(255 * max(0.15, fade))
            pygame.draw.circle(surf, (c, c, c), (int(pt[0]), int(pt[1])), 2)
        # power meter
        txt = small_font.render('%d%%' % int(power * 100), True, YELLOW if power >= 1 else WHITE)
        surf.blit(txt, (band_end[0] + 12, band_end[1] - 10))

    def draw_hud(self, surf):
        name = small_font.render('Level %d: %s' % (self.level_index + 1, self.data['name']), True, WHITE)
        surf.blit(name, (16, 12))
        shots = small_font.render('Shots: %d' % self.shots, True, GREY)
        surf.blit(shots, (16, 38))
        got = sum(s.collected for s in self.stars)
        stars = small_font.render('Stars: %d/%d' % (got, len(self.stars)), True, YELLOW)
        surf.blit(stars, stars.get_rect(topright=(SCREEN_WIDTH - 16, 12)))
        hint = self.data.get('hint')
        if hint and self.state == 'aim' and self.shots < 3:
            h = small_font.render(hint, True, GREY)
            surf.blit(h, h.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 16)))
        if self.show_full_path:
            dbg = small_font.render('DEBUG: full path (F1)', True, RED)
            surf.blit(dbg, dbg.get_rect(topright=(SCREEN_WIDTH - 16, 38)))

    def draw_centered(self, surf, lines):
        """lines = [(text, font, colour), ...] drawn as a block in the middle of the screen."""
        shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 140))
        surf.blit(shade, (0, 0))
        y = SCREEN_HEIGHT // 2 - len(lines) * 30
        for text, font, color in lines:
            img = font.render(text, True, color)
            surf.blit(img, img.get_rect(center=(SCREEN_WIDTH // 2, y)))
            y += font.get_height() + 14

    def draw(self, surf):
        surf.blit(self.background, (0, 0))
        for p in self.planets:
            self.draw_planet(surf, p)
        self.draw_target(surf)
        for s in self.stars:
            self.draw_star(surf, s)
        if self.state == 'select':
            self.select.draw(surf, self.background)
            return

        # launcher pad
        pygame.draw.circle(surf, (60, 60, 90), self.start, 16, 2)

        if self.probe:
            self.draw_trail(surf, self.probe.trail)
            if self.probe.state == 'flying' or self.probe.state == 'won':
                self.draw_probe(surf, self.probe.x, self.probe.y, self.probe.vx, self.probe.vy)
        if self.state == 'aim':
            if self.dragging:
                self.draw_aim(surf)
            self.draw_probe(surf, *self.start)

        self.fx.draw(surf)
        if self.state != 'title':
            self.draw_hud(surf)

        if self.state == 'title':
            self.draw_centered(surf, [
                ('ORBIT SLINGSHOT', big_font, CYAN),
                ('Use gravity to guide your probe to the target', small_font, WHITE),
                ('Click to start', mid_font, YELLOW),
                ('Esc to quit', small_font, GREY),
            ])
        elif self.state == 'won':
            got = self.probe.stars_this_shot
            self.draw_centered(surf, [
                ('TARGET REACHED', big_font, CYAN),
                ('', mid_font, YELLOW),     # star icons drawn below
                ('Shots: %d' % self.shots, small_font, WHITE),
                ('Click or Enter for next level', small_font, GREY),
            ])
            total = len(self.stars)
            for i in range(total):
                x = SCREEN_WIDTH // 2 + (i - (total - 1) / 2) * 60
                y = SCREEN_HEIGHT // 2 - 120 + big_font.get_height() + 14   # centre of the 2nd line
                draw_star_shape(surf, x, y, 24, YELLOW if i < got else GREY, width=0 if i < got else 2)
        elif self.state == 'finished':
            total = sum(self.best_stars)
            self.draw_centered(surf, [
                ('MISSION COMPLETE', big_font, CYAN),
                ('Total stars: %d / %d' % (total, sum(len(l.get('stars', [])) for l in LEVELS)), mid_font, YELLOW),
                ('Click to return to title', small_font, GREY),
            ])


# ------------------------------------------------------------------ main loop
def main():
    game = Game()
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif not game.handle_event(event):
                running = False
        game.update()
        game.draw(canvas)
        screen.fill(BG)
        screen.blit(canvas, game.fx.offset())
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
