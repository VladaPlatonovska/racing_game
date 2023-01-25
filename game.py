import pygame
import math
import random
from vector import Vector


def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)


def blit_rotate_center(surface, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    surface.blit(rotated_image, new_rect.topleft)


def blit_text_center(win, font, text):
    render = font.render(text, 1, (200, 200, 200))
    win.blit(render, (win.get_width() / 2 - render.get_width() /
                      2, win.get_height() / 2 - render.get_height() / 2))


pygame.font.init()

GRASS = scale_image(pygame.image.load("Images/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("Images/track.png"), 0.9)

TRACK_BORDER = scale_image(pygame.image.load("Images/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
RED_CAR = scale_image(pygame.image.load("Images/red-car.png"), 0.4)
FINISH = scale_image(pygame.image.load("Images/finish.png"), 1)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (140, 250)
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

MAIN_FONT = pygame.font.SysFont("comicsans", 44)

FPS = 60


class GameInform:
    LEVELS = 2

    def __init__(self, level=1):
        self.level = level
        self.started = False

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True


class Obstacle:

    def __init__(self, vector: Vector):
        self.x = vector.x
        self.y = vector.y
        self.position = vector
        self.radius = 10

    def draw(self):
        pygame.draw.circle(WIN, (0, 0, 0), (self.x, self.y), 15)


class Car:
    IMG = RED_CAR
    START_POS = (180, 200)

    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.01

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def collision(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        intersection = mask.overlap(car_mask, offset)
        return intersection

    def collision_with_obstacle(self, obstacle: Obstacle):
        car_vector = Vector(self.x, self.y)
        distance = (car_vector - obstacle.position).magnitude()
        return distance < 10

    def rebound(self):
        self.vel = -self.vel
        self.move()

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0


run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION)]
player_car = Car(4, 4)
game_info = GameInform()
obstacles = []


def generate_obstacles(number_of_obstacles):
    for i in range(0, number_of_obstacles):
        x = random.randrange(15, 885)
        y = random.randrange(15, 885)
        vector = Vector(x, y)
        obstacle = Obstacle(vector)
        obstacles.append(obstacle)


def draw(win, images, player_car):
    for img, pos in images:
        win.blit(img, pos)
    for obstacle in obstacles:
        obstacle.draw()

    level_text = MAIN_FONT.render(
        f"Level {game_info.level}", 1, (255, 255, 255))
    win.blit(level_text, (10, HEIGHT - level_text.get_height() - 70))

    vel_text = MAIN_FONT.render(
        f"Vel: {round(player_car.vel, 1)}px/s", 1, (255, 255, 255))
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 10))
    player_car.draw(win)
    pygame.display.update()


generate_obstacles(15)
while run:
    clock.tick(FPS)

    draw(WIN, images, player_car)

    while not game_info.started:
        blit_text_center(
            WIN, MAIN_FONT, f"Press any key to start level {game_info.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game_info.start_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_LEFT]:
        player_car.rotate(left=True)
    if keys[pygame.K_RIGHT]:
        player_car.rotate(right=True)
    if keys[pygame.K_UP]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_DOWN]:
        moved = True
        player_car.move_backward()

    if not moved:
        player_car.reduce_speed()

    if player_car.collision(TRACK_BORDER_MASK) is not None:
        player_car.rebound()

    for obstacle in obstacles:
        if player_car.collision_with_obstacle(obstacle):
            blit_text_center(WIN, MAIN_FONT, "You LOST the game!")
            pygame.display.update()
            pygame.time.wait(5000)
            game_info.reset()
            player_car.reset()

    if player_car.collision(FINISH_MASK, *FINISH_POSITION) is not None:
        if player_car.collision(FINISH_MASK, *FINISH_POSITION)[1] == 0:
            player_car.rebound()
        else:
            player_car.reset()
            game_info.level += 1
            obstacles.clear()
            generate_obstacles(15)
            if game_info.level == 2:
                blit_text_center(WIN, MAIN_FONT, "Next level!")
            pygame.display.update()
            pygame.time.wait(700)

    if game_info.game_finished():
        blit_text_center(WIN, MAIN_FONT, "You WON the game!")
        pygame.display.update()
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()

pygame.quit()
