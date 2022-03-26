import json
from re import A
from select import select

class Action:
    def __init__(self, action) -> None:
        self.action=action

class Data:

    GET_DEV=Action("get devices")
    GET_DATA=Action("get data")
    N=Action("unknown action")
    action=N

    def __init__(self, message:str) -> None:
        self.message=json.loads(message)
        self.devs=[]
        self.data=[]
        if self.message["cmd"]=='get_devices_resp':
            self.action=self.GET_DEV
            for dev in self.message["devices_list"]:
                self.devs.append({"id":dev["devEui"], "name":dev["devName"]})
        elif self.message["cmd"]=="get_data_resp":
            self.action=self.GET_DATA
            for dt in self.message["data_list"]:
                self.data.append({'dev_id':dt["devEui"], 'data':[i["data"] for i in dt["data_list"]]})
    
    def __str__(self) -> str:
        st=""
        if self.devs!=[]:
            st=", devices:"+str(self.devs)
        elif self.data!=[]:
            st=", data:"+str(self.data)
        return f"{'action':{self.action}{st}}"