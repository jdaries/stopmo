#!/usr/bin/python3

import pygame

from pygame.locals import *
from gpiozero import Button
from picamera import PiCamera


IMG_DIR = "/home/pi/Documents/stopmo_files"
PROJECT = "testing"

BUTTON_NUMBERS = [2, 3, 4, 17, 27, 22]

# 2 = delete movie
# 3 = preview movie
# 4 = delete a frame
# 17 - take a picture
# 27 - save movie
# 22 - exit program

delete_movie_button = 2
preview_movie_button = 3
delete_frame_button = 4
take_picture_button = 17
save_movie_button = 27
exit_program_button = 22


BUTTONS = {
    bnum: Button(bnum)
    for bnum in BUTTON_NUMBERS
}


def get_pressed_buttons():
    return set([bnum for bnum in BUTTONS if BUTTONS[bnum].is_pressed])


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

while True:

    pressed = get_pressed_buttons()
    if pressed == set(delete_movie_button):
        delete_and_quit = True
    elif pressed == set(preview_movie_button):
        show_preview = True
    elif pressed == set(delete_frame_button):
        erase_last_frame = True
    elif pressed == set(take_picture_button):
        take_picture = True
    elif pressed == set(save_movie_button):
        make_and_save_movie = True
    elif pressed == set(exit_program_button):
        exit_app = True

    if frame > 1:
        CAMERA.stop_preview()
        frame_display_ghost(WIDTH, HEIGHT, frame)

    CAMERA.start_preview()

    if take_picture:
        CAMERA.capture('{}/{}/frame_{}.jpg'.format(IMG_DIR, PROJECT, str(frame)))
        frame += 1
    elif exit_app:
        CAMERA.stop_preview()
        break
