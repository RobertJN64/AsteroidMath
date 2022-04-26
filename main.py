import random
import pygame
from typing import List
import math

#ELLIPSE EQ
# x^2 + y^2 / b = rad ^ 2
# y = sqrt((rad^2 - x^2) * b)

#RENDER MODE
RENDER_MODE = 1 #render only nearby
#RENDER_MODE = 2 #render all
DEBUG_ENABLE = False

def rotate_point(x, y, angle):
    angle = math.radians(angle)
    nx = math.cos(angle) * x - math.sin(angle) * y
    ny = math.sin(angle) * x + math.cos(angle) * y
    return nx, ny

def text_objects(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def message_display(screen, text, pos, color=(255,0,0), size=30):
    largeText = pygame.font.SysFont("Consolas", size)
    TextSurf, TextRect = text_objects(str(text), largeText, color)
    TextRect.center = pos
    screen.blit(TextSurf, TextRect)

def is_close(x1, y1, x2, y2, threshold):
    return (x1 - x2) ** 2 + (y1 - y2) ** 2 < threshold ** 2

def random_range(minv, maxv):
    return random.random() * (maxv - minv) + minv

class Asteroid:
    def __init__(self, orbit_rad, frame_period, x_center, y_center):
        self.orbit_rad = orbit_rad
        self.offset_angle = random_range(0, 360)
        self.frame_period = frame_period
        self.offset_frame = random_range(0, frame_period)

        self.x_center = x_center
        self.y_center = y_center

        self.b = random_range(0.5, 2) #random b value for ellipse eq from 0.5 to 2

    def get_xy(self, frame):
        frame += self.offset_frame
        xpos = math.sin(frame / self.frame_period * math.pi * 2) * self.orbit_rad
        ypos = math.sqrt((self.orbit_rad ** 2 - xpos ** 2) * self.b)
        if self.frame_period/4 < frame % self.frame_period < self.frame_period * 3/4:
            ypos *= -1
        xpos, ypos = rotate_point(xpos, ypos, self.offset_angle)
        return xpos + self.x_center, ypos + self.y_center



all_asteroids: List[Asteroid] = []
active_asteroids: List[Asteroid]  = []

spaceship_x = 150
spaceship_y = 300

close_threshold = 200
render_threshold = 50

n_asteroids = 5000
update_block_size = 125

def hard_recalc(frame):
    active_asteroids.clear()
    for asteroid in all_asteroids:
        x, y = asteroid.get_xy(frame)
        if is_close(spaceship_x, spaceship_y, x, y, close_threshold):
            active_asteroids.append(asteroid)

def recalc_range(minv, maxv, frame):
    for asteroid in all_asteroids[minv:maxv]:
        x, y = asteroid.get_xy(frame)
        if is_close(spaceship_x, spaceship_y, x, y, close_threshold):
            if asteroid not in active_asteroids:
                active_asteroids.append(asteroid)
                if DEBUG_ENABLE and is_close(spaceship_x, spaceship_y, x, y, render_threshold):
                    print("Missed asteroid")
        else:
            if asteroid in active_asteroids:
                active_asteroids.remove(asteroid)



def main():
    pygame.init()
    display = pygame.display.set_mode((600,600))

    # INIT
    for i in range(0, n_asteroids):
        all_asteroids.append(Asteroid(random_range(100, 200), #orbit radius (pixels)
                                      random_range(400, 500), #frame_period (frames)
                                      300, 300)) #x, y center pos


    done = False
    clock = pygame.time.Clock()
    frame = 0
    hard_recalc(frame)
    recalc_pos = 0
    while not done:
        display.fill((200, 200, 200))

        if RENDER_MODE == 1: #NORMAL
            for index in range(len(active_asteroids) - 1, -1, -1):
                asteroid = active_asteroids[index]
                x, y = asteroid.get_xy(frame)
                if is_close(x, y, spaceship_x, spaceship_y, render_threshold):
                    pygame.draw.circle(display, (0,0,0), (x, y), 5)
                if not is_close(x, y, spaceship_x, spaceship_y, close_threshold):
                    active_asteroids.pop(index)

        if RENDER_MODE == 2: #ALL
            for asteroid in all_asteroids:
                x, y = asteroid.get_xy(frame)
                if is_close(x, y, spaceship_x, spaceship_y, render_threshold):
                    if asteroid in active_asteroids:
                        pygame.draw.circle(display, (0,0,0), (x, y), 5)
                    else:
                        pygame.draw.circle(display, (0,100,0), (x,y), 5)

                else:
                    if asteroid in active_asteroids:
                        pygame.draw.circle(display, (100,0,0), (x,y), 5)
                    else:
                        pygame.draw.circle(display, (0,0,100), (x, y), 5)

                if asteroid in active_asteroids and not is_close(x, y, spaceship_x, spaceship_y, close_threshold):
                    active_asteroids.remove(asteroid)

        pygame.draw.circle(display, (200,0,0), (spaceship_x, spaceship_y), 10)
        pygame.draw.circle(display, (100,100,100), (300,300),5)

        message_display(display, 'FPS: ' + str(round(clock.get_fps(),1)), (500, 50),
                        color=(0, 0, 0), size=15)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        clock.tick(60)
        frame += 1

        recalc_range(recalc_pos, recalc_pos + update_block_size, frame)
        recalc_pos += update_block_size
        if recalc_pos > len(all_asteroids):
            recalc_pos = 0


if __name__ == '__main__':
    main()