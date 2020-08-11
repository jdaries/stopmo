from picamera import PiCamera
from time import sleep
from gpiozero import Button
from PIL import Image

IMG_DIR = "/home/pi/Documents/stopmo_files"
PROJECT = "testing"

button = Button(17)



def load_overlay(cur_frame):
    '''cur_frame: int, number of frame about to be taken
    '''
    img = Image.open('{}/{}/frame_{}.jpg'.format(IMG_DIR, PROJECT, str(cur_frame-1)))
    pad = Image.new('RGB', (
        ((img.size[0] + 31) // 32) * 32,
        ((img.size[1] + 15) // 16) * 16,
        ))
    pad.paste(img, (0, 0))
    return img, pad


camera = PiCamera()
camera.start_preview()
frame = 1
while True:
    if frame > 2:
        camera.remove_overlay(o)
    if frame > 1:
        camera = PiCamera()
        camera.start_preview()
        overlay_img, overlay_pad = load_overlay(frame)
        o = camera.add_overlay(overlay_pad.tobytes(), size=overlay_img.size)
        o.alpha = 128
        o.layer = 3
    try:
        button.wait_for_press()
        camera.capture('{}/{}/frame_{}.jpg'.format(IMG_DIR, PROJECT, str(frame)))
        frame += 1
    except KeyboardInterrupt:
        camera.stop_preview()
        break
