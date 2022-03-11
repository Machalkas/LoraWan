import json
class Data:
    def __init__(self, message) -> None:
        msg=json.loads(message)
        self.m=msg
        if msg["cmd"]=='get_data_resp':
            pass
