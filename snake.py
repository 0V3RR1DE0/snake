import pygame
import time
import random
import winsound
from collections import deque

pygame.init()

# Game Variables
screen_width = 800
screen_height = 600
snake_block_size = 20
snake_speed = 15

# Colors
color_white = (255, 255, 255)
color_red = (255, 0, 0)
color_black = (0, 0, 0)
color_green = (0, 255, 0)
color_dark_green = (0, 200, 0)
color_yellow = (255, 255, 0)
color_blue = (0, 0, 255)
color_light_blue = (173, 216, 230)

# Path line thickness
path_line_thickness = 2

# Fonts
font_style = pygame.font.SysFont("Roboto", 30)
score_font = pygame.font.SysFont("Roboto", 35)

game_display = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Snake Game with Improved Pathfinding Bot')

clock = pygame.time.Clock()

DIRECTIONS = [(-snake_block_size, 0), (snake_block_size, 0), (0, -snake_block_size), (0, snake_block_size)]

def display_score(score, high_score):
    value = score_font.render(f"Score: {score}  High Score: {high_score}", True, color_white)
    game_display.blit(value, [10, 10])

def draw_snake(snake_block_size, snake_body):
    for index, block in enumerate(snake_body):
        if index == len(snake_body) - 1:
            pygame.draw.rect(game_display, color_yellow, [block[0], block[1], snake_block_size, snake_block_size])
        else:
            pygame.draw.rect(game_display, color_dark_green, [block[0], block[1], snake_block_size, snake_block_size])

def message(msg, color, pos):
    mesg = font_style.render(msg, True, color)
    game_display.blit(mesg, pos)

def play_chirp_sound():
    winsound.Beep(1000, 100)

def play_crash_sound():
    winsound.MessageBeep(winsound.MB_ICONHAND)

def bfs(snake_head, food, snake_body):
    start = tuple(snake_head)
    goal = tuple(food)
    queue = deque([start])
    came_from = {start: None}
    body_set = set(map(tuple, snake_body))

    while queue:
        current = queue.popleft()
        if current == goal:
            break
        for direction in DIRECTIONS:
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if (0 <= neighbor[0] < screen_width and
                0 <= neighbor[1] < screen_height and
                neighbor not in came_from and
                neighbor not in body_set):
                queue.append(neighbor)
                came_from[neighbor] = current

    path = []
    current = goal
    while current != start:
        if current is None:
            return []
        path.append(current)
        current = came_from.get(current)
    path.reverse()
    return path

def find_safe_move(snake_head, snake_body, food):
    safe_moves = []
    for direction in DIRECTIONS:
        next_move = [snake_head[0] + direction[0], snake_head[1] + direction[1]]
        if (0 <= next_move[0] < screen_width and 
            0 <= next_move[1] < screen_height and 
            next_move not in snake_body):
            if not is_enclosed(next_move, snake_body + [snake_head]):
                safe_moves.append(direction)
    
    if safe_moves:
        return min(safe_moves, key=lambda x: ((snake_head[0] + x[0] - food[0])**2 + (snake_head[1] + x[1] - food[1])**2))
    return None

def is_enclosed(position, obstacles):
    open_spaces = 0
    for direction in DIRECTIONS:
        neighbor = (position[0] + direction[0], position[1] + direction[1])
        if (0 <= neighbor[0] < screen_width and
            0 <= neighbor[1] < screen_height and
            list(neighbor) not in obstacles):
            open_spaces += 1
    return open_spaces <= 1

def spawn_food(snake_body):
    while True:
        food_x = round(random.randrange(0, screen_width - snake_block_size) / 20.0) * 20.0
        food_y = round(random.randrange(0, screen_height - snake_block_size) / 20.0) * 20.0
        if [food_x, food_y] not in snake_body:
            return food_x, food_y

def draw_path(path):
    if len(path) > 1:
        pixel_path = [(p[0] + snake_block_size // 2, p[1] + snake_block_size // 2) for p in path]
        pygame.draw.lines(game_display, color_light_blue, False, pixel_path, path_line_thickness)

def game_loop():
    global path_line_thickness
    game_over = False
    game_close = False
    bot_mode = False

    x1 = screen_width / 2
    y1 = screen_height / 2
    x1_change = 0
    y1_change = 0

    snake_body = [[x1, y1]]
    snake_length = 1

    score = 0
    high_score = 0

    try:
        with open("high_score.txt", "r") as file:
            high_score = int(file.read())
    except FileNotFoundError:
        high_score = 0

    food_x, food_y = spawn_food(snake_body)

    path_to_apple = []
    calculating_path = True

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
                if event.key == pygame.K_b:
                    bot_mode = not bot_mode
                    if bot_mode:
                        path_to_apple = []
                        calculating_path = True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_PLUS] or keys[pygame.K_EQUALS]:
            path_line_thickness = min(path_line_thickness + 1, 10)
        elif keys[pygame.K_MINUS]:
            path_line_thickness = max(path_line_thickness - 1, 1)

        if bot_mode:
            if calculating_path or not path_to_apple:
                path_to_apple = bfs(snake_body[-1], [food_x, food_y], snake_body)
                calculating_path = False

            if path_to_apple:
                next_move = path_to_apple.pop(0)
                x1_change = next_move[0] - snake_body[-1][0]
                y1_change = next_move[1] - snake_body[-1][1]
            else:
                safe_move = find_safe_move(snake_body[-1], snake_body, [food_x, food_y])
                if safe_move:
                    x1_change, y1_change = safe_move
                else:
                    x1_change, y1_change = 0, 0
        else:
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

        if x1 >= screen_width or x1 < 0 or y1 >= screen_height or y1 < 0:
            play_crash_sound()
            game_close = True

        for segment in snake_body[:-1]:
            if segment == [x1, y1]:
                play_crash_sound()
                game_close = True

        snake_body.append([x1, y1])
        if len(snake_body) > snake_length:
            del snake_body[0]

        game_display.fill(color_black)
        if bot_mode:
            draw_path(path_to_apple)
        draw_snake(snake_block_size, snake_body)
        pygame.draw.rect(game_display, color_red, [food_x, food_y, snake_block_size, snake_block_size])

        display_score(score, high_score)

        thickness_text = font_style.render(f"Line Thickness: {path_line_thickness}", True, color_white)
        game_display.blit(thickness_text, [10, screen_height - 40])

        pygame.display.update()

        if x1 == food_x and y1 == food_y:
            play_chirp_sound()
            food_x, food_y = spawn_food(snake_body)
            snake_length += 1
            score += 1

            if score > high_score:
                high_score = score
                with open("high_score.txt", "w") as file:
                    file.write(str(high_score))

            path_to_apple = []
            calculating_path = True

        clock.tick(snake_speed)

    pygame.quit()
    quit()

game_loop()
