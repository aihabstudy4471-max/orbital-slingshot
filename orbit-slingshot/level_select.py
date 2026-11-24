"""Level select screen. Every level is playable - click one to start it.

Levels are split automatically:
  - normal levels  = any level in levels.py WITHOUT a 'boss' key
  - boss levels    = any level WITH a 'boss' key (shown in their own row)

Best stars are remembered while the game is open (not saved to a file yet).
"""
import math
import pygame

COLUMNS = 5
BUTTON_W, BUTTON_H = 110, 74
GAP = 18

WHITE = (255, 255, 255)
GREY = (110, 115, 140)
DARK = (22, 22, 44)
CYAN = (90, 230, 255)
YELLOW = (255, 220, 70)
RED = (255, 90, 90)


def draw_star(surf, x, y, radius, color, width=0):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = radius if i % 2 == 0 else radius * 0.45
        pts.append((x + math.cos(a) * r, y + math.sin(a) * r))
    pygame.draw.polygon(surf, color, pts, width)


# ------------------------------------------------------------------ the screen
class LevelSelect():
    def __init__(self, levels, fonts, screen_size):
        self.levels = levels
        self.big_font, self.mid_font, self.small_font = fonts
        self.width, self.height = screen_size
        self.progress = {}          # {level name: best stars} - a level in here has been beaten
        self.normal = [i for i, l in enumerate(levels) if 'boss' not in l]
        self.bosses = [i for i, l in enumerate(levels) if 'boss' in l]
        self.buttons = self.layout()

    # ---------------------------------------------------------- progress
    def name(self, index):
        return self.levels[index]['name']

    def completed(self, index):
        return self.name(index) in self.progress

    def best_stars(self, index):
        return self.progress.get(self.name(index), 0)

    def record_win(self, index, stars):
        """Call this when a level is won. Keeps the best star count."""
        if not self.completed(index) or stars > self.best_stars(index):
            self.progress[self.name(index)] = stars

    # ---------------------------------------------------------- layout
    def layout(self):
        """Works out where every button goes. Returns [(rect, level index), ...]."""
        buttons = []
        grid_w = COLUMNS * BUTTON_W + (COLUMNS - 1) * GAP
        left = (self.width - grid_w) // 2

        top = 150
        for n, index in enumerate(self.normal):
            row, col = divmod(n, COLUMNS)
            rect = pygame.Rect(left + col * (BUTTON_W + GAP), top + row * (BUTTON_H + GAP), BUTTON_W, BUTTON_H)
            buttons.append((rect, index))

        rows = max(1, math.ceil(len(self.normal) / COLUMNS))
        self.boss_header_y = top + rows * (BUTTON_H + GAP) + 8
        boss_top = self.boss_header_y + 24
        boss_w = len(self.bosses) * BUTTON_W + max(0, len(self.bosses) - 1) * GAP
        boss_left = (self.width - boss_w) // 2
        for n, index in enumerate(self.bosses):
            rect = pygame.Rect(boss_left + n * (BUTTON_W + GAP), boss_top, BUTTON_W, BUTTON_H)
            buttons.append((rect, index))
        return buttons

    # ---------------------------------------------------------- input
    def handle_event(self, event):
        """Returns the level index that was clicked, otherwise None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, index in self.buttons:
                if rect.collidepoint(event.pos):
                    return index
        return None

    # ---------------------------------------------------------- drawing
    def draw(self, surf, background):
        surf.blit(background, (0, 0))
        title = self.big_font.render('SELECT LEVEL', True, CYAN)
        surf.blit(title, title.get_rect(center=(self.width // 2, 60)))

        header = self.small_font.render('LEVELS', True, GREY)
        surf.blit(header, header.get_rect(center=(self.width // 2, 125)))
        if self.bosses:
            header = self.small_font.render('BOSSES', True, RED)
            surf.blit(header, header.get_rect(center=(self.width // 2, self.boss_header_y)))

        mouse = pygame.mouse.get_pos()
        for rect, index in self.buttons:
            self.draw_button(surf, rect, index, rect.collidepoint(mouse))

        total = sum(len(l.get('stars', [])) for l in self.levels)
        got = sum(self.best_stars(i) for i in range(len(self.levels)))
        info = self.small_font.render('Stars: %d / %d      Esc: back' % (got, total), True, GREY)
        surf.blit(info, info.get_rect(center=(self.width // 2, self.height - 24)))

    def draw_button(self, surf, rect, index, hover):
        is_boss = index in self.bosses
        accent = RED if is_boss else CYAN
        pygame.draw.rect(surf, (35, 35, 70) if hover else DARK, rect, border_radius=10)
        pygame.draw.rect(surf, accent if hover or self.completed(index) else GREY, rect, 2, border_radius=10)

        label = 'BOSS %d' % (self.bosses.index(index) + 1) if is_boss else str(self.normal.index(index) + 1)
        text = (self.small_font if is_boss else self.mid_font).render(label, True, WHITE)
        text_y = rect.centery if is_boss else rect.y + 26     # bosses have no stars, so centre the text
        surf.blit(text, text.get_rect(center=(rect.centerx, text_y)))

        # stars row (normal levels with stars only)
        total = len(self.levels[index].get('stars', []))
        best = self.best_stars(index)
        for s in range(total):
            x = rect.centerx + (s - (total - 1) / 2) * 22
            if s < best:
                draw_star(surf, x, rect.bottom - 18, 8, YELLOW)
            else:
                draw_star(surf, x, rect.bottom - 18, 8, GREY, 1)

        if hover:       # level name under the grid
            name = self.small_font.render(self.levels[index]['name'], True, accent)
            surf.blit(name, name.get_rect(center=(self.width // 2, self.height - 54)))
