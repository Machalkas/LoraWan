import json
class Data:
    def __init__(self, message) -> None:
        self.message=json.loads(message)
        self.action=self.message["cmd"]
        if self.message["cmd"]=='get_data_resp':
            pass
