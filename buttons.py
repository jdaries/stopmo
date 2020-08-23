#!/usr/bin/python3

from gpiozero import Button

# 2 = delete movie
# 3 = preview movie
# 4 = delete a frame
# 17 - take a picture
# 27 - save movie
# 22 - exit program

delete_movie_button = Button(2)
preview_movie_button = Button(3)
delete_frame_button = Button(4)
take_picture_button = Button(17)
save_movie_button = Button(27)
exit_program_button = Button(22)


def echo(stmt):
    print(stmt)


def delete_button():
    echo("delete movie button pressed")


def preview_button():
    echo("preview button pressed")


def deleteframe_button():
    echo("delete frame button pressed")


def takepic_button():
    echo("take picture button pressed")


def save_button():
    echo("save picure button pressed")


def exit_button():
    exit()


while True:
    delete_movie_button.when_pressed = delete_button
    preview_movie_button.when_pressed = preview_button
    delete_frame_button.when_pressed = deleteframe_button
    take_picture_button.when_pressed = takepic_button
    save_movie_button.when_pressed = save_button
    exit_program_button.when_pressed = exit_button
