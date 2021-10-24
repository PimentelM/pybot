import time
from dataclasses import astuple
from typing import Optional, Tuple

import cv2
import win32gui, win32ui, win32api
from win32con import *
import numpy as np

from datastructures import Point
from utils import MakeLeftClick


class Window:
    hwnd: int

    def __init__(self, hwnd):
        if hwnd is None or hwnd == 0:
            raise Exception(f"Window handle '{hwnd}' is invalid")
        self.emtpyDc = None
        self.hwnd = hwnd
        self.cache = {}
        self.windowState = None

    def clickOnImage(self,imagePath: str, confidence=0.9) -> bool:
        self.EnterRenderMode()
        positionOnClient, positionOnScreen = self.findImage(imagePath, confidence)

        if positionOnClient is None:
            return False

        lparam = win32api.MAKELONG(*astuple(positionOnClient))

        mousePosition = win32gui.GetCursorPos()

        win32api.SetCursorPos(positionOnScreen.asTuple())

        win32api.SendMessage(self.hwnd, WM_MOUSEMOVE, 0, lparam)

        win32api.SendMessage(self.hwnd, WM_LBUTTONDOWN, 0, lparam)

        win32api.SendMessage(self.hwnd, WM_MOUSEMOVE, 0, lparam)

        time.sleep(.1)

        win32api.SendMessage(self.hwnd, WM_LBUTTONUP, 0, lparam)

        win32api.SetCursorPos(mousePosition)

        self.ExitRenderMode()

        return True


    def getScreenCapture(self, captureMinimized=False) -> Tuple[any,Optional[Point]]:
        isMinimized = win32gui.IsIconic(self.hwnd)
        specialCapture = isMinimized and captureMinimized

        if isMinimized and not captureMinimized:
            return None, None

        ####### Restore Window and Make It Invisible ########
        if specialCapture:
            self.EnterRenderMode()
        #####################################################

        # Get some data about the window and client area
        left, top, right, bot = win32gui.GetWindowRect(self.hwnd)
        windowWidth = right - left
        windowHeight = bot - top
        windowTop = top
        windowLeft = left

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
            self.ExitRenderMode()
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

        clientPosition = Point(windowLeft + difX, windowTop + difY)

        return image, clientPosition

    def findImage(self, imagePath: str, confidence) -> Tuple[Optional[Point], Optional[Point]]:
        template = self.cache.get(imagePath)
        if template is None:
            template = cv2.imread(imagePath)
            self.cache[imagePath] = template

        image, clientPosition = self.getScreenCapture()

        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val < confidence:
            return None, None

        positionOnClient = Point(*max_loc)
        positionOnScreen = clientPosition + positionOnClient

        return positionOnClient, positionOnScreen

    def EnterRenderMode(self):
        if win32gui.IsIconic(self.hwnd):
            self.windowState = win32api.GetWindowLong(self.hwnd, GWL_EXSTYLE)
            win32api.SetWindowLong(self.hwnd, GWL_EXSTYLE, self.windowState | WS_EX_LAYERED)
            win32gui.SetLayeredWindowAttributes(self.hwnd, 0, 1, LWA_ALPHA)
            win32gui.ShowWindow(self.hwnd, SW_RESTORE)
            win32api.SendMessage(self.hwnd, WM_PAINT, 0, 0)

    def ExitRenderMode(self):
        if self.windowState is not None:
            win32gui.ShowWindow(self.hwnd, SW_MINIMIZE)
            win32api.SetWindowLong(self.hwnd, GWL_EXSTYLE, self.windowState)
            self.windowState = None