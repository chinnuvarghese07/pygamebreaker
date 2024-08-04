import pygame
import random
import webbrowser  # Necessary for opening the registration link
import requests
import sys
import os
import logging

import subprocess
os.environ['DISPLAY'] = ':99'
# os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Use a dummy video driver
# os.environ['SDL_AUDIODRIVER'] = 'dummy'  # Use a dummy audio driver
# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BRICK_WIDTH = 80
BRICK_HEIGHT = 30
BALL_RADIUS = 10
PADDLE_WIDTH = 150
PADDLE_HEIGHT = 10
BALL_SPEED_X = 7
BALL_SPEED_Y = -7

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)  # Black for the paddle
BLUE = (0, 0, 255)  # Blue for the ball
SILVER = (192, 192, 192)
BLUE_BLACK = (10, 10, 40)  # Blue-Black color for the "Game Over" text

# Get the current working directory and player name passed from app.py
current_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
player_name = sys.argv[2] if len(sys.argv) > 2 else "Player"

# Load images using relative paths
copilot_background = pygame.image.load(os.path.join(current_dir, "images", "Copilot.jpg"))
microsoft_logo = pygame.image.load(os.path.join(current_dir, "images", "microsoft_logo.png"))
cns_logo = pygame.image.load(os.path.join(current_dir, "images", "CNS.png"))

# Scale images
copilot_background = pygame.transform.scale(copilot_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
microsoft_logo = pygame.transform.scale(microsoft_logo, (BRICK_WIDTH, BRICK_HEIGHT))
cns_logo = pygame.transform.scale(cns_logo, (BRICK_WIDTH, BRICK_HEIGHT))

# Game setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bricks Breaker")


ball = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
ball_speed = [BALL_SPEED_X, BALL_SPEED_Y]
paddle = pygame.Rect(SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, SCREEN_HEIGHT - 30, PADDLE_WIDTH, PADDLE_HEIGHT)
bricks = [pygame.Rect(col * BRICK_WIDTH, row * BRICK_HEIGHT, BRICK_WIDTH, BRICK_HEIGHT) for row in range(5) for col in range(10)]
score = 0
font = pygame.font.Font(None, 36)

# Registration Link
REGISTRATION_LINK = "https://forms.office.com/Pages/ResponsePage.aspx?id=Se8oF0VYv0ij-tILIIJR2WHObAW-S8lKjVDM86zOFEpUNUtBQk81Tko4SDlIRTgwVExNWkxSSTU5Sy4u"

# Add this function for celebration particles
def create_celebration_particles():
    particles = []
    for _ in range(100):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        dx = random.uniform(-2, 2)
        dy = random.uniform(-2, 2)
        radius = random.randint(2, 5)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        particles.append([x, y, dx, dy, radius, color])
    return particles

celebration_particles = []

# Set up logging
logging.basicConfig(filename='game_errors.log', level=logging.DEBUG)

# Game Loop
clock = pygame.time.Clock()
running = True
game_over = False
win = False
try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(copilot_background, (0, 0))
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         running = False

        mouse_x, mouse_y = pygame.mouse.get_pos()
        paddle.x = mouse_x - PADDLE_WIDTH // 2

        if not game_over:
            ball.x += ball_speed[0]
            ball.y += ball_speed[1]

            # Ball collision with walls
            if ball.left <= 0 or ball.right >= SCREEN_WIDTH:
                ball_speed[0] = -ball_speed[0]
            if ball.top <= 0:
                ball_speed[1] = -ball_speed[1]
            # Check if ball misses the paddle
            if ball.bottom >= SCREEN_HEIGHT:
                game_over = True

            # Ball collision with the paddle
            if ball.colliderect(paddle):
                ball_speed[1] = -ball_speed[1]

            # Ball collision with bricks
            for brick in bricks[:]:
                if ball.colliderect(brick):
                    ball_speed[1] = -ball_speed[1]  # Bounce the ball back
                    bricks.remove(brick)
                    score += 10

            # Check if all bricks are destroyed
            if not bricks:
                win = True
                game_over = True
                celebration_particles = create_celebration_particles()

        # Drawing game objects
        pygame.draw.rect(screen, BLACK, paddle)
        pygame.draw.ellipse(screen, BLUE, ball)

        for index, brick in enumerate(bricks):
            if index % 2 == 0:
                screen.blit(microsoft_logo, brick)
            else:
                screen.blit(cns_logo, brick)

        # Displaying the score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20, 20))

        # Handling game over state
        if game_over:
            if win:
                win_text = f"Congratulations, {player_name}! You Won with a score of {score}!"
                win_message = font.render(win_text, True, BLUE_BLACK)
                win_rect = win_message.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
                screen.blit(win_message, win_rect)
                
                register_text = "Register for a free license."
                register_message = font.render(register_text, True, BLUE_BLACK)
                register_rect = register_message.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))
                screen.blit(register_message, register_rect)
                
                # Update and draw celebration particles
                for particle in celebration_particles:
                    pygame.draw.circle(screen, particle[5], (int(particle[0]), int(particle[1])), particle[4])
                    particle[0] += particle[2]
                    particle[1] += particle[3]
                    if particle[0] < 0 or particle[0] > SCREEN_WIDTH or particle[1] < 0 or particle[1] > SCREEN_HEIGHT:
                        particle[0] = random.randint(0, SCREEN_WIDTH)
                        particle[1] = random.randint(0, SCREEN_HEIGHT)
                
                print("Register here:", REGISTRATION_LINK)
            else:
                game_over_text = font.render("Game Over", True, BLUE_BLACK)
                text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
                screen.blit(game_over_text, text_rect)

            exit_text = font.render("Press any key to exit", True, WHITE)
            exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50))
            screen.blit(exit_text, exit_rect)

        pygame.display.flip()
        clock.tick(60)

        if game_over:
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        running = False
                    if event.type == pygame.KEYDOWN:
                        waiting = False
                        running = False
except Exception as e:
    logging.exception("An error occurred while running the game: %s", e)

# At the end of your game loop, after pygame.quit()
import os

if win:
    with open('game_result.txt', 'w') as f:
        f.write('win')
else:
    with open('game_result.txt', 'w') as f:
        f.write('lose')

sys.exit()