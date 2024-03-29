#!/usr/bin/env python3
import glob
import os
import sys
import subprocess
import argparse

import ffmpeg
import keyboard
from picamera import PiCamera
from PIL import Image, ImageDraw, ImageFont

HOME_DIR = "/home/pi/Documents/stopmo_files"
PAD_WIDTH = 4
FONT_DIR = "/usr/share/fonts/truetype/freefont"


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
    pad = Image.new('RGBA', _pad(camera.resolution))
    pad.paste(overlay_img)

    txt = Image.new("RGBA", pad.size, (255, 255, 255, 0))

    font = ImageFont.truetype(os.path.join(FONT_DIR, "FreeSans.ttf"), 120)

    d = ImageDraw.Draw(txt)
    frame_no = count_frames(PROJECT)
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
    if count_frames(PROJECT) == 0:
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
    frames = glob.glob(os.path.join(frames_dir, "frame_*.jpg"))
    if len(frames) == 0:
        frame_no = str(1).zfill(PAD_WIDTH)
    else:
        sequence = [int(os.path.basename(x).split(".")[0].split("_")[-1])
                    for x
                    in frames]
        frame_no = str(max(sequence)+offset).zfill(PAD_WIDTH)
    return os.path.join(frames_dir, 'frame_{}.jpg').format(frame_no)


def assemble_and_preview():
    if debug_mode:
        print("assemble_and_preview button pushed")
        return
    stop()
    frame_count_file = os.path.join(movie_dir, "preview_frame.txt")
    output_fname = os.path.join(movie_dir,
                                '{proj}_preview.mp4').format(proj=PROJECT)
    frame_range = os.path.join(frames_dir,
                               'frame_%0{}d.jpg').format(PAD_WIDTH)
    if not os.path.exists(output_fname):
        append_flag = False
        video_in = ffmpeg.input(frame_range,
                                pattern_type='sequence',
                                framerate=FRAME_RATE)
        video_out = ffmpeg.output(video_in, output_fname)
        with open(frame_count_file, "w") as f_out:
            f_out.write(count_frames(PROJECT))
    else:
        append_flag = True
        old_preview_fname = os.path.join(movie_dir, "old_preview.mp4")
        os.rename(output_fname, old_preview_fname)
        with open(frame_count_file, "r") as f_in:
            prev_count = int(f_in.readlines()[0].strip())
        new_video_in = ffmpeg.input(frame_range,
                                    pattern_type='sequence',
                                    start_number=prev_count + 1,
                                    framerate=FRAME_RATE)
        existing_preview = ffmpeg.input(old_preview_fname)
        new_preview_stream = ffmpeg.concat(existing_preview, new_video_in)
        video_out = ffmpeg.output(new_preview_stream, output_fname)
        with open(frame_count_file, "w") as f_out:
            f_out.write(count_frames(PROJECT))
    video_out.run(overwrite_output=True)
    subprocess.call(['xdg-open', output_fname])
    return


def clear_project():
    if debug_mode:
        print("asked to remove files associated with {}".format(PROJECT))
        return
    frames = glob.glob(os.path.join(frames_dir, "*.jpg"))
    previews = glob.glob(os.path.join(movie_dir, "*_preview.mp4"))
    for frame in frames:
        os.remove(frame)
    for preview in previews:
        os.remove(preview)


def count_frames(proj):
    tmp_frame_dir = os.path.join(HOME_DIR, proj, "frames")
    frames = glob.glob(os.path.join(tmp_frame_dir, "frame_*.jpg"))
    if len(frames) == 0:
        return str(1).zfill(PAD_WIDTH)
    sequence = [int(os.path.basename(x).split(".")[0].split("_")[-1])
                for x
                in frames]
    frame_no = str(max(sequence)).zfill(PAD_WIDTH)
    return frame_no


def list_projects():
    projects = glob.glob(os.path.join(HOME_DIR, "*"))
    project_names = [os.path.basename(x) for x in projects]
    frame_counts = [count_frames(x) for x in projects]
    projs_w_frames = zip(project_names, frame_counts)
    for x, y in projs_w_frames:
        print("Project:{}; Frames:{}".format(x, y))
    return


def frame_directory(proj):
    return os.path.join(HOME_DIR, proj, "frames")


def movie_directory(proj):
    return os.path.join(HOME_DIR, proj, "movies")


def main():
    print("ok ready")
    keyboard.add_hotkey('esc', stop)
    keyboard.add_hotkey('return', preview)
    keyboard.add_hotkey('delete', deleteframe_button)
    keyboard.add_hotkey('space',take_picture)
    keyboard.add_hotkey('p', assemble_and_preview)
    keyboard.add_hotkey('q', exit_button)
    keyboard.wait()


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
    parser.add_argument('--frame_rate', '-f',
                        type=int, default=12,
                        help="specify frame rate for animations")
    args = parser.parse_args()
    debug_mode = args.debug_mode
    PROJECT = args.project_name
    clear_flag = args.clear_files
    list_flag = args.list_projects
    FRAME_RATE = args.frame_rate

    frames_dir = frame_directory(PROJECT)
    movie_dir = movie_directory(PROJECT)

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
