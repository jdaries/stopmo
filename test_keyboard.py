#!/usr/bin/env python


import keyboard

def spaced():
    print("space was pressed")

keyboard.add_hotkey('space', spaced)
keyboard.wait()
