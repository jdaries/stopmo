#!/usr/bin/python3
import glob
import os
import sys
import subprocess
import argparse

import ffmpeg
from gpiozero import Button
from picamera import PiCamera
from PIL import Image, ImageDraw, ImageFont

HOME_DIR = "/home/pi/Documents/stopmo_files"
PAD_WIDTH = 4
FONT_DIR = "/usr/share/fonts"

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

    overlay_img = Image.open(get_next_frame(offset=0))
    pad = Image.new('RGB', _pad(camera.resolution))
    pad.paste(overlay_img)

    txt = Image.new("RGBA", pad.size, (255, 255, 255, 0))

    font = ImageFont.truetype(os.path.join(FONT_DIR, "arial.ttf"), 120)

    d = ImageDraw.Draw(txt)
    frame_no = count_frames()
    d.text((10, 10), frame_no, fill=(0, 0, 0), font=font)

    out = Image.alpha_composite(pad, txt)
    out = out.convert("RGB")
    # Add the overlay
    camera.add_overlay(out.tobytes(), alpha=128, layer=3)


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
                                                         str(1).zfill(
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
        frame_no = str(1).zfill(PAD_WIDTH)
        return '{}/frame_{}.jpg'.format(frames_dir, frame_no)
    sequence = [int(os.path.basename(x).split(".")[0].split("_")[-1])
                for x
                in frames]
    frame_no = str(max(sequence)+offset).zfill(PAD_WIDTH)
    return '{}/frame_{}.jpg'.format(frames_dir, frame_no)


def assemble_and_preview():
    if debug_mode:
        print("assemble_and_preview button pushed")
        return
    stop()
    output_fname = '{m_dir}/{proj}_preview.mp4'.format(m_dir=movie_dir,
                                                       proj=PROJECT)
    if os.path.exists(output_fname):
        os.remove(output_fname)
    video_in = ffmpeg.input('{}/frame_*.jpg'.format(frames_dir),
                            pattern_type='glob',
                            framerate=12)
    video_out = ffmpeg.output(video_in, output_fname)
    video_out.run()
    subprocess.call(['xdg-open', output_fname])


def clear_project():
    if debug_mode:
        print("asked to remove files associated with {}".format(PROJECT))
        return
    frames = glob.glob("{}/*.jpg".format(frames_dir))
    previews = glob.glob("{}/*_preview.mp4".format(movie_dir))
    for frame in frames:
        os.remove(frame)
    for preview in previews:
        os.remove(preview)


def count_frames():
    frames = glob.glob("{}/frame_*.jpg".format(frames_dir))
    if len(frames) == 0:
        return str(1).zfill(PAD_WIDTH)
    sequence = [int(os.path.basename(x).split(".")[0].split("_")[-1])
                for x
                in frames]
    frame_no = str(max(sequence)).zfill(PAD_WIDTH)
    return frame_no


def list_projects():
    projects = glob.glob("{}/*".format(HOME_DIR))
    frame_counts = [len(glob.glob("{}/{}/frames/frame_*.jpg".format(HOME_DIR, x))) for x in projects]
    projs_w_frames = zip(projects, frame_counts)
    for x, y in projs_w_frames:
        print("Project:{}; Frames:{}".format(x, y))
    return


def main():
    print("ok ready")
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
    parser.add_argument('--clear_files', '-c',
                        action='store_true',
                        help="delete files for specified project")
    parser.add_argument('--list_projects', '-ls',
                        action='store_true',
                        help="list current projects")
    args = parser.parse_args()
    debug_mode = args.debug_mode
    PROJECT = args.project_name
    clear_flag = args.clear_files
    list_flag = args.list_projects

    frames_dir = "{}/{}/frames".format(HOME_DIR, PROJECT)
    movie_dir = "{}/{}/movie".format(HOME_DIR, PROJECT)

    if clear_flag:
        clear_project()
        exit()

    if list_flag:
        list_projects()
        exit()

    if not os.path.exists(frames_dir):
        if debug_mode:
            print("creating 'frames' directory at {}".format(frames_dir))
        os.makedirs(frames_dir)
    if not os.path.exists(movie_dir):
        if debug_mode:
            print("creating 'movie' directory at {}".format(movie_dir))
        os.makedirs(movie_dir)
    main()
