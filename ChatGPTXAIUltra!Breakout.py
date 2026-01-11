 
#!/usr/bin/env python3
# Cat's Ultra!BREAKOUT — PYGOTHIC
# Main Menu skin: Ultra! Tetris 1.x
# (C) SAMSOFT
# (C) ATARI 1972-2026
# (C) SAMSOFT 1999-2026
#
# Dynamic SFX Engine: generated square/triangle/noise (no external files)

import sys, math, random
from array import array
import pygame

# ───────────────── CONFIG ─────────────────
FPS = 60
LW, LH = 256, 240
SCALE = 2
SW, SH = LW * SCALE, LH * SCALE

# ───────────────── CONSTANTS ─────────────────
BORDER_L, BORDER_R, BORDER_T = 8, LW - 8, 32
PADDLE_W, PADDLE_H = 48, 8
PADDLE_Y = LH - 40
BALL_SIZE = 4

BRICK_ROWS, BRICK_COLS = 8, 14
BRICK_W, BRICK_H = 18, 8
BRICK_X = (LW - BRICK_COLS * BRICK_W) // 2
BRICK_Y = 40

POINTS = [7, 7, 5, 5, 3, 3, 1, 1]

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DIM   = (140, 140, 140)
TEXT  = (220, 220, 220)

FP = 256
def to_fp(x): return int(x * FP)
def clamp(v, lo, hi): return lo if v < lo else hi if v > hi else v


# ───────────────── DYNAMIC SFX ENGINE (NO FILES) ─────────────────
class APUSynth:
    """Tiny APU-ish synth: square, triangle, noise + mix + seq. Outputs int16 samples."""
    def __init__(self, rate=44100):
        self.rate = rate
        self.enabled = True
        self.channels = 2  # prefer stereo for device compatibility

        # Mixer may fail (no audio device). We gracefully disable.
        try:
            if pygame.mixer.get_init() is None:
                # Try stereo first, fallback mono.
                try:
                    pygame.mixer.init(frequency=rate, size=-16, channels=2, buffer=512)
                except pygame.error:
                    pygame.mixer.init(frequency=rate, size=-16, channels=1, buffer=512)

            init = pygame.mixer.get_init()
            self.channels = init[2] if init else 2
            pygame.mixer.set_num_channels(16)
        except pygame.error:
            self.enabled = False

    def _fade_edges(self, samples: array, ramp_ms: float = 2.0) -> None:
        n = len(samples)
        if n <= 0:
            return
        ramp = int(self.rate * (ramp_ms / 1000.0))
        ramp = min(ramp, n // 2)
        if ramp <= 0:
            return
        for i in range(ramp):
            g = i / ramp
            samples[i] = int(samples[i] * g)
            samples[n - 1 - i] = int(samples[n - 1 - i] * g)

    def square(self, freq: float, dur: float, vol: float = 0.35, duty: float = 0.50) -> array:
        n = int(self.rate * dur)
        if n <= 0:
            return array("h")
        amp = int(32767 * vol)
        period = self.rate / float(max(freq, 1.0))
        high = int(period * duty)

        out = array("h", [0] * n)
        phase = 0.0
        for i in range(n):
            out[i] = amp if phase < high else -amp
            phase += 1.0
            if phase >= period:
                phase -= period

        self._fade_edges(out)
        return out

    def triangle(self, freq: float, dur: float, vol: float = 0.30) -> array:
        n = int(self.rate * dur)
        if n <= 0:
            return array("h")
        amp = int(32767 * vol)
        period = self.rate / float(max(freq, 1.0))

        out = array("h", [0] * n)
        for i in range(n):
            t = (i % period) / period  # 0..1
            tri = (4 * t - 1) if t < 0.5 else (-4 * t + 3)  # -1..1
            out[i] = int(amp * tri)

        self._fade_edges(out)
        return out

    def noise(self, dur: float, vol: float = 0.22) -> array:
        n = int(self.rate * dur)
        if n <= 0:
            return array("h")
        amp = int(32767 * vol)
        out = array("h", [0] * n)

        lfsr = 1
        for i in range(n):
            bit = (lfsr ^ (lfsr >> 1)) & 1
            lfsr = (lfsr >> 1) | (bit << 14)
            out[i] = amp if (lfsr & 1) else -amp

        self._fade_edges(out)
        return out

    def mix(self, *waves: array) -> array:
        if not waves:
            return array("h")
        n = max(len(w) for w in waves)
        out = array("h", [0] * n)
        for w in waves:
            for i, s in enumerate(w):
                v = out[i] + s
                if v > 32767: v = 32767
                elif v < -32768: v = -32768
                out[i] = v
        self._fade_edges(out)
        return out

    def seq(self, parts) -> array:
        out = array("h")
        for p in parts:
            kind = p[0]
            if kind == "sq":
                _, f, d, v, du = p
                out.extend(self.square(f, d, v, du))
            elif kind == "tri":
                _, f, d, v = p
                out.extend(self.triangle(f, d, v))
            elif kind == "noi":
                _, d, v = p
                out.extend(self.noise(d, v))
        return out

    def _to_device_channels(self, mono: array) -> array:
        ch = max(1, int(self.channels))
        if ch == 1:
            return mono
        out = array("h")
        out_extend = out.extend
        for s in mono:
            out_extend([s] * ch)
        return out

    def sound(self, mono_samples: array):
        if not self.enabled:
            return None
        dev = self._to_device_channels(mono_samples)
        try:
            return pygame.mixer.Sound(buffer=dev)
        except TypeError:
            return pygame.mixer.Sound(buffer=dev.tobytes())


class DynamicSFX:
    """Dynamic chiptune SFX: varies pitch by events (row/speed/position)."""
    def __init__(self):
        self.apu = APUSynth(rate=44100)
        self.enabled = self.apu.enabled
        self.on = self.enabled
        self.cache = {}

        # Static UI sounds
        self.s_select = self._mk(self.apu.seq([("sq", 740.0, 0.020, 0.18, 0.125)]))
        self.s_start  = self._mk(self.apu.seq([
            ("sq", 392.0, 0.040, 0.22, 0.25),
            ("sq", 523.0, 0.040, 0.22, 0.25),
            ("sq", 659.0, 0.060, 0.24, 0.25),
        ]))
        self.s_launch = self._mk(self.apu.seq([
            ("sq", 330.0, 0.020, 0.20, 0.50),
            ("sq", 440.0, 0.030, 0.22, 0.50),
        ]))
        self.s_lose   = self._mk(self.apu.seq([
            ("tri", 440.0, 0.050, 0.30),
            ("tri", 392.0, 0.050, 0.28),
            ("tri", 349.0, 0.050, 0.26),
            ("tri", 330.0, 0.050, 0.24),
            ("tri", 294.0, 0.060, 0.22),
            ("tri", 262.0, 0.070, 0.20),
            ("tri", 220.0, 0.080, 0.18),
        ]))

    def toggle(self):
        if self.enabled:
            self.on = not self.on
            # little click
            if self.on:
                self.select()

    def _mk(self, mono_samples: array):
        return self.apu.sound(mono_samples) if self.enabled else None

    def _q(self, x, step):  # quantize
        return int(round(x / step) * step)

    def _cached_sq(self, freq, dur, vol, duty):
        fq = self._q(freq, 5)
        ms = int(round(dur * 1000))
        vv = int(round(vol * 100))
        dd = int(round(duty * 100))
        key = ("sq", fq, ms, vv, dd, self.apu.channels)
        snd = self.cache.get(key)
        if snd is None:
            snd = self._mk(self.apu.square(float(fq), ms / 1000.0, vol, duty))
            self.cache[key] = snd
        return snd

    def _cached_mix_brick(self, freq):
        fq = self._q(freq, 5)
        key = ("brickmix", fq, self.apu.channels)
        snd = self.cache.get(key)
        if snd is None:
            mono = self.apu.mix(
                self.apu.noise(0.030, 0.18),
                self.apu.square(float(fq), 0.030, 0.14, 0.125),
            )
            snd = self._mk(mono)
            self.cache[key] = snd
        return snd

    def _play(self, snd):
        if self.on and snd:
            snd.play()

    # UI
    def select(self): self._play(self.s_select)
    def start(self):  self._play(self.s_start)
    def launch(self): self._play(self.s_launch)
    def lose(self):   self._play(self.s_lose)

    # Dynamic events
    def wall(self, speed):
        # speed ~ px/frame : 1.5..3.5 => pitch bump
        f = 180.0 + float(speed) * 120.0
        snd = self._cached_sq(f, 0.030, 0.22, 0.50)
        self._play(snd)

    def paddle(self, rel01):
        # rel 0..1 -> darker edges, brighter center
        rel01 = 0.0 if rel01 < 0.0 else 1.0 if rel01 > 1.0 else rel01
        center = 1.0 - abs(rel01 - 0.5) * 2.0  # 0 edges -> 1 center
        f = 520.0 + center * 360.0
        snd = self._cached_sq(f, 0.028, 0.24, 0.25)
        self._play(snd)

    def brick(self, row):
        # top rows higher pitch
        notes = [988.0, 932.0, 880.0, 784.0, 740.0, 659.0, 587.0, 523.0]
        r = max(0, min(7, int(row)))
        snd = self._cached_mix_brick(notes[r])
        self._play(snd)


# ───────────────── GAME ─────────────────
class UltraBreakout:
    def __init__(self, sfx: DynamicSFX):
        self.sfx = sfx
        self.state = "menu"  # menu / play / how / credits
        self.menu_items = ["PLAY GAME", "HOW TO PLAY", "CREDITS", "EXIT"]
        self.menu_index = 0
        self.reset_game()

    def reset_game(self):
        self.lives = 5
        self.score = 0
        self.paddle_x = LW // 2 - PADDLE_W // 2

        self.ball_wait = True
        self.ball_x_fp = 0
        self.ball_y_fp = 0
        self.vx_fp = 0
        self.vy_fp = 0

        self.bricks = [[1] * BRICK_COLS for _ in range(BRICK_ROWS)]
        self.reset_ball()

    def reset_ball(self):
        self.ball_wait = True
        self.ball_x_fp = to_fp(self.paddle_x + (PADDLE_W - BALL_SIZE) / 2)
        self.ball_y_fp = to_fp(PADDLE_Y - BALL_SIZE)
        self.vx_fp = 0
        self.vy_fp = 0

    def launch_ball(self):
        a = math.radians(random.choice([-60, -45, -30, 30, 45, 60]))
        sp = 1.80
        self.vx_fp = int(sp * math.sin(a) * FP) or FP
        self.vy_fp = int(-sp * math.cos(a) * FP) or -FP
        self.ball_wait = False

    # ───────── MENU INPUT ─────────
    def update_menu(self, click, keys_down, hover_index):
        moved = False
        if pygame.K_UP in keys_down:
            self.menu_index = (self.menu_index - 1) % len(self.menu_items)
            moved = True
        if pygame.K_DOWN in keys_down:
            self.menu_index = (self.menu_index + 1) % len(self.menu_items)
            moved = True
        if moved:
            self.sfx.select()

        if hover_index is not None and hover_index != self.menu_index:
            self.menu_index = hover_index
            self.sfx.select()

        if click or (pygame.K_RETURN in keys_down) or (pygame.K_SPACE in keys_down):
            self.sfx.start()
            choice = self.menu_index
            if choice == 0:
                self.reset_game()
                self.state = "play"
            elif choice == 1:
                self.state = "how"
            elif choice == 2:
                self.state = "credits"
            elif choice == 3:
                pygame.quit()
                sys.exit()

    def update_backable(self, click, keys_down):
        if click or (pygame.K_ESCAPE in keys_down) or (pygame.K_RETURN in keys_down) or (pygame.K_SPACE in keys_down):
            self.sfx.select()
            self.state = "menu"

    # ───────── PLAY UPDATE ─────────
    def update_play(self, mx, click, keys_down):
        if pygame.K_ESCAPE in keys_down:
            self.sfx.select()
            self.state = "menu"
            return

        self.paddle_x = int(clamp(mx - PADDLE_W / 2, BORDER_L, BORDER_R - PADDLE_W))

        # waiting serve
        if self.ball_wait:
            self.ball_x_fp = to_fp(self.paddle_x + (PADDLE_W - BALL_SIZE) / 2)
            self.ball_y_fp = to_fp(PADDLE_Y - BALL_SIZE)
            if click or (pygame.K_SPACE in keys_down) or (pygame.K_RETURN in keys_down):
                self.launch_ball()
                self.sfx.launch()
            return

        # move ball
        self.ball_x_fp += self.vx_fp
        self.ball_y_fp += self.vy_fp

        bx = self.ball_x_fp // FP
        by = self.ball_y_fp // FP

        # speed for dynamic pitch
        spd = math.sqrt((self.vx_fp / FP) ** 2 + (self.vy_fp / FP) ** 2)

        # walls (clamp + bounce)
        if bx <= BORDER_L:
            self.ball_x_fp = BORDER_L * FP
            self.vx_fp *= -1
            bx = BORDER_L
            self.sfx.wall(spd)
        elif bx >= (BORDER_R - BALL_SIZE):
            self.ball_x_fp = (BORDER_R - BALL_SIZE) * FP
            self.vx_fp *= -1
            bx = (BORDER_R - BALL_SIZE)
            self.sfx.wall(spd)

        if by <= BORDER_T:
            self.ball_y_fp = BORDER_T * FP
            self.vy_fp *= -1
            by = BORDER_T
            self.sfx.wall(spd)

        ball = pygame.Rect(int(bx), int(by), BALL_SIZE, BALL_SIZE)
        paddle = pygame.Rect(self.paddle_x, PADDLE_Y, PADDLE_W, PADDLE_H)

        # paddle bounce
        if ball.colliderect(paddle) and self.vy_fp > 0:
            self.ball_y_fp = (PADDLE_Y - BALL_SIZE) * FP
            self.vy_fp *= -1
            rel = ((bx + BALL_SIZE * 0.5) - self.paddle_x) / float(PADDLE_W)
            self.sfx.paddle(rel)

        # bricks
        hit = False
        for r in range(BRICK_ROWS):
            if hit:
                break
            ry = BRICK_Y + r * BRICK_H
            for c in range(BRICK_COLS):
                if not self.bricks[r][c]:
                    continue
                rx = BRICK_X + c * BRICK_W
                rect = pygame.Rect(rx, ry, BRICK_W, BRICK_H)
                if ball.colliderect(rect):
                    self.bricks[r][c] = 0
                    self.score += POINTS[r]
                    self.vy_fp *= -1
                    self.sfx.brick(r)
                    hit = True
                    break

        # miss
        if (self.ball_y_fp // FP) > LH:
            self.lives -= 1
            self.sfx.lose()
            if self.lives <= 0:
                self.state = "menu"
            self.reset_ball()

    # ───────── DRAW ─────────
    def draw_menu(self, surf, f_title, f_menu, f_small, mx, my, sfx_on: bool):
        surf.fill(BLACK)

        title = f_title.render("Ultra! Tetris 1.x", False, WHITE)
        surf.blit(title, title.get_rect(center=(LW // 2, 32)))

        sub = f_small.render("Ultra!BREAKOUT — PYGOTHIC", False, TEXT)
        surf.blit(sub, sub.get_rect(center=(LW // 2, 50)))

        hover = None
        for i, item in enumerate(self.menu_items):
            y = 92 + i * 22
            col = DIM
            txt = f_menu.render(item, False, col)
            rect = txt.get_rect(center=(LW // 2, y))
            if rect.collidepoint(mx, my):
                hover = i
            is_sel = (hover == i) or (self.menu_index == i)
            col = WHITE if is_sel else DIM
            txt = f_menu.render(item, False, col)
            surf.blit(txt, rect)

        footer = [
            "(C) SAMSOFT",
            "(C) ATARI 1972-2026",
            "(C) SAMSOFT 1999-2026",
        ]
        base_y = LH - 56
        for i, line in enumerate(footer):
            t = f_small.render(line, False, TEXT)
            surf.blit(t, t.get_rect(center=(LW // 2, base_y + i * 12)))

        sline = f_small.render(f"SFX {'ON' if sfx_on else 'OFF'}  (PRESS S)", False, TEXT)
        surf.blit(sline, sline.get_rect(center=(LW // 2, LH - 18)))

        hint = f_small.render("UP/DOWN + ENTER  |  CLICK TO SELECT", False, TEXT)
        surf.blit(hint, hint.get_rect(center=(LW // 2, LH - 6)))

        return hover

    def draw_how(self, surf, f_small):
        surf.fill(BLACK)
        lines = [
            "HOW TO PLAY",
            "",
            "MOUSE MOVES PADDLE",
            "CLICK / SPACE / ENTER TO LAUNCH",
            "",
            "BREAK BRICKS FOR SCORE",
            "PYGOTHIC BRICKS = WHITE + OUTLINE",
            "",
            "ESC IN GAME = MENU",
            "S = TOGGLE SFX",
            "",
            "CLICK / SPACE / ESC TO RETURN",
        ]
        for i, line in enumerate(lines):
            t = f_small.render(line, False, TEXT)
            surf.blit(t, t.get_rect(center=(LW // 2, 36 + i * 14)))

    def draw_credits(self, surf, f_small):
        surf.fill(BLACK)
        lines = [
            "CREDITS",
            "",
            "Ultra! Tetris 1.x",
            "(C) SAMSOFT",
            "(C) ATARI 1972-2026",
            "(C) SAMSOFT 1999-2026",
            "",
            "GAME: Ultra!BREAKOUT — PYGOTHIC",
            "DYNAMIC SFX: GENERATED (NO FILES)",
            "",
            "CLICK / SPACE / ESC TO RETURN",
        ]
        for i, line in enumerate(lines):
            t = f_small.render(line, False, TEXT)
            surf.blit(t, t.get_rect(center=(LW // 2, 36 + i * 14)))

    def draw_play(self, surf, f_small, sfx_on: bool):
        surf.fill(BLACK)

        # PYGOTHIC BRICKS (white fill + black outline)
        for r in range(BRICK_ROWS):
            for c in range(BRICK_COLS):
                if self.bricks[r][c]:
                    rect = pygame.Rect(
                        BRICK_X + c * BRICK_W,
                        BRICK_Y + r * BRICK_H,
                        BRICK_W,
                        BRICK_H,
                    )
                    pygame.draw.rect(surf, WHITE, rect)
                    pygame.draw.rect(surf, BLACK, rect, 1)

        # paddle + ball
        pygame.draw.rect(surf, WHITE, (self.paddle_x, PADDLE_Y, PADDLE_W, PADDLE_H))
        bx = self.ball_x_fp // FP
        by = self.ball_y_fp // FP
        pygame.draw.rect(surf, WHITE, (bx, by, BALL_SIZE, BALL_SIZE))

        # HUD
        surf.blit(f_small.render(f"SCORE {self.score}", False, WHITE), (8, 8))
        surf.blit(f_small.render(f"BALLS {self.lives}", False, WHITE), (LW - 88, 8))
        surf.blit(f_small.render(f"SFX {'ON' if sfx_on else 'OFF'}", False, TEXT), (LW // 2 - 24, 8))

        if self.ball_wait:
            msg = f_small.render("READY  CLICK/SPACE", False, TEXT)
            surf.blit(msg, msg.get_rect(center=(LW // 2, LH - 18)))

    def update(self, mx, my, click, keys_down, hover_index):
        if self.state == "menu":
            self.update_menu(click, keys_down, hover_index)
        elif self.state == "how":
            self.update_backable(click, keys_down)
        elif self.state == "credits":
            self.update_backable(click, keys_down)
        elif self.state == "play":
            self.update_play(mx, click, keys_down)

    def draw(self, surf, f_title, f_menu, f_small, mx, my, sfx_on: bool):
        if self.state == "menu":
            return self.draw_menu(surf, f_title, f_menu, f_small, mx, my, sfx_on)
        elif self.state == "how":
            self.draw_how(surf, f_small)
        elif self.state == "credits":
            self.draw_credits(surf, f_small)
        elif self.state == "play":
            self.draw_play(surf, f_small, sfx_on)
        return None


# ───────────────── MAIN ─────────────────
def main():
    # Pre-init audio BEFORE init for best reliability.
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()

    screen = pygame.display.set_mode((SW, SH))
    pygame.display.set_caption("Ultra!BREAKOUT — PYGOTHIC")
    clock = pygame.time.Clock()

    frame = pygame.Surface((LW, LH))

    f_title = pygame.font.SysFont("monospace", 20, bold=True)
    f_menu  = pygame.font.SysFont("monospace", 14, bold=True)
    f_small = pygame.font.SysFont("monospace", 10)

    sfx = DynamicSFX()
    game = UltraBreakout(sfx)

    while True:
        click = False
        keys_down = set()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                click = True

            if e.type == pygame.KEYDOWN:
                keys_down.add(e.key)
                if e.key == pygame.K_s:
                    sfx.toggle()

        mx, my = pygame.mouse.get_pos()
        mx //= SCALE
        my //= SCALE

        hover = game.draw(frame, f_title, f_menu, f_small, mx, my, sfx.on)
        game.update(mx, my, click, keys_down, hover)

        pygame.transform.scale(frame, (SW, SH), screen)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
 
