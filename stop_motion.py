#!/usr/bin/python3
import glob
import os
import sys
import subprocess
import argparse

import ffmpeg
from gpiozero import Button
from picamera import PiCamera
from PIL import Image

HOME_DIR = "/home/pi/Documents/stopmo_files"
PAD_WIDTH = 4

stop_preview_button = Button(2)
preview_button = Button(3)
delete_frame_button = Button(4)
take_picture_button = Button(17)
preview_film_button = Button(27)
exit_program_button = Button(22)


CAMERA = PiCamera(sensor_mode=2)


def _pad(resolution, width=32, height=16):
    # Pads the specified resolution
    # up to the nearest multiple of *width* and *height*; this is
    # needed because overlays require padding to the camera's
    # block size (32x16)
    if debug_mode:
        print("_pad function called")
    return (
        ((resolution[0] + (width - 1)) // width) * width,
        ((resolution[1] + (height - 1)) // height) * height,
    )


def remove_overlays(camera):
    # Remove all overlays from the camera preview
    if debug_mode:
        print("remove_overlays function called")
    for o in camera.overlays:
        camera.remove_overlay(o)


def preview_overlay(camera=None):
    # Remove all overlays
    if debug_mode:
        print("preview_overlay function called")
    remove_overlays(camera)

    # Get an Image object of the chosen overlay
    overlay_img = Image.open(get_next_frame(offset=0))

    # Pad it to the right resolution
    pad = Image.new('RGB', _pad(camera.resolution))
    pad.paste(overlay_img)

    # Add the overlay
    camera.add_overlay(pad.tobytes(), alpha=128, layer=3)


def stop():
    if debug_mode:
        print("stop preview button pressed")
        return
    remove_overlays(CAMERA)
    CAMERA.stop_preview()


def preview():
    if debug_mode:
        print("preview button pressed")
        return
    CAMERA.start_preview()
    frame_base_str = '{}/frame_{}.jpg'
    if get_next_frame(offset=0) == frame_base_str.format(frames_dir,
                                                         str(0).zfill(
                                                                      PAD_WIDTH
                                                                      )
                                                         ):
        return
    else:
        ghost_preview()


def deleteframe_button():
    if debug_mode:
        print("delete frame button pressed")
        return
    os.remove(get_next_frame(offset=0))


def take_picture():
    if debug_mode:
        print("take picture button pressed")
        return
    frame_fname = get_next_frame()
    CAMERA.capture(frame_fname)
    ghost_preview()


def ghost_preview():
    if debug_mode:
        print("ghost_preview function called")
    preview_overlay(CAMERA)


def exit_button():
    if debug_mode:
        print("exit button pushed")
    exit()


def get_next_frame(offset=1):
    if debug_mode:
        print("get_next_frame function called")
    frames = glob.glob("{}/frame_*.jpg".format(frames_dir))
    if len(frames) == 0:
        return '{}/frame_{}.jpg'.format(frames_dir,
                                        str(1).zfill(PAD_WIDTH))
    sequence = [int(os.path.basename(x).split(".")[0].split("_")[-1])
                for x
                in frames]
    return '{}/frame_{}.jpg'.format(frames_dir,
                                    str(
                                        max(sequence)+offset
                                        ).zfill(PAD_WIDTH))


def assemble_and_preview():
    if debug_mode:
        print("assemble_and_preview button pushed")
        return
    stop()
    output_fname = '{m_dir}/{proj}_preview.mp4'.format(m_dir=movie_dir,
                                                       proj=PROJECT)
    os.remove(output_fname)
    video_in = ffmpeg.input('{}/frame_*.jpg'.format(frames_dir),
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
    parser = argparse.ArgumentParser(description="Stop Motion Pi")
    parser.add_argument('project_name',
                        type=str,
                        help="name for project, no spaces, used for directory")
    parser.add_argument('--debug_mode', '-d',
                        action='store_true',
                        help="debug functions by just printing" +
                             "what is to be done to standard output")
    args = parser.parse_args()
    debug_mode = args.debug_mode
    PROJECT = args.project_name

    frames_dir = "{}/{}/frames".format(HOME_DIR, PROJECT)
    movie_dir = "{}/{}/movie".format(HOME_DIR, PROJECT)

    if not os.path.exists(frames_dir):
        if debug_mode:
            print("creating 'frames' directory at {}".format(frames_dir))
        os.makedirs(frames_dir)
    if not os.path.exists(movie_dir):
        if debug_mode:
            print("creating 'movie' directory at {}".format(movie_dir))
        os.makedirs(movie_dir)
    main()
