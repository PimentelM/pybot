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
        print(game.clickOnImage("./Images/Play.png"))

        break

    game.ExitRenderMode()



asyncio.run(main())




