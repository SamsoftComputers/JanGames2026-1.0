#!/usr/bin/env python3
"""
Classic Pong Game
A complete two-player Pong implementation using Python's turtle module.

Controls:
- Player 1 (Left): W (up), S (down)
- Player 2 (Right): Up Arrow (up), Down Arrow (down)
- Press Q or close window to quit
"""

import turtle
import time

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100
BALL_SIZE = 20
PADDLE_SPEED = 30
BALL_SPEED_X = 4
BALL_SPEED_Y = 4
WINNING_SCORE = 11


class Paddle:
    """Represents a player's paddle."""

    def __init__(self, x_position):
        self.turtle = turtle.Turtle()
        self.turtle.speed(0)
        self.turtle.shape("square")
        self.turtle.color("white")
        self.turtle.shapesize(stretch_wid=PADDLE_HEIGHT/20, stretch_len=PADDLE_WIDTH/20)
        self.turtle.penup()
        self.turtle.goto(x_position, 0)

    def move_up(self):
        """Move paddle up if not at top boundary."""
        y = self.turtle.ycor()
        max_y = (SCREEN_HEIGHT / 2) - (PADDLE_HEIGHT / 2) - 10
        if y < max_y:
            self.turtle.sety(y + PADDLE_SPEED)

    def move_down(self):
        """Move paddle down if not at bottom boundary."""
        y = self.turtle.ycor()
        min_y = -(SCREEN_HEIGHT / 2) + (PADDLE_HEIGHT / 2) + 10
        if y > min_y:
            self.turtle.sety(y - PADDLE_SPEED)

    def get_position(self):
        """Return current paddle position."""
        return self.turtle.xcor(), self.turtle.ycor()


class Ball:
    """Represents the game ball."""

    def __init__(self):
        self.turtle = turtle.Turtle()
        self.turtle.speed(0)
        self.turtle.shape("circle")
        self.turtle.color("white")
        self.turtle.shapesize(stretch_wid=BALL_SIZE/20, stretch_len=BALL_SIZE/20)
        self.turtle.penup()
        self.turtle.goto(0, 0)
        self.dx = BALL_SPEED_X
        self.dy = BALL_SPEED_Y

    def move(self):
        """Move ball by its velocity."""
        x = self.turtle.xcor() + self.dx
        y = self.turtle.ycor() + self.dy
        self.turtle.goto(x, y)

    def bounce_y(self):
        """Reverse vertical direction."""
        self.dy *= -1

    def bounce_x(self):
        """Reverse horizontal direction and slightly increase speed."""
        self.dx *= -1.05
        self.dy *= 1.05
        # Cap max speed
        max_speed = 15
        if abs(self.dx) > max_speed:
            self.dx = max_speed if self.dx > 0 else -max_speed
        if abs(self.dy) > max_speed:
            self.dy = max_speed if self.dy > 0 else -max_speed

    def reset(self, direction=1):
        """Reset ball to center with given horizontal direction."""
        self.turtle.goto(0, 0)
        self.dx = BALL_SPEED_X * direction
        self.dy = BALL_SPEED_Y * (1 if self.dy > 0 else -1)

    def get_position(self):
        """Return current ball position."""
        return self.turtle.xcor(), self.turtle.ycor()


class Scoreboard:
    """Displays and tracks the score."""

    def __init__(self):
        self.turtle = turtle.Turtle()
        self.turtle.speed(0)
        self.turtle.color("white")
        self.turtle.penup()
        self.turtle.hideturtle()
        self.turtle.goto(0, SCREEN_HEIGHT / 2 - 60)
        self.score_left = 0
        self.score_right = 0
        self.update_display()

    def update_display(self):
        """Update the score display."""
        self.turtle.clear()
        self.turtle.write(
            f"{self.score_left}  :  {self.score_right}",
            align="center",
            font=("Courier", 48, "bold")
        )

    def score_point_left(self):
        """Add point to left player."""
        self.score_left += 1
        self.update_display()
        return self.score_left >= WINNING_SCORE

    def score_point_right(self):
        """Add point to right player."""
        self.score_right += 1
        self.update_display()
        return self.score_right >= WINNING_SCORE

    def reset(self):
        """Reset scores to zero."""
        self.score_left = 0
        self.score_right = 0
        self.update_display()


class GameOverScreen:
    """Displays game over message."""

    def __init__(self):
        self.turtle = turtle.Turtle()
        self.turtle.speed(0)
        self.turtle.color("yellow")
        self.turtle.penup()
        self.turtle.hideturtle()
        self.turtle.goto(0, 0)

    def show_winner(self, winner):
        """Display the winner."""
        self.turtle.clear()
        self.turtle.write(
            f"Player {winner} Wins!",
            align="center",
            font=("Courier", 36, "bold")
        )
        self.turtle.goto(0, -60)
        self.turtle.write(
            "Press SPACE to play again or Q to quit",
            align="center",
            font=("Courier", 18, "normal")
        )

    def clear(self):
        """Clear the game over message."""
        self.turtle.clear()


class PongGame:
    """Main game controller."""

    def __init__(self):
        # Set up screen
        self.screen = turtle.Screen()
        self.screen.title("PONG")
        self.screen.bgcolor("black")
        self.screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        self.screen.tracer(0)

        # Draw center line
        self.draw_center_line()

        # Create game objects
        self.paddle_left = Paddle(-SCREEN_WIDTH/2 + 40)
        self.paddle_right = Paddle(SCREEN_WIDTH/2 - 40)
        self.ball = Ball()
        self.scoreboard = Scoreboard()
        self.game_over_screen = GameOverScreen()

        # Game state
        self.running = True
        self.game_active = True

        # Set up controls
        self.setup_controls()

    def draw_center_line(self):
        """Draw dashed center line."""
        line = turtle.Turtle()
        line.speed(0)
        line.color("white")
        line.penup()
        line.goto(0, SCREEN_HEIGHT/2)
        line.pendown()
        line.setheading(270)

        # Draw dashed line
        dash_length = 20
        gap_length = 15
        y = SCREEN_HEIGHT/2
        while y > -SCREEN_HEIGHT/2:
            line.forward(dash_length)
            line.penup()
            line.forward(gap_length)
            line.pendown()
            y -= (dash_length + gap_length)

        line.hideturtle()

    def setup_controls(self):
        """Set up keyboard controls."""
        self.screen.listen()

        # Player 1 controls (left paddle)
        self.screen.onkeypress(self.paddle_left.move_up, "w")
        self.screen.onkeypress(self.paddle_left.move_up, "W")
        self.screen.onkeypress(self.paddle_left.move_down, "s")
        self.screen.onkeypress(self.paddle_left.move_down, "S")

        # Player 2 controls (right paddle)
        self.screen.onkeypress(self.paddle_right.move_up, "Up")
        self.screen.onkeypress(self.paddle_right.move_down, "Down")

        # Game controls
        self.screen.onkeypress(self.quit_game, "q")
        self.screen.onkeypress(self.quit_game, "Q")
        self.screen.onkeypress(self.restart_game, "space")

    def quit_game(self):
        """Quit the game."""
        self.running = False

    def restart_game(self):
        """Restart the game after game over."""
        if not self.game_active:
            self.scoreboard.reset()
            self.ball.reset()
            self.game_over_screen.clear()
            self.game_active = True

    def check_wall_collision(self):
        """Check and handle ball collision with top/bottom walls."""
        ball_x, ball_y = self.ball.get_position()

        # Top wall
        if ball_y > SCREEN_HEIGHT/2 - BALL_SIZE:
            self.ball.turtle.sety(SCREEN_HEIGHT/2 - BALL_SIZE)
            self.ball.bounce_y()

        # Bottom wall
        if ball_y < -SCREEN_HEIGHT/2 + BALL_SIZE:
            self.ball.turtle.sety(-SCREEN_HEIGHT/2 + BALL_SIZE)
            self.ball.bounce_y()

    def check_paddle_collision(self):
        """Check and handle ball collision with paddles."""
        ball_x, ball_y = self.ball.get_position()

        # Right paddle collision
        paddle_x, paddle_y = self.paddle_right.get_position()
        if (ball_x > paddle_x - PADDLE_WIDTH and
            ball_x < paddle_x + PADDLE_WIDTH and
            ball_y < paddle_y + PADDLE_HEIGHT/2 + 10 and
            ball_y > paddle_y - PADDLE_HEIGHT/2 - 10 and
            self.ball.dx > 0):
            self.ball.turtle.setx(paddle_x - PADDLE_WIDTH)
            self.ball.bounce_x()
            # Add angle based on where ball hits paddle
            offset = (ball_y - paddle_y) / (PADDLE_HEIGHT/2)
            self.ball.dy += offset * 2

        # Left paddle collision
        paddle_x, paddle_y = self.paddle_left.get_position()
        if (ball_x < paddle_x + PADDLE_WIDTH and
            ball_x > paddle_x - PADDLE_WIDTH and
            ball_y < paddle_y + PADDLE_HEIGHT/2 + 10 and
            ball_y > paddle_y - PADDLE_HEIGHT/2 - 10 and
            self.ball.dx < 0):
            self.ball.turtle.setx(paddle_x + PADDLE_WIDTH)
            self.ball.bounce_x()
            # Add angle based on where ball hits paddle
            offset = (ball_y - paddle_y) / (PADDLE_HEIGHT/2)
            self.ball.dy += offset * 2

    def check_scoring(self):
        """Check if ball passed a paddle and update score."""
        ball_x, _ = self.ball.get_position()

        # Ball passed right side - left player scores
        if ball_x > SCREEN_WIDTH/2:
            game_won = self.scoreboard.score_point_left()
            if game_won:
                self.end_game(1)
            else:
                time.sleep(0.5)
                self.ball.reset(-1)

        # Ball passed left side - right player scores
        if ball_x < -SCREEN_WIDTH/2:
            game_won = self.scoreboard.score_point_right()
            if game_won:
                self.end_game(2)
            else:
                time.sleep(0.5)
                self.ball.reset(1)

    def end_game(self, winner):
        """End the game and show winner."""
        self.game_active = False
        self.game_over_screen.show_winner(winner)

    def run(self):
        """Main game loop."""
        while self.running:
            try:
                self.screen.update()

                if self.game_active:
                    self.ball.move()
                    self.check_wall_collision()
                    self.check_paddle_collision()
                    self.check_scoring()

                time.sleep(0.01)
            except turtle.Terminator:
                break
            except Exception as e:
                print(f"Game error: {e}")
                break

        try:
            self.screen.bye()
        except:
            pass


def main():
    """Entry point for the game."""
    print("=" * 50)
    print("           PONG - Classic Arcade Game")
    print("=" * 50)
    print()
    print("Controls:")
    print("  Player 1 (Left):  W = Up, S = Down")
    print("  Player 2 (Right): Up Arrow = Up, Down Arrow = Down")
    print()
    print(f"  First to {WINNING_SCORE} points wins!")
    print()
    print("  Press Q to quit")
    print("  Press SPACE to restart after game over")
    print()
    print("=" * 50)

    game = PongGame()
    game.run()

    print("\nThanks for playing!")


if __name__ == "__main__":
    main()
