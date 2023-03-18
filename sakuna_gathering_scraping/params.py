from enum import Enum


# 1: 地養の洞
# 2: 実りのしとね
# 3: 清澄滝
# 4: 赤井秘湯
# 5: 武火の隠し金山
class Stage(Enum):
    JIYO = 1
    MINORI = 2
    KIYOZUMI = 3
    AKAIDE = 4
    TAKERIBI = 5


class Season(Enum):
    SPRING = 1
    SUMMER = 2
    AUTUMN = 3
    WINTER = 4
    