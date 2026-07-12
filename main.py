import random

import pygame

import audio
import visuals
from algorithms import ALGORITHMS, DESCRIPTIONS, NEEDS_SORTED, NEEDS_TARGET

WIDTH, HEIGHT = 900, 500
ARRAY_SIZE = 50
MIN_VAL, MAX_VAL = 20, 460
MIN_SPEED, MAX_SPEED = 2, 300

ALGO_NAMES = list(ALGORITHMS.keys())


class App:
    def __init__(self):
        pygame.init()
        pygame.mixer.set_num_channels(16)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Algo-Sonic")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 18)

        self.algo_index = 0
        self.speed = 40  # algorithm steps per second
        self.playing = True
        self.step_accum_ms = 0
        self.show_info = False

        self.new_array()

    @property
    def algo_name(self):
        return ALGO_NAMES[self.algo_index]

    def new_array(self):
        self.arr = random.sample(range(MIN_VAL, MAX_VAL), ARRAY_SIZE)
        self.active_indices = set()
        self.finalized = False
        self.step_accum_ms = 0
        self.playing = True

        if self.algo_name in NEEDS_SORTED:
            self.arr.sort()

        if self.algo_name in NEEDS_TARGET:
            self.target = random.choice(self.arr)
            self.gen = ALGORITHMS[self.algo_name](self.arr, self.target)
        else:
            self.target = None
            self.gen = ALGORITHMS[self.algo_name](self.arr)

        self.lo, self.hi = min(self.arr), max(self.arr)

    def switch_algorithm(self, delta):
        self.algo_index = (self.algo_index + delta) % len(ALGO_NAMES)
        self.new_array()

    def adjust_speed(self, factor):
        self.speed = max(MIN_SPEED, min(MAX_SPEED, round(self.speed * factor)))

    def step(self):
        try:
            event = next(self.gen)
        except StopIteration:
            self.finalized = True
            self.playing = False
            return

        kind = event[0]
        self.active_indices = set()

        if kind == "compare":
            _, i, j = event
            self.active_indices = {i, j}
            audio.play_event("compare", audio.note_index_for_value(self.arr[i], self.lo, self.hi))
            audio.play_event("compare", audio.note_index_for_value(self.arr[j], self.lo, self.hi))
        elif kind == "swap":
            _, i, j = event
            self.active_indices = {i, j}
            audio.play_event("swap", audio.note_index_for_value(self.arr[i], self.lo, self.hi))
            audio.play_event("swap", audio.note_index_for_value(self.arr[j], self.lo, self.hi))
        elif kind == "visit":
            _, i = event
            self.active_indices = {i}
            audio.play_event("visit", audio.note_index_for_value(self.arr[i], self.lo, self.hi))
        elif kind == "set":
            _, i, val = event
            self.active_indices = {i}
            audio.play_event("set", audio.note_index_for_value(val, self.lo, self.hi))

    def handle_key(self, key):
        if key == pygame.K_SPACE:
            self.playing = not self.playing
        elif key == pygame.K_r:
            self.new_array()
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.switch_algorithm(1)
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.switch_algorithm(-1)
        elif key in (pygame.K_UP, pygame.K_w):
            self.adjust_speed(1.3)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.adjust_speed(1 / 1.3)
        elif key == pygame.K_i:
            self.show_info = not self.show_info

    def draw_hud(self):
        status = "playing" if self.playing else ("done" if self.finalized else "paused")
        status_line = f"{self.algo_name}  |  speed: {self.speed}/s  |  {status}"
        if self.target is not None:
            status_line += f"  |  target: {self.target}"
        controls_line = "[space] play/pause  [r] reset  [<-/->] algorithm  [up/down] speed  [i] info"

        for row, line in enumerate((status_line, controls_line)):
            text = self.font.render(line, True, (220, 220, 230))
            self.screen.blit(text, (20, HEIGHT - 52 + row * 22))

    def wrap_to_width(self, text, max_width):
        """Greedy word-wrap measured against the actual font, not a guessed char count."""
        words = text.split()
        lines, current = [], ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if self.font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def draw_info(self):
        info = DESCRIPTIONS[self.algo_name]
        text_width = WIDTH - 40  # 20px margin on each side
        lines = [self.algo_name] + self.wrap_to_width(info["desc"], text_width)
        lines += [f"Time: {info['time']}", f"Space: {info['space']}"]

        panel_h = 20 + len(lines) * 22
        panel = pygame.Surface((WIDTH, panel_h))
        panel.set_alpha(215)
        panel.fill((10, 10, 16))
        self.screen.blit(panel, (0, 0))

        for row, line in enumerate(lines):
            text = self.font.render(line, True, (230, 230, 240))
            self.screen.blit(text, (20, 12 + row * 22))

    def run(self):
        running = True
        while running:
            dt = min(self.clock.tick(60), 100)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.handle_key(event.key)

            if self.playing and not self.finalized:
                self.step_accum_ms += dt
                step_interval = 1000 / self.speed
                while self.step_accum_ms >= step_interval:
                    self.step_accum_ms -= step_interval
                    self.step()
                    if self.finalized:
                        break

            visuals.draw_bars(self.screen, self.arr, self.active_indices, self.finalized)
            self.draw_hud()
            if self.show_info:
                self.draw_info()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    App().run()
