import json
from re import A
from select import select

class Action:
    def __init__(self, action) -> None:
        self.action=action
    def __str__(self) -> str:
        return self.action

class Data:

    GET_DEV=Action("get devices")
    GET_DATA=Action("get data")
    CONSOLE=Action("console")
    N=Action("unknown action")
    action=N

    def __init__(self, message:str) -> None:
        self.message=json.loads(message)
        self.devs=[] #TODO: отказаться от параметра devs
        self.data=[] 
        if self.message["cmd"]=='get_devices_resp':
            self.action=self.GET_DEV
            for dev in self.message["devices_list"]:
                self.devs.append({"id":dev["devEui"], "name":dev["devName"]})
        elif self.message["cmd"]=="get_data_resp":
            self.action=self.GET_DATA
            for dt in self.message["data_list"]:
                self.data.append({'dev_id':dt["devEui"], 'data':[i["data"] for i in dt["data_list"]]})
        elif self.message["cmd"]=="console":
            self.action=self.CONSOLE
            self.data.append({"mess":self.message["message"], "color":self.message["color"]})
    
    def __str__(self) -> str:
        st=""
        if self.devs!=[]:
            st="devices:"+str(self.devs)
        elif self.data!=[]:
            st="data:"+str(self.data)
        if self.action==self.N:
            st=f"\ncmd:{self.message['cmd']}"
        return f"Action => {self.action}\nData => {st}"