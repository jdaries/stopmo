from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.rotation = 180
camera.start_preview()
sleep(3)
camera.capture('/home/pi/Documents/stopmo_files/image.jpg')
camera.stop_preview()
