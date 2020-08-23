#!/usr/bin/python3
import pygame

from pygame.locals import *
from gpiozero import Button
from picamera import PiCamera

# 2 = delete movie
# 3 = preview movie
# 4 = delete a frame
# 17 - take a picture
# 27 - save movie
# 22 - exit program

stop_preview_button = Button(2)
preview_button = Button(3)
delete_frame_button = Button(4)
take_picture_button = Button(17)
save_movie_button = Button(27)
exit_program_button = Button(22)


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


def echo(stmt):
    print(stmt)


def stop():
    print("stop preview button pressed")
    CAMERA.stop_preview()


def preview():
    print("preview button pressed")
    CAMERA.start_preview()


def deleteframe_button():
    echo("delete frame button pressed")


def takepic_button():
    echo("take picture button pressed")


def save_button():
    echo("save picure button pressed")


def exit_button():
    exit()


while True:
    stop_preview_button.when_pressed = stop
    preview_movie_button.when_pressed = preview
    delete_frame_button.when_pressed = deleteframe_button
    take_picture_button.when_pressed = takepic_button
    save_movie_button.when_pressed = save_button
    exit_program_button.when_pressed = exit_button
