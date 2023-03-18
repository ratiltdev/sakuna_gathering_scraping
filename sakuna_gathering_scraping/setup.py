from enum import Enum
import pydirectinput
import time

from params import Stage

class Key(Enum):
    ESCAPE = "escape"
    TAB = "tab"
    Q = "q"
    ENTER = "enter"
    SPACE = "space"
    UP = "up"
    LEFT = "left"
    DOWN = "down"
    RIGHT = "right"


def load() -> None:
    pydirectinput.press(Key.TAB.value)
    time.sleep(0.001)
    pydirectinput.press(Key.Q.value)
    time.sleep(0.001)
    pydirectinput.press(Key.DOWN.value)
    time.sleep(0.001)
    pydirectinput.press(Key.ENTER.value)
    time.sleep(0.001)
    pydirectinput.press(Key.ENTER.value)
    time.sleep(0.001)
    pydirectinput.press(Key.UP.value)
    time.sleep(0.001)
    pydirectinput.press(Key.ENTER.value)
    time.sleep(1)
    return


def move(stage: Stage) -> None:
    match stage:
        case Stage.JIYO:
            pydirectinput.keyDown(Key.RIGHT.value)
            time.sleep(6.25)
            pydirectinput.keyUp(Key.RIGHT.value)
        case Stage.MINORI:
            pydirectinput.keyDown(Key.RIGHT.value)
            time.sleep(6.75)
            pydirectinput.keyUp(Key.RIGHT.value)
        case Stage.KIYOZUMI:
            pydirectinput.keyDown(Key.RIGHT.value)
            time.sleep(6.75)
            pydirectinput.press(Key.SPACE.value)
            time.sleep(6.75)
            pydirectinput.keyUp(Key.RIGHT.value)
        case Stage.AKAIDE:
            pydirectinput.keyDown(Key.RIGHT.value)
            time.sleep(4.6)
            pydirectinput.keyUp(Key.RIGHT.value)
        case Stage.TAKERIBI:
            pydirectinput.keyDown(Key.RIGHT.value)
            time.sleep(7)
            pydirectinput.keyUp(Key.RIGHT.value)
            pydirectinput.keyDown(Key.LEFT.value)
            time.sleep(4)
            pydirectinput.keyUp(Key.LEFT.value)
    return
        

def gathering() -> None:
    pydirectinput.press(Key.ENTER.value)
    time.sleep(0.001)
    pydirectinput.press(Key.ENTER.value)
    time.sleep(5.5)
    return


def scroll() -> None:
    pydirectinput.press(Key.UP.value)
    time.sleep(0.01)
    return


def close() -> None:
    pydirectinput.press(Key.ESCAPE.value)
    time.sleep(0.75)
    return


# 強制終了時にKeyの押下を解除する
def reset() -> None:
    # keyDownを用いているKeyのみ解除
    pydirectinput.keyUp(Key.LEFT.value)
    pydirectinput.keyUp(Key.RIGHT.value)
    return
