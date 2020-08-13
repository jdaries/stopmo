#!/usr/bin/python3

import pygame

from pygame.locals import *
from gpiozero import Button
from picamera import PiCamera


IMG_DIR = "/home/pi/Documents/stopmo_files"
PROJECT = "testing"


# 2 = delete movie
# 3 = preview movie
# 4 = delete a frame
# 17 - take a picture
# 27 - save movie
# 22 - exit program

delete_movie_button = Button(2)
preview_movie_button = Button(3)
delete_frame_button = Button(4)
take_picture_button = Button(17)
save_movie_button = Button(27)
exit_program_button = Button(22)


def frame_display_ghost(W, H, frame_no):
    last_image = frame_get_last(W, H, frame_no)
    SCREEN.blit(last_image, (0, 0))
    pygame.display.update()


def frame_get_last(W, H, frame_no):
    if frame_no > 1:
        image = pygame.image.load('{}/{}/frame_{}.jpg'.format(IMG_DIR, PROJECT, str(frame_no-1)))
        image = pygame.transform.scale(image, (W, H))
    else:
        image = pygame.Surface((W, H))
        image.fill([0, 0, 0])
    return image


pygame.init()
W, H = pygame.display.list_modes()[0]
WIDTH = int(W)
HEIGHT = int(H)
print('Resolution: ({WIDTH}, {HEIGHT}).'.format(WIDTH=WIDTH, HEIGHT=HEIGHT))
SCREEN = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.mouse.set_visible = False
pygame.display.toggle_fullscreen()
CAMERA = PiCamera()
CAMERA.preview_alpha = 200
CAMERA.resolution = (WIDTH, HEIGHT)

frame = 1


def take_picture():
    global frame
    CAMERA.capture('{}/{}/frame_{}.jpg'.format(IMG_DIR, PROJECT, str(frame)))
    frame += 1


def exit_app():
    exit()


while True:
    CAMERA.start_preview()

    take_picture_button.when_pressed = take_picture
    exit_program_button.when_pressed = exit_app

    if frame > 1:
        CAMERA.stop_preview()
        frame_display_ghost(WIDTH, HEIGHT, frame)
