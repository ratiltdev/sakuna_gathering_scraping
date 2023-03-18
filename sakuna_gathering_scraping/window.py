import win32com.client
import win32con
import win32gui

from PIL import Image, ImageGrab


class Window:
    def __init__(self, hwnd: int) -> None:
        self.__hwnd = hwnd
        self.updateRect()
        return
    
    def updateRect(self) -> None:
        self.__offset = win32gui.GetWindowRect(self.__hwnd)
        return

    def active(self) -> None:
        # おまじない
        # SetForegroundWindowの前にAltキーを押下することでアクティブ化が機能する
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys("%")
        win32gui.ShowWindow(self.__hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(self.__hwnd)
        self.updateRect()
        return

    def is_minimize(self) -> bool:
        left, top, right, bottom = self.__offset
        return left < 0 or top < 0 or right < 0 or bottom < 0
    
    def capture(self, bbox: tuple[int, int, int, int]) -> Image.Image:
        offsetBox = (
            self.__offset[0] + bbox[0],
            self.__offset[1] + bbox[1],
            self.__offset[0] + bbox[2],
            self.__offset[1] + bbox[3]
        )
        return ImageGrab.grab(offsetBox)
    
    @property
    def width(self):
        return self.__offset[2] - self.__offset[0]
    
    @property
    def height(self):
        return self.__offset[3] - self.__offset[1]
    
