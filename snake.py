import pygame
import time
import random
import winsound  # For system sounds (Windows only)
from collections import deque  # For BFS queue

# Initialize Pygame
pygame.init()

# Game Variables
screen_width = 800
screen_height = 600
snake_block_size = 20  # Snake size
snake_speed = 12       # Snake speed

# Colors
color_white = (255, 255, 255)
color_red = (255, 0, 0)
color_black = (0, 0, 0)
color_green = (0, 255, 0)
color_dark_green = (0, 200, 0)  # Snake body color
color_yellow = (255, 255, 0)    # Snake head color
color_blue = (0, 0, 255)        # Visualization for bot path

# Fonts
font_style = pygame.font.SysFont("Roboto", 30)  # Professional robotic font
score_font = pygame.font.SysFont("Roboto", 35)

# Game Window
game_display = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Snake Game with Pathfinding Bot')

# Clock to control frame rate
clock = pygame.time.Clock()

# Directions: LEFT, RIGHT, UP, DOWN
DIRECTIONS = [(-snake_block_size, 0), (snake_block_size, 0), (0, -snake_block_size), (0, snake_block_size)]

# Function to display score and high score
def display_score(score, high_score):
    value = score_font.render(f"Score: {score}  High Score: {high_score}", True, color_white)
    game_display.blit(value, [10, 10])

# Function to draw the snake with a distinct head
def draw_snake(snake_block_size, snake_body):
    for index, block in enumerate(snake_body):
        if index == len(snake_body) - 1:
            # Snake head
            pygame.draw.rect(game_display, color_yellow, [block[0], block[1], snake_block_size, snake_block_size])
        else:
            # Snake body
            pygame.draw.rect(game_display, color_dark_green, [block[0], block[1], snake_block_size, snake_block_size])

# Function to display a message on the screen
def message(msg, color, pos):
    mesg = font_style.render(msg, True, color)
    game_display.blit(mesg, pos)

# Function to play a chirp-like sound when the snake eats food
def play_chirp_sound():
    winsound.Beep(1000, 100)  # Beep at 1000 Hz for 100 milliseconds

# Function to play a crash sound when the snake crashes
def play_crash_sound():
    winsound.MessageBeep(winsound.MB_ICONHAND)

# Breadth-First Search (BFS) for pathfinding
def bfs(snake_head, food, snake_body):
    start = tuple(snake_head)
    goal = tuple(food)

    # Use a queue for BFS
    queue = deque([start])
    came_from = {start: None}  # Keeps track of the path
    body_set = set(map(tuple, snake_body))  # Make a set for O(1) collision checks

    while queue:
        current = queue.popleft()

        if current == goal:
            break

        # Explore neighbors in four directions
        for direction in DIRECTIONS:
            neighbor = (current[0] + direction[0], current[1] + direction[1])

            # Check boundaries and avoid the snake's body
            if (0 <= neighbor[0] < screen_width and
                0 <= neighbor[1] < screen_height and
                neighbor not in came_from and
                neighbor not in body_set):
                queue.append(neighbor)
                came_from[neighbor] = current

    # Reconstruct the path from the goal back to the start
    path = []
    current = goal
    while current != start:
        if current is None:  # If there's no path, return empty
            return []
        path.append(current)
        current = came_from.get(current, None)
    path.reverse()  # We constructed the path backwards, so reverse it
    return path

# Function to find a safe direction if no food is detected
def find_safe_move(snake_head, snake_body):
    for direction in DIRECTIONS:
        next_move = [snake_head[0] + direction[0], snake_head[1] + direction[1]]
        if (0 <= next_move[0] < screen_width and 0 <= next_move[1] < screen_height and next_move not in snake_body):
            return direction  # Return a safe direction
    return None  # No safe move found

# Function to spawn food avoiding the snake body
def spawn_food(snake_body):
    while True:
        food_x = round(random.randrange(0, screen_width - snake_block_size) / 20.0) * 20.0
        food_y = round(random.randrange(0, screen_height - snake_block_size) / 20.0) * 20.0
        if [food_x, food_y] not in snake_body:  # Ensure food doesn't spawn inside the snake
            return food_x, food_y

# Main game loop
def game_loop():
    # Initial game state
    game_over = False
    game_close = False
    bot_mode = False  # Start in human mode

    # Snake Starting Position
    x1 = screen_width / 2
    y1 = screen_height / 2
    x1_change = 0
    y1_change = 0

    snake_body = [[x1, y1]]
    snake_length = 1

    # Initial Score and High Score
    score = 0
    high_score = 0

    # Food Position
    food_x, food_y = spawn_food(snake_body)

    path_to_apple = []
    calculating_path = True  # Flag to control pathfinding process

    while not game_over:
        while game_close:
            game_display.fill(color_black)
            message("You Crashed! Press Q to Quit or C to Play Again", color_red, [screen_width / 6, screen_height / 3])
            display_score(score, high_score)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:  # Toggle bot mode
                    bot_mode = not bot_mode
                    if bot_mode:
                        # Reset for bot mode
                        path_to_apple = []
                        calculating_path = True

        # Pathfinding: Calculate path to apple in steps
        if bot_mode and calculating_path:
            path_to_apple = bfs(snake_body[-1], [food_x, food_y], snake_body)
            calculating_path = False  # Stop calculating until we consume the food

        if bot_mode and path_to_apple:
            # Move according to the path
            next_move = path_to_apple.pop(0)
            x1_change = next_move[0] - snake_body[-1][0]
            y1_change = next_move[1] - snake_body[-1][1]

            if not path_to_apple:  # If reached the food
                calculating_path = True  # Re-enable path calculation

        elif bot_mode and not path_to_apple:  # If no path found, try to avoid itself
            safe_move = find_safe_move(snake_body[-1], snake_body)
            if safe_move:
                x1_change, y1_change = safe_move

        elif not bot_mode:  # Normal human control
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                x1_change = -snake_block_size
                y1_change = 0
            elif keys[pygame.K_RIGHT]:
                x1_change = snake_block_size
                y1_change = 0
            elif keys[pygame.K_UP]:
                y1_change = -snake_block_size
                x1_change = 0
            elif keys[pygame.K_DOWN]:
                y1_change = snake_block_size
                x1_change = 0

        x1 += x1_change
        y1 += y1_change

        # Snake out of bounds check
        if x1 >= screen_width or x1 < 0 or y1 >= screen_height or y1 < 0:
            play_crash_sound()
            game_close = True

        # Snake collision with itself check
        for segment in snake_body[:-1]:
            if segment == [x1, y1]:
                play_crash_sound()
                game_close = True

        # Update the snake's body
        snake_body.append([x1, y1])
        if len(snake_body) > snake_length:
            del snake_body[0]

        # Drawing
        game_display.fill(color_black)
        draw_snake(snake_block_size, snake_body)
        pygame.draw.rect(game_display, color_red, [food_x, food_y, snake_block_size, snake_block_size])  # Apple

        display_score(score, high_score)

        # Check if snake ate food
        if x1 == food_x and y1 == food_y:
            play_chirp_sound()
            food_x, food_y = spawn_food(snake_body)
            snake_length += 1
            score += 1

            # Update high score
            if score > high_score:
                high_score = score

            path_to_apple = []  # Recalculate path
            calculating_path = True  # Allow new path calculation

        pygame.display.update()
        clock.tick(snake_speed)

    pygame.quit()
    quit()

# Start the Game
game_loop()
