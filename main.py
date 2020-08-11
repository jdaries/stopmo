from picamera import PiCamera
from time import sleep
from gpiozero import Button
from PIL import Image

img = Image.open('/home/pi/Documents/stopmo_files/image.jpg')

button = Button(17)
camera = PiCamera()

# Create an image padded to the required size with
# mode 'RGB'
pad = Image.new('RGB', (
    ((img.size[0] + 31) // 32) * 32,
    ((img.size[1] + 15) // 16) * 16,
    ))
# Paste the original image into the padded one
pad.paste(img, (0, 0))


#camera.rotation = 180
camera.start_preview()
o = camera.add_overlay(pad.tobytes(), size=img.size)
o.alpha = 128
o.layer = 3
button.wait_for_press()
camera.capture('/home/pi/Documents/stopmo_files/image2.jpg')
camera.stop_preview()
