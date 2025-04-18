import curses
import json
import time
import random

# Settings
WIDTH = 60
HEIGHT = 20
PADDLE_HEIGHT = 5
BALL_SPEED_INCREMENT = 0.5
MAX_SCORE = 5
LEADERBOARD_FILE = "wynik.json"

class PongGame:
    def __init__(self, screen, mode):
        self.screen = screen
        self.mode = mode  # AI or Multi 
        self.screen.timeout(0)
        curses.curs_set(0)

        # Create Paddle and ball
        self.left_paddle_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.right_paddle_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.ball_x, self.ball_y = WIDTH // 2, HEIGHT // 2
        self.ball_dx, self.ball_dy = random.choice([-1, 1]), random.choice([-1, 1])
        self.ball_speed = 0.1

        # Scores
        self.left_score = 0
        self.right_score = 0

    def draw(self):
        self.screen.clear()

        # Draw Box
        for x in range(WIDTH):
            self.screen.addch(0, x, "*")
            self.screen.addch(HEIGHT - 1, x, "*")
        for y in range(HEIGHT):
            self.screen.addch(y, 0, "*")
            self.screen.addch(y, WIDTH - 1, "*")

        # Draw paddles
        for i in range(PADDLE_HEIGHT):
            self.screen.addch(self.left_paddle_y + i, 1, "X")
            self.screen.addch(self.right_paddle_y + i, WIDTH - 2, "X")

        # Draw ball
        self.screen.addch(self.ball_y, self.ball_x, "O")

        # Draw scores
        self.screen.addstr(0, WIDTH // 4, f"Player 1: {self.left_score}")
        self.screen.addstr(0, WIDTH * 3 // 4 - 10, f"Player 2: {self.right_score}")

        self.screen.refresh()

    def handle_input(self):
        key = self.screen.getch()
        if self.mode == "Multiplayer":
            # Multiplayer logic
            if key == curses.KEY_UP and self.right_paddle_y > 1:
                self.right_paddle_y -= 1
            elif key == curses.KEY_DOWN and self.right_paddle_y < HEIGHT - PADDLE_HEIGHT - 1:
                self.right_paddle_y += 1
        elif self.mode == "AI":
            # AI player logic
            if self.ball_y < self.right_paddle_y and self.right_paddle_y > 1:
                self.right_paddle_y -= 1
            elif self.ball_y > self.right_paddle_y + PADDLE_HEIGHT - 1 and self.right_paddle_y < HEIGHT - PADDLE_HEIGHT - 1:
                self.right_paddle_y += 1

        # Player 1 logic        
        if key == ord('w') and self.left_paddle_y > 1:
            self.left_paddle_y -= 1
        elif key == ord('s') and self.left_paddle_y < HEIGHT - PADDLE_HEIGHT - 1:
            self.left_paddle_y += 1

    def update_ball(self):
        # Ball movement
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Ball collision
        if self.ball_y <= 1 or self.ball_y >= HEIGHT - 2:
            self.ball_dy = -self.ball_dy

        # Ball collision with paddles
        if self.ball_x == 2 and self.left_paddle_y <= self.ball_y < self.left_paddle_y + PADDLE_HEIGHT:
            self.ball_dx = -self.ball_dx
            self.ball_speed = max(self.ball_speed - BALL_SPEED_INCREMENT, 0.05)
        elif self.ball_x == WIDTH - 3 and self.right_paddle_y <= self.ball_y < self.right_paddle_y + PADDLE_HEIGHT:
            self.ball_dx = -self.ball_dx
            self.ball_speed = max(self.ball_speed - BALL_SPEED_INCREMENT, 0.05)

        # Ball scores
        if self.ball_x <= 0:
            self.right_score += 1
            self.reset_ball()
        elif self.ball_x >= WIDTH - 1:
            self.left_score += 1
            self.reset_ball()

    def reset_ball(self):
        # Reset ball
        self.ball_x, self.ball_y = WIDTH // 2, HEIGHT // 2
        self.ball_dx, self.ball_dy = random.choice([-1, 1]), random.choice([-1, 1])
        self.ball_speed = 0.1

    def save_leaderboard(self, winner):
        # Leaderboard
        try:
            with open(LEADERBOARD_FILE, "r") as file:
                leaderboard = json.load(file)
        except FileNotFoundError:
            leaderboard = {}

        leaderboard[winner] = leaderboard.get(winner, 0) + 1

        with open(LEADERBOARD_FILE, "w") as file:
            json.dump(leaderboard, file)

    def play(self):
        # Main game loop
        while True:
            self.handle_input()
            self.update_ball()
            self.draw()

            # Check for win condition
            if self.left_score >= MAX_SCORE:
                self.save_leaderboard("Player 1")
                self.screen.addstr(HEIGHT // 2, WIDTH // 2 - 10, "Player 1 Wins!")
                self.screen.refresh()
                time.sleep(2)
                break
            elif self.right_score >= MAX_SCORE:
                self.save_leaderboard("Player 2")
                self.screen.addstr(HEIGHT // 2, WIDTH // 2 - 10, "Player 2 Wins!")
                self.screen.refresh()
                time.sleep(2)
                break

            time.sleep(self.ball_speed)

def main_menu(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.addstr(HEIGHT // 2 - 2, WIDTH // 2 - 10, "Pong THE Game")
    stdscr.addstr(HEIGHT // 2, WIDTH // 2 - 15, "Press 1 for AI")
    stdscr.addstr(HEIGHT // 2 + 1, WIDTH // 2 - 15, "Press 2 for Multiplayer Mode")
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == ord('1'):
            return "AI"
        elif key == ord('2'):
            return "Multiplayer"

def main(stdscr):
    mode = main_menu(stdscr)
    game = PongGame(stdscr, mode)
    game.play()

curses.wrapper(main)