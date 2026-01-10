#!/usr/bin/env python3
"""
ULTRAPONG! v0.2
Mouse vs AI Pong — NES/Famicom style (NO FILES)

Main Menu:
  ↑/↓ = Move  |  Enter = Select  |  ESC = Exit

In-game:
  Mouse = Move paddle
  M = Menu  |  ESC = Exit

Game Over:
  Y = Restart  |  N = Menu  |  ESC = Exit
"""

import sys, math, random
import pygame

# Optional (for synth sound)
try:
    import numpy as np
    NUMPY = True
except Exception:
    NUMPY = False

# ───────────────── INIT ─────────────────
# Pre-init mixer for lower latency (safe if mixer init fails later)
try:
    pygame.mixer.pre_init(22050, -16, 2, 512)
except Exception:
    pass

pygame.init()

SOUND = True and NUMPY
try:
    pygame.mixer.init(22050, -16, 2, 512)
    pygame.mixer.set_num_channels(8)
except pygame.error:
    SOUND = False

# ───────────────── COLORS (NES) ─────────────────
BLACK  = (0, 0, 0)
WHITE  = (252, 252, 252)
CYAN   = (0, 188, 188)
RED    = (188, 40, 40)
BLUE   = (0, 88, 248)
YELLOW = (248, 216, 0)
GREEN  = (0, 168, 0)

# ───────────────── SCREEN ─────────────────
W, H = 640, 480
TOP = 40
BOT = H - 10

# Try to enable vsync when available (pygame 2+); fall back cleanly.
_flags = pygame.DOUBLEBUF
try:
    screen = pygame.display.set_mode((W, H), _flags, vsync=1)
except TypeError:
    screen = pygame.display.set_mode((W, H), _flags)

pygame.display.set_caption("ULTRAPONG! v0.2")
clock = pygame.time.Clock()
FPS = 60

# Fixed-step update for authentic 60Hz console-like timing.
STEP = 1.0 / FPS
MAX_CATCHUP = 0.25  # seconds; avoids spiral of death if window is dragged / paused

# ───────────────── SOUND (FIXED STEREO) ─────────────────
class _NullSound:
    def play(self):  # noqa
        pass

def beep(freq, ms, vol=0.3):
    if not SOUND:
        return _NullSound()
    rate = 22050
    n = int(rate * ms / 1000)
    t = np.linspace(0, ms / 1000, n, endpoint=False)
    wave = np.sign(np.sin(2 * math.pi * freq * t))
    wave = (wave * vol * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)

snd_hit   = beep(440, 40)
snd_wall  = beep(330, 30)
snd_score = beep(220, 200)
snd_over  = beep(110, 500)
snd_start = beep(880, 120)
snd_move  = beep(660, 25)
snd_select= beep(990, 60)

# ───────────────── FONT ─────────────────
_font = {}
def text(msg, x, y, c=WHITE, s=32, center=False):
    if s not in _font:
        _font[s] = pygame.font.Font(None, s)
    surf = _font[s].render(msg, False, c)
    if center:
        x -= surf.get_width() // 2
    screen.blit(surf, (x, y))

def text_center(msg, y, c=WHITE, s=32):
    text(msg, W // 2, y, c, s, center=True)

# ───────────────── OBJECTS ─────────────────
PW, PH = 12, 60
BALL = 12
BR = BALL // 2

# These are effectively "pixels per frame" at 60Hz because we use fixed STEP.
PS = 8 * FPS   # paddle speed
BS = 5 * FPS   # ball start speed

# Atari-ish feel: discrete deflection angles + gentle speed ramp.
ATARI_BOUNCE = True
MAX_BALL_SPEED = 10 * FPS   # slightly lower cap feels more "Pong" than pinball-fast
BALL_ACCEL = 1.03           # keep your original ramp (console-like), but capped above

# Brief pause after each score/serve (classic Pong "ready" beat)
SERVE_PAUSE = int(0.55 * FPS)

class Paddle:
    def __init__(self, x):
        self.x = x
        self.y = H // 2 - PH // 2

    def rect(self):
        return pygame.Rect(self.x, int(self.y), PW, PH)

    def draw(self, c):
        pygame.draw.rect(screen, c, self.rect())

    def clamp(self):
        self.y = max(TOP, min(BOT - PH, self.y))

class BallObj:
    def __init__(self):
        self.reset()

    def reset(self, dir=None):
        self.x = W // 2
        self.y = H // 2
        d = random.choice([-1, 1]) if dir is None else dir

        # Classic-ish serve angles (avoid super-steep serves)
        if ATARI_BOUNCE:
            ang = math.radians(random.choice([-30, -15, 0, 15, 30]))
        else:
            ang = random.uniform(-0.35, 0.35)

        self.vx = d * BS * math.cos(ang)
        self.vy = BS * math.sin(ang)

    def rect(self):
        return pygame.Rect(int(self.x - BR), int(self.y - BR), BALL, BALL)

    def move(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

        top_y = TOP + BR
        bot_y = BOT - BR

        if self.y <= top_y:
            self.y = top_y
            self.vy *= -1
            snd_wall.play()
        elif self.y >= bot_y:
            self.y = bot_y
            self.vy *= -1
            snd_wall.play()

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect())

# ───────────────── GAME LOGIC ─────────────────
def collide(ball, p, left):
    if not ball.rect().colliderect(p.rect()):
        return False
    if left and ball.vx > 0:
        return False
    if (not left) and ball.vx < 0:
        return False

    # Push the ball out of the paddle so we never "double-hit" on overlap.
    if left:
        ball.x = p.x + PW + BR
    else:
        ball.x = p.x - BR

    off = (ball.y - (p.y + PH / 2)) / (PH / 2)
    off = max(-1.0, min(1.0, off))

    if ATARI_BOUNCE:
        # Discrete angles like classic Pong paddles.
        if abs(off) < 0.15:
            ang = 0.0
        else:
            mag = abs(off)
            if mag < 0.35:
                deg = 15
            elif mag < 0.60:
                deg = 30
            elif mag < 0.85:
                deg = 45
            else:
                deg = 60
            ang = math.radians(deg) * (1 if off > 0 else -1)
    else:
        ang = off * math.radians(60)

    sp = min(math.hypot(ball.vx, ball.vy) * BALL_ACCEL, MAX_BALL_SPEED)

    # Ensure the ball always leaves the paddle horizontally in the correct direction.
    ball.vx = abs(sp * math.cos(ang)) * (1 if left else -1)
    ball.vy = sp * math.sin(ang)

    # If we ended up *too* flat, nudge a hair so wall bounces still happen sometimes.
    if abs(ball.vy) < 0.10 * FPS and abs(off) > 0.15:
        ball.vy = (0.10 * FPS) * (1 if off > 0 else -1)

    snd_hit.play()
    return True

def draw_court():
    screen.fill(BLACK)
    pygame.draw.rect(screen, BLUE, (0, TOP - 5, W, 5))
    pygame.draw.rect(screen, BLUE, (0, BOT, W, 5))
    for y in range(TOP + 10, BOT, 25):
        pygame.draw.rect(screen, WHITE, (W // 2 - 2, y, 4, 15))

def _reflect_y(y):
    """Reflect y into the playfield (TOP+BR .. BOT-BR) as if it bounces off walls."""
    top_y = TOP + BR
    bot_y = BOT - BR
    span = bot_y - top_y
    if span <= 0:
        return top_y
    rel = y - top_y
    m = rel % (2 * span)
    if m < 0:
        m += 2 * span
    if m > span:
        m = 2 * span - m
    return top_y + m

def info_screen(title, lines):
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)

    while True:
        _ = clock.tick(FPS) / 1000  # stable timing (unused)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return "back"
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return "back"

        draw_court()
        text_center(title, 70, YELLOW, 54)

        y = 150
        for ln in lines:
            text_center(ln, y, WHITE, 26)
            y += 32

        text_center("ENTER/SPACE = BACK   ESC = BACK", H - 60, CYAN, 22)
        pygame.display.flip()

def menu_loop():
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)

    items = [
        ("START GAME", "start"),
        ("HOW TO PLAY", "how"),
        ("CREDITS", "credits"),
        ("EXIT", "quit"),
    ]
    idx = 0
    t_blink = 0.0

    while True:
        dt = clock.tick(FPS) / 1000
        t_blink += dt

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return "quit"
                if e.key in (pygame.K_UP, pygame.K_w):
                    idx = (idx - 1) % len(items)
                    snd_move.play()
                if e.key in (pygame.K_DOWN, pygame.K_s):
                    idx = (idx + 1) % len(items)
                    snd_move.play()
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    snd_select.play()
                    return items[idx][1]

        draw_court()
        text_center("ULTRAPONG!", 70, WHITE, 62)
        text_center("NES/Famicom Mouse Pong", 120, GREEN, 26)

        base_y = 190
        for i, (label, _) in enumerate(items):
            y = base_y + i * 44
            selected = (i == idx)
            c = YELLOW if selected else WHITE
            prefix = "▶ " if (selected and (int(t_blink * 3) % 2 == 0)) else "  "
            text(prefix + label, W // 2, y, c, 34, center=True)

        text_center("↑/↓ = MOVE   ENTER = SELECT   ESC = EXIT", H - 60, CYAN, 22)
        pygame.display.flip()

def _game_once():
    L = Paddle(30)
    R = Paddle(W - 30 - PW)
    B = BallObj()

    ps = 0
    cs = 0
    over = False

    serve_timer = SERVE_PAUSE  # tiny pause on start
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    snd_start.play()

    # AI: add a small, stable "miss" offset per incoming ball to feel human/retro.
    ai_err = 0.0
    last_toward_cpu = (B.vx > 0)

    acc = 0.0

    while True:
        # Busy-loop tick gives tighter 60Hz pacing (retro feel).
        frame_dt = clock.tick_busy_loop(FPS) / 1000.0
        acc = min(acc + frame_dt, MAX_CATCHUP)

        # --- events (once per rendered frame) ---
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.event.set_grab(False)
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.event.set_grab(False)
                    return "quit"
                if (not over) and e.key == pygame.K_m:
                    pygame.event.set_grab(False)
                    return "menu"
                if over:
                    if e.key == pygame.K_y:
                        pygame.event.set_grab(False)
                        return "restart"
                    if e.key == pygame.K_n:
                        pygame.event.set_grab(False)
                        return "menu"

        # --- fixed 60Hz updates ---
        while acc >= STEP:
            acc -= STEP

            if not over:
                # Player paddle = mouse (absolute position)
                _, my = pygame.mouse.get_pos()
                L.y = my - PH // 2
                L.clamp()

                # AI paddle (retro-ish): predict impact point when ball travels toward CPU,
                # otherwise drift back to center.
                toward_cpu = (B.vx > 0)
                if toward_cpu and (not last_toward_cpu):
                    ai_err = random.uniform(-14, 14)  # a little imperfection
                last_toward_cpu = toward_cpu

                if toward_cpu:
                    # Predict where the ball will be when it reaches the CPU paddle x.
                    dx = (R.x - (B.x + BR))
                    t = dx / B.vx if B.vx != 0 else 0.0
                    if t < 0:
                        t = 0.0
                    y_pred = _reflect_y(B.y + B.vy * t)
                    target = y_pred + ai_err
                else:
                    target = H / 2

                # Move AI toward target with a capped speed (slightly slower than player).
                ai_speed = PS * 0.82
                center = R.y + PH / 2
                if center < target - 2:
                    R.y += ai_speed * STEP
                elif center > target + 2:
                    R.y -= ai_speed * STEP
                R.clamp()

                if serve_timer > 0:
                    serve_timer -= 1
                else:
                    B.move(STEP)
                    hit_l = collide(B, L, True)
                    hit_r = collide(B, R, False)

                    # If the CPU just hit it back, refresh the "miss" a bit so rallies vary.
                    if hit_r:
                        ai_err = random.uniform(-10, 10)

                    if B.x < 0:
                        cs += 1
                        snd_score.play()
                        B.reset(-1)
                        serve_timer = SERVE_PAUSE
                    elif B.x > W:
                        ps += 1
                        snd_score.play()
                        B.reset(1)
                        serve_timer = SERVE_PAUSE

                    if ps == 5 or cs == 5:
                        over = True
                        snd_over.play()

        # --- draw ---
        draw_court()
        text(str(ps), W // 4, 5, CYAN, 36)
        text(str(cs), 3 * W // 4, 5, RED, 36)

        L.draw(CYAN)
        R.draw(RED)
        B.draw()

        if not over:
            text_center("M = MENU   ESC = EXIT", H - 30, BLUE, 20)
            if serve_timer > 0:
                text_center("READY", H // 2 - 8, YELLOW, 28)

        if over:
            text_center("GAME OVER", H // 2 - 40, WHITE, 54)
            winner = "YOU WIN!" if ps > cs else "CPU WINS!"
            text_center(winner, H // 2 + 10, YELLOW, 32)
            text_center("Y = RESTART   N = MENU   ESC = EXIT", H // 2 + 55, CYAN, 24)

        pygame.display.flip()

def game_loop():
    while True:
        result = _game_once()
        if result != "restart":
            return result

def app():
    while True:
        choice = menu_loop()
        if choice == "quit":
            return
        if choice == "how":
            r = info_screen("HOW TO PLAY", [
                "Move your paddle with the MOUSE.",
                "Hit the ball past the CPU to score.",
                "First to 5 points wins.",
                "",
                "In-game:  M = Menu   ESC = Exit",
            ])
            if r == "quit":
                return
        elif choice == "credits":
            r = info_screen("CREDITS", [
                "ULTRAPONG! v0.2 (No Files Edition)",
                "Code: Cat-san",
                "Tech: Python + pygame",
                "",
                "♡ vibe-coded goodness ♡",
            ])
            if r == "quit":
                return
        elif choice == "start":
            r = game_loop()
            if r == "quit":
                return
            # if r == "menu": just loop back to menu

if __name__ == "__main__":
    app()
    pygame.quit()
