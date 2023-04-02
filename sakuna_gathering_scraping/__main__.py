import click
import csv
import datetime
import os
import sys
import time
import setup

from params import *
from recognizer import *
from template import *
from window import *


# Title
WINDOW_TITLE = "天穂のサクナヒメ"

# WindowSize: 1920 x 1080
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
WINDOW_OFFSET = (8, 31, 8, 8)

# CaptureArea
RESULT_BBOX = (417, 210, 947, 815)

# Message
MESSAGE_NOT_RUNNING = "天穂のサクナヒメが起動していないため終了します。"
MESSAGE_MINIMIZE = "天穂のサクナヒメのウィンドウが最小化されており取得できませんでした。"
MESSAGE_WINDOW_SIZE = "天穂のサクナヒメは1920x1080のウィンドウサイズで起動してください。"
MESSAGE_DIFFERENT_HEADER = "異なる条件で記録されたdata.csvが存在するため終了します。"


def get_window() -> Window:
    # ハンドルが取得できない場合は終了
    hwnd: int = win32gui.FindWindow(None, WINDOW_TITLE)
    if hwnd <= 0:
        print(MESSAGE_NOT_RUNNING)
        sys.exit()
    
    window = Window(hwnd)

    # アクティブ化
    window.active()
    time.sleep(3)

    # ウィンドウサイズのチェック
    width = window.width - (WINDOW_OFFSET[0] + WINDOW_OFFSET[2])
    height = window.height - (WINDOW_OFFSET[1] + WINDOW_OFFSET[3])
    if width != WINDOW_WIDTH or height != WINDOW_HEIGHT:
        print(MESSAGE_WINDOW_SIZE, width, height)
        sys.exit()

    return window


# データ保存用csvファイルの初期化 -> start_countを返却
def init_csv(path: str, item_labels: list[str]) -> int:
    csv_path = os.path.join(path, "data.csv")
    csv_header = ["timestamp"] + item_labels

    # data.csvが存在する場合は最低限ヘッダーが一致するかチェック
    if (os.path.isfile(csv_path)):
        with open(csv_path, mode="r") as f:
            reader = csv.reader(f)
            header = reader.__next__()
            if (header != csv_header):
                print(MESSAGE_DIFFERENT_HEADER)
                sys.exit()
            else:
                return sum(1 for line in f) + 1
    # 新規作成
    else:
        with open(csv_path, mode="w", newline="") as f:
            csv.writer(f).writerow(csv_header)
    return 1


# データ保存
def write_csv(path: str, data: list) -> None:
    with open(os.path.join(path, "data.csv"), mode="a", newline="") as f:
        csv.writer(f).writerow(data)
    return


# 結果を成形
def format_result(result: dict[str, int], item_labels: list[str]) -> list:
    # timestamp
    data = [datetime.datetime.now().isoformat(sep=" ", timespec="seconds")]
    # sort
    for label in item_labels:
        # 出現していないアイテムなら個数は0
        data.append(result.get(label, 0))
    
    return data


@click.command()
@click.option("--stage_id", prompt="StageID", type=click.IntRange(1, 5), help="1: 地養の洞, 2: 実りのしとね, 3: 清澄滝, 4: 赤井秘湯, 5: 武火の隠し金山")
@click.option("--season_id", prompt="Season", type=click.IntRange(1, 4), help="1: 春, 2: 夏, 3: 秋, 4: 冬")
@click.option("--count", prompt="Count", type=click.IntRange(1, 2000), help="測定回数")
@click.option("--path", prompt="SavePath", type=click.Path(exists=True), help="キャプチャ保存ディレクトリ")
def main(stage_id, season_id, count, path):
    try:
        stage = Stage(stage_id)
        season = Season(season_id)
        
        window = get_window()
        template = load_template(stage, season)
        recognizer = GatheringRecognizer(template)
        
        item_labels = list(template.items.keys())
        offset = init_csv(path, item_labels)
        for i in range(offset, count + offset):
            setup.load()
            setup.move(stage)
            setup.gathering()
            
            image = window.capture(RESULT_BBOX)
            image.save(os.path.join(path, f"{i:03}.png"))
            result = recognizer.reconize(image, dict())
            
            # スクロールバーが表示されているなら差分をキャプチャ
            if recognizer.is_display_scrollbar(image):
                setup.scroll()
                image = window.capture(RESULT_BBOX)
                image.save(os.path.join(path, f"{i:03}(2).png"))
                result = recognizer.reconize(image, result)
            
            write_csv(path, format_result(result, item_labels))
            setup.close()
        
    except KeyboardInterrupt:
        setup.reset()
        sys.exit()

@click.command()
@click.option("--stage_id", prompt="StageID", type=click.IntRange(1, 5), help="1: 地養の洞, 2: 実りのしとね, 3: 清澄滝, 4: 赤井秘湯, 5: 武火の隠し金山")
@click.option("--season_id", prompt="Season", type=click.IntRange(1, 4), help="1: 春, 2: 夏, 3: 秋, 4: 冬")
@click.option("--count", prompt="Count", type=click.IntRange(1, 1000), help="測定回数")
@click.option("--path", prompt="SavePath", type=click.Path(exists=True), help="キャプチャ保存ディレクトリ")
def re_reconize(stage_id, season_id, count, path):
    try:
        stage = Stage(stage_id)
        season = Season(season_id)
        
        template = load_template(stage, season)
        reconizer = GatheringRecognizer(template)
        
        item_labels = list(template.items.keys())
        offset = init_csv(path, item_labels)
        
        for i in range(offset, count + offset):
            image = Image.open(os.path.join(path, f"{i:03}.png"))
            result = reconizer.reconize(image, dict())
            
            # スクロールバーが表示されているなら差分をキャプチャ
            if reconizer.is_display_scrollbar(image):
                image = Image.open(os.path.join(path, f"{i:03}(2).png"))
                result = reconizer.reconize(image, result)
            
            write_csv(path, format_result(result, item_labels))
        
    except KeyboardInterrupt:
        sys.exit()


@click.command()
@click.option("--stage_id", prompt="StageID", type=click.IntRange(1, 5), help="1: 地養の洞, 2: 実りのしとね, 3: 清澄滝, 4: 赤井秘湯, 5: 武火の隠し金山")
@click.option("--season_id", prompt="Season", type=click.IntRange(1, 4), help="1: 春, 2: 夏, 3: 秋, 4: 冬")
@click.option("--path", prompt="ImagePath", type=click.Path(exists=True), help="キャプチャ画像パス")
def single_reconize(stage_id, season_id, path):
    try:
        stage = Stage(stage_id)
        season = Season(season_id)
        
        template = load_template(stage, season)
        reconizer = GatheringRecognizer(template)
        
        image = Image.open(path)
        result = reconizer.reconize(image, dict())
        print(result)
        
    except KeyboardInterrupt:
        sys.exit()

if __name__ == "__main__":
    main()
    