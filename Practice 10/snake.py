import pygame
import random

# size of one grid cell (snake moves in steps of this size)
size = 30
half_size = size // 2

# window resolution
res = 750
# make resolution divisible by cell size (keeps grid aligned)
res = res // size // 2*2*size + size

FPS = 12  # frames per second
clock = pygame.time.Clock()

# create game window
screen = pygame.display.set_mode((res, res))

# controls how often the snake moves (higher = slower)
snake_frame_speed = 5
frame_counter = 0  # counts frames

score = 0  # player score

# starting position of the snake (center of screen)
snake_start_pos = res // 2 - half_size

length = 4  # initial snake length

# initial movement direction (down)
DirX, DirY = 0, size

# snake body (list of coordinates)
snake = [(snake_start_pos, snake_start_pos)]

# initial apple position
apple = (
    random.randrange(0, res - size, size),
    random.randrange(0, res - size, size)
)


# function to generate a new apple
def apple_gen():
    global apple, score, length
    while True:
        # generate random position
        apple = (
            random.randrange(0, res - size, size),
            random.randrange(0, res - size, size)
        )
        # make sure apple does not spawn inside the snake
        if apple not in snake:
            break

    score += 1   # increase score
    length += 1  # increase snake length


# main game loop
while True:
    # update window title with score
    pygame.display.set_caption(f"Snake - Score: {score}")
    
    # handle events (like closing the window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # clear screen (black background)
    screen.fill((0, 0, 0))
    
    # draw snake (each segment is a square)
    [pygame.draw.rect(screen, (0, 160, 0), (x, y, size, size)) for x, y in snake]

    # draw apple (circle)
    pygame.draw.circle(
        screen,
        (160, 0, 0),
        (apple[0] + half_size, apple[1] + half_size),
        half_size
    )

    # move snake every few frames (based on snake_frame_speed)
    if frame_counter % snake_frame_speed == 0:
        # calculate new head position
        newX = snake[-1][0] + DirX
        newY = snake[-1][1] + DirY

        # add new head to the snake
        snake.append((newX, newY))

        # trim snake to maintain its length
        snake = snake[-length-1:]

    # check if snake eats the apple
    if apple[0] == snake[-1][0] and apple[1] == snake[-1][1]:
        apple_gen()
    
    # handle keyboard input
    key = pygame.key.get_pressed()

    # W - move up (prevent reversing direction)
    if key[pygame.K_w] and DirY != size:
        DirX, DirY = 0, -size

    # S - move down
    elif key[pygame.K_s] and DirY != -size:
        DirX, DirY = 0, size

    # A - move left
    elif key[pygame.K_a] and DirX != size:
        DirX, DirY = -size, 0

    # D - move right
    elif key[pygame.K_d] and DirX != -size:
        DirX, DirY = size, 0

    # check for collision:
    # - hitting walls
    # - hitting itself
    if (
        snake[-1][0] <= -size or
        snake[-1][0] >= res or
        snake[-1][1] <= -size or
        snake[-1][1] >= res or
        snake[-1] in snake[:-1]
    ):
        print("Game Over! Your score was:", score)
        quit()

    # control game speed
    clock.tick(FPS)

    # update display
    pygame.display.flip()