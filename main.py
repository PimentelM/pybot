from dataclasses import astuple

import numpy as np
import win32gui
from window import Window
import time
import cv2
import asyncio

async def main():
    hwnd = win32gui.FindWindow(None,"Super Animal Royale")
    game = Window(hwnd)


    while True:
        pt = game.findImage('./Images/Play.png')
        print(f"Play: {pt}")
        image = game.getScreenCapture()
        radius = 10
        color = [250,0,0]
        # draw our random circle on the canvas
        cv2.circle(image, astuple(pt), radius, color, -1)

        cv2.imshow('output', image)
        cv2.waitKey(50)
        time.sleep(0.001)




asyncio.run(main())




