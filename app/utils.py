import pathlib


ROOT = pathlib.Path()
LOCAL_STORAGE = ROOT / 'data'


def split(l: list, chunks: int) -> list[list]:
    m, n = divmod(len(l), chunks)
    return [l[i*m+min(i, n):(i+1)*m+min(i+1, n)] for i in range(chunks)]
