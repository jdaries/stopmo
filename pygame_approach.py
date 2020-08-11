#!/usr/bin/python3

import pygame

from pygame.locals import *
from gpiozero import Button
from picamera import PiCamera


IMG_DIR = "/home/pi/Documents/stopmo_files"
PROJECT = "testing"
button = Button(17)


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
    if frame > 1:
        CAMERA.stop_preview()
        frame_display_ghost(WIDTH, HEIGHT, frame)

    CAMERA.start_preview(fullscreen=False, window = (W-WIDTH, 100, WIDTH, HEIGHT))
    button.wait_for_press()
    CAMERA.capture('{}/{}/frame_{}.jpg'.format(IMG_DIR, PROJECT, str(frame)))
    frame += 1
