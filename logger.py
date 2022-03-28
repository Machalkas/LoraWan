from datetime import datetime
import queue


def logger(que: queue):
    while True:
        if not que.empty():
            data = que.get()
            print(f"{datetime.now().__str__()} | {data}")