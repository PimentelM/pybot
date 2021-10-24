from dataclasses import astuple

import numpy as np
import win32api
import win32gui
from window import Window
import time
import cv2
import asyncio

async def main():
    hwnd = win32gui.FindWindow(None,"Super Animal Royale")
    game = Window(hwnd)


    while True:
        iconPt, parentPt = game.findImage('./Images/Play.png')
        print(f"Play: {iconPt}")
        image, _ = game.getScreenCapture()
        radius = 10
        color = [250,0,0]
        # draw our random circle on the canvas
        if iconPt:
            cv2.circle(image, astuple(iconPt), radius, color, -1)
            #win32api.SetCursorPos(astuple(iconPt + parentPt))

        cv2.imshow('output', image)
        cv2.waitKey(50)
        time.sleep(0.001)




asyncio.run(main())




