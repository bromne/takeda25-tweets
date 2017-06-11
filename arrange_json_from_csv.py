#!/usr/bin/python3

import os
import csv
import json
import itertools
from datetime import datetime
import pathlib

# CSV の列の順序に完全に対応する、列名のリストです
COLUMNS = [
    "tweet_id",
    "in_reply_to_status_id",
    "in_reply_to_user_id",
    "timestamp",
    "source",
    "text",
    "retweeted_status_id",
    "retweeted_status_user_id",
    "retweeted_status_timestamp",
    "expanded_urls",
]

def delete_folder(path):
    """
    ディレクトリを完全に削除します
    https://stackoverflow.com/questions/303200/how-do-i-remove-delete-a-folder-that-is-not-empty-with-python
    """
    def delete_folder_inner(pth):
        """
        delete_folder の内部処理
        """
        if not pth.exists():
            return
        for sub in pth.iterdir():
            if sub.is_dir():
                delete_folder(sub)
            else:
                sub.unlink()
        pth.rmdir()
    delete_folder_inner(pathlib.Path(path))

def item_from_line(line):
    """
    CSV 行をツイートのデータを表現する辞書に変換します
    """
    item = {}
    for i, column_name in enumerate(COLUMNS):
        item[column_name] = line[i]
    return item

def date_from_item(item):
    """
    ツイートを日付（文字列）に変換します
    """
    return datetime.strptime(item["timestamp"], '%Y-%m-%d %H:%M:%S %z')\
        .strftime('%Y-%m-%d')

with open('tweets.csv') as file:
    destination = "out"

    lines = csv.reader(file)
    _ = next(lines) # 最初の行（ラベル）を除外する

    # ツイートを、日付ごとにグループ化します
    items = map(item_from_line, lines)
    groups = itertools.groupby(items, date_from_item)

    # 出力用フォルダを用意します
    delete_folder(destination)
    os.makedirs(destination, exist_ok=True)

    # グループごとに JSON としてフォルダに出力します
    for group in groups:
        date, tweets = group
        data = {
            "date": date,
            "items": list(tweets),
        }
        with open("{0}/{1}.json".format(destination, date), 'w') as file:
            json.dump(data, file, indent=4, sort_keys=True)
            print("created: {0}/{1}.json".format(destination, date))

    # 出力したファイルの個数を表示します
    files = len(list(pathlib.Path(destination).iterdir()))
    print("{0} files created.".format(files))
