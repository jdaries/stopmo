#!/usr/bin/python3
import pygame
import glob
import os
import sys
import subprocess

# from pygame.locals import *
import ffmpeg
from gpiozero import Button
from picamera import PiCamera
from PIL import Image

HOME_DIR = "/home/pi/Documents/stopmo_files"
PROJECT = sys.argv[1]
PAD_WIDTH = 2

stop_preview_button = Button(2)
preview_button = Button(3)
delete_frame_button = Button(4)
take_picture_button = Button(17)
preview_film_button = Button(27)
exit_program_button = Button(22)


# pygame.init()
# W, H = pygame.display.list_modes()[0]
# WIDTH = (int(W*.9) // 32) * 32
# HEIGHT = (int(H*.9) // 32) * 32
# X_OFFSET = W - WIDTH // 2
# Y_OFFSET = H - HEIGHT // 2
# print('Resolution: ({WIDTH}, {HEIGHT}).'.format(WIDTH=WIDTH, HEIGHT=HEIGHT))
# SCREEN = pygame.display.set_mode([WIDTH, HEIGHT])
# pygame.mouse.set_visible = False
# pygame.display.toggle_fullscreen()
CAMERA = PiCamera(sensor_mode=2)
# CAMERA.preview_alpha = 128
# CAMERA.resolution = (WIDTH, HEIGHT)


def _pad(resolution, width=32, height=16):
    # Pads the specified resolution
    # up to the nearest multiple of *width* and *height*; this is
    # needed because overlays require padding to the camera's
    # block size (32x16)
    return (
        ((resolution[0] + (width - 1)) // width) * width,
        ((resolution[1] + (height - 1)) // height) * height,
    )


def remove_overlays(camera):

    # Remove all overlays from the camera preview
    for o in camera.overlays:
        camera.remove_overlay(o)


def preview_overlay(camera=None):
    # Remove all overlays
    remove_overlays(camera)

    # Get an Image object of the chosen overlay
    overlay_img = Image.open(get_next_frame(offset=0))

    # Pad it to the right resolution
    pad = Image.new('RGB', _pad(camera.resolution))
    pad.paste(overlay_img)

    # Add the overlay
    camera.add_overlay(pad.tobytes(), alpha=128, layer=3)


def echo(stmt):
    print(stmt)


def stop():
    print("stop preview button pressed")
    remove_overlays(CAMERA)
    CAMERA.stop_preview()


def preview():
    print("preview button pressed")
    CAMERA.start_preview()
    frame_base_str = '{}/{}/frames/frame_{}.jpg'
    if get_next_frame(offset=0) == frame_base_str.format(HOME_DIR,
                                                         PROJECT,
                                                         str(0).zfill(
                                                                      PAD_WIDTH
                                                                      )
                                                         ):
        return
    else:
        ghost_preview()


def deleteframe_button():
    echo("delete frame button pressed")
    os.remove(get_next_frame(offset=0))


def take_picture():
    print("take picture button pressed")
    frame_fname = get_next_frame()
    CAMERA.capture(frame_fname)
    ghost_preview()


def ghost_preview():
    print("ghost button pressed")
    preview_overlay(CAMERA)


def exit_button():
    exit()


def get_next_frame(offset=1):
    frames = glob.glob("{}/{}/frames/frame_*.jpg".format(HOME_DIR, PROJECT))
    if len(frames) == 0:
        return '{}/{}/frames/frame_{}.jpg'.format(HOME_DIR, PROJECT,
                                                  str(1).zfill(PAD_WIDTH))
    sequence = [int(os.path.basename(x).split(".")[0].split("_")[-1])
                for x
                in frames]
    return '{}/{}/frames/frame_{}.jpg'.format(HOME_DIR, PROJECT,
                                              str(
                                                  max(sequence)+offset
                                                  ).zfill(PAD_WIDTH))


def assemble_and_preview():
    stop()
    output_fname = '{hdir}/{proj}/movie/{proj}.mp4'.format(hdir=HOME_DIR,
                                                            proj=PROJECT)
    video_in = ffmpeg.input('{}/{}/frame_*.jpg'.format(HOME_DIR, PROJECT),
                            pattern_type='glob',
                            framerate=12)
    video_out = ffmpeg.output(video_in, output_fname)
    video_out.run()
    subprocess.call(['xdg-open', output_fname])


def main():
    while True:
        stop_preview_button.when_pressed = stop
        preview_button.when_pressed = preview
        delete_frame_button.when_pressed = deleteframe_button
        take_picture_button.when_pressed = take_picture
        preview_film_button.when_pressed = assemble_and_preview
        exit_program_button.when_pressed = exit_button


if __name__ == '__main__':
    if not os.path.exists("{}/{}/frames".format(HOME_DIR, PROJECT)):
        os.makedirs("{}/{}/frames".format(HOME_DIR, PROJECT))
        os.mkdir("{}/{}/movie".format(HOME_DIR, PROJECT))
    main()
