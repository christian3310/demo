import json
import os
import pathlib


ROOT = pathlib.Path()
LOCAL_STORAGE = ROOT / 'data'


def split(l: list, chunks: int) -> list[list]:
    m, n = divmod(len(l), chunks)
    return [l[i*m+min(i, n):(i+1)*m+min(i+1, n)] for i in range(chunks)]


def save_json_to_local(filename, data, **kwargs):
    if not LOCAL_STORAGE.exists():
        os.mkdir(LOCAL_STORAGE)
    
    with open(LOCAL_STORAGE / filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, **kwargs)
