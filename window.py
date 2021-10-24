from typing import Optional

import cv2
import win32gui, win32ui, win32api
from win32con import *
import numpy as np

from datastructures import Point


class Window:
    hwnd: int

    def __init__(self, hwnd):
        self.emtpyDc = None
        self.hwnd = hwnd
        self.cache = {}

    def getScreenCapture(self, captureMinimized=False):
        result = None
        isMinimized = win32gui.IsIconic(self.hwnd)
        specialCapture = isMinimized and captureMinimized
        windowState = win32api.GetWindowLong(self.hwnd, GWL_EXSTYLE)

        if isMinimized and not captureMinimized:
            return None

        ####### Restore Window and Make It Invisible ########
        if specialCapture:
            win32api.SetWindowLong(self.hwnd, GWL_EXSTYLE, windowState | WS_EX_LAYERED)
            win32gui.SetLayeredWindowAttributes(self.hwnd, 0, 1, LWA_ALPHA)
            win32gui.ShowWindow(self.hwnd, SW_RESTORE)
            win32api.SendMessage(self.hwnd, WM_PAINT, 0, 0)
        #####################################################

        # Get some data about the window and client area
        left, top, right, bot = win32gui.GetWindowRect(self.hwnd)
        windowWidth = right - left
        windowHeight = bot - top

        left, top, right, bot = win32gui.GetClientRect(self.hwnd)
        clientWidth = right - left
        clientHeight = bot - top

        difX = windowWidth - clientWidth - 8
        difY = windowHeight - clientHeight - 8

        # Get the screen capture data

        hWindowDC = win32gui.GetWindowDC(self.hwnd)
        windowDC = win32ui.CreateDCFromHandle(hWindowDC)
        emptyDC = windowDC.CreateCompatibleDC()
        bitmapObject = win32ui.CreateBitmap()
        bitmapObject.CreateCompatibleBitmap(windowDC, clientWidth, clientHeight)
        emptyDC.SelectObject(bitmapObject)

        emptyDC.BitBlt((0, 0), (clientWidth, clientHeight), windowDC, (difX, difY), SRCCOPY)

        ####### Minimize Window and Make It Visible #########
        if specialCapture:
            win32gui.ShowWindow(self.hwnd, SW_MINIMIZE)
            win32api.SetWindowLong(self.hwnd, GWL_EXSTYLE, windowState)
        #####################################################

        # Saves debug file
        # bitmapObject.SaveBitmapFile(emptyDC, "./test.png")

        # Get some info about the bitmap
        bmpinfo = bitmapObject.GetInfo()
        bitmapWidth, bitmapHeight = bmpinfo['bmWidth'], bmpinfo['bmHeight']

        # Convert image into a format that is readable by cv2
        imageArray = bitmapObject.GetBitmapBits(True)
        image = np.fromstring(imageArray, dtype='uint8')
        image.shape = (bitmapHeight, bitmapWidth, 4)

        # Clear resources
        emptyDC.DeleteDC()
        windowDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, hWindowDC)
        win32gui.DeleteObject(bitmapObject.GetHandle())

        # Remove Alpha Channel
        image = image[..., :3]

        # Make it C_CONTIGUOUS
        image = np.ascontiguousarray(image)

        return image

    # TODO: How to interpret result from match template
    def findImage(self, imagePath: str, confidence=0.9) -> Optional[Point]:
        template = self.cache.get(imagePath)
        if template is None:
            template = cv2.imread(imagePath)
            self.cache[imagePath] = template

        screen = self.getScreenCapture()
        image = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)

        cv2.imshow("result", result)
        cv2.waitKey(1)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        print(f"Min: {min_val}, Max: {max_val}. Best Loc: {max_loc}")

        if max_val < confidence:
            return None

        return Point(*max_loc)
