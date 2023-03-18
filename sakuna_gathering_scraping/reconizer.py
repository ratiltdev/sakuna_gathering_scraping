import cv2
import numpy

from PIL import Image
from template import Template


SCROLL_BBOX = (506, 18, 521, 585)
MAX_DISPLAY = 9
ITEM_WIDTH = 530
ITEM_HEIGHT = 66


class GatheringReconizer:
    def __init__(self, template: Template) -> None:
        self.__template = template

    def is_display_scrollbar(self, image: Image.Image) -> bool:
        # グレースケールでマッチング
        score = match_template_gray(pil2cv(image.crop(box=SCROLL_BBOX)), self.__template.scrollbar)

        # 類似度参考
        # スクロールバー有 最上段 -> 1.0
        # スクロールバー有 最下段 -> 0.996
        # スクロールバー無 -> 0.978～0.979
        # -> 閾値0.99を超えていればスクロールバーが表示されているものとみなす
        return score > 0.99
    
    def reconize(self, image: Image.Image, result: dict[str, int]):
        # 採集結果をアイテム行に分割
        images = []
        for i in range(MAX_DISPLAY):
            item = image.crop(box=(0, ITEM_HEIGHT * i, ITEM_WIDTH, ITEM_HEIGHT * (i + 1)))
            images.append(pil2cv(item))

        templates: list[tuple[str, cv2.Mat]] = list(self.__template.items.items())
        offset = 0

        # 表示アイテムを上から順に判定
        for image in images:
            is_match = False
            for i in range(offset, len(templates)):
                name, template = templates[i]
                # 二値化でマッチング
                score = match_template_thresh(image, template)
                if score > 0.95:
                    result[name] = match_number(image, self.__template.num_chars)
                    is_match = True
                    offset = i + 1
                    break
            # matchしなければ空欄 -> 以降も空欄とみなして終了
            if not is_match:
                break

        return result


# Pillow -> OpenCV
def pil2cv(image):
    new_image = numpy.array(image, dtype=numpy.uint8)
    # モノクロ
    if new_image.ndim == 2:
        pass
    # カラー
    elif new_image.shape[2] == 3:
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    # 透過
    elif new_image.shape[2] == 4:
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    return new_image


# グレースケールでのテンプレートマッチング
def match_template_gray(image: cv2.Mat, template: cv2.Mat) -> float:
    image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)

    result = cv2.matchTemplate(image_gray, template_gray, method=cv2.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    return max_val

# 二値化でのテンプレートマッチング
def match_template_thresh(image: cv2.Mat, template: cv2.Mat) -> float:
    image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)
    ret, image_thresh = cv2.threshold(image_gray, 128, 255, cv2.THRESH_OTSU)
    ret, template_thresh = cv2.threshold(template_gray, 128, 255, cv2.THRESH_OTSU)

    result = cv2.matchTemplate(image_thresh, template_thresh, method=cv2.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    return max_val


# 個数の判別
def match_number(image: cv2.Mat, templates: list[cv2.Mat]) -> int:
    # 現状2桁は考慮しない 0はスキップ
    for i in range(1, len(templates)):
        template = templates[i]
        # 二値化でマッチング
        score = match_template_thresh(image, template)
        if score > 0.94:
            return i
    # matchしない場合は検出のため99扱い
    return 99
