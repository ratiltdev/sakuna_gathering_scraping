import cv2
import json
import os

from dataclasses import dataclass
from functools import cache
from params import Stage, Season


@dataclass
class Item:
    id: str
    name: str
    season: tuple[bool, bool, bool, bool]


@dataclass
class Template:
    items: dict[str, cv2.Mat]
    num_chars: list[cv2.Mat]
    scrollbar: cv2.Mat


def load_template(stage: Stage, season: Season):
    items = load_item_list(stage, season)
    return Template(
        items=item_templates(stage, items),
        num_chars=load_num_char_templates(),
        scrollbar=load_scrollbar_template()
    )


def load_item_list(stage: Stage, season: Season) -> list[Item]:
    path = os.path.join(item_directory_path(stage), "items.json")
    file = open(path, "r", encoding="utf-8_sig")
    items: list[Item] = json.load(file, object_hook=decord_item)
    return list(filter(lambda item: item.season[season.value], items))


def decord_item(data: dict) -> Item:
    return Item(id=data["id"], name=data["name"], season=data["season"])


@cache
def item_directory_path(stage: Stage) -> str:
    match stage:
        case Stage.JIYO:
            path = "01_jiyo"
        case Stage.MINORI:
            path = "02_minori"
        case Stage.KIYOZUMI:
            path = "03_kiyozumi"
        case Stage.AKAIDE:
            path = "04_akaide"
        case Stage.TAKERIBI:
            path = "05_takeribi"
    return f"templates/{path}/"


def item_templates(stage: Stage, items: list[Item]) -> dict:
    item_dict: dict = dict()
    path = item_directory_path(stage)

    for item in items:
        item_dict[item.name] = cv2.imread(os.path.join(path, f"{item.id}.png"))

    return item_dict


def load_num_char_templates() -> list[cv2.Mat]:
    result: list[cv2.Mat] = []
    for i in range(10):
        result.append(cv2.imread(f"templates/num_chars/{i}.png"))
    return result


def load_scrollbar_template() -> cv2.Mat:
    return cv2.imread("templates/scrollbar.png")

