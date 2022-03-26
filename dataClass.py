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
    RX=Action("corresponding device")
    AUTH=Action("auth response")
    N=Action("unknown action")

    def __init__(self, message:str) -> None:
        self.action=self.N
        self.devs=[]#TODO: отказаться от параметра devs
        self.data=[]
        self.status=False
        self.error=""
        self.message:dict=json.loads(message)
        self.status=self.message["status"]
        if not self.status:
            self.error=self.message["err_string"]
        if self.message["cmd"]=='get_devices_resp':
            self.action=self.GET_DEV
            for dev in self.message["devices_list"]:
                self.devs.append({"id":dev["devEui"], "name":dev["devName"]})
        elif self.message["cmd"]=="get_data_resp":
            self.action=self.GET_DATA
            self.data.append({'dev_id':self.message["devEui"], 'data':[i["data"] for i in self.message["data_list"]]})
        elif self.message["cmd"]=="rx":
            self.action=self.RX
            self.data.append({'dev_id':self.message["devEui"], 'data':self.message["data"]})   
        elif self.message["cmd"]=="auth_resp":
            self.action=self.AUTH
            self.data.append({"status":self.message["status"], "error":self.message.get("err_string",""), "token":self.message.get("token","")})
        elif self.message["cmd"]=="console":
            self.action=self.CONSOLE
            self.data.append({"mess":self.message["message"], "color":self.message["color"]})
    
    def __str__(self) -> str:
        st=""
        if self.devs!=[]:
            st+="devices:"+str([i["id"] for i in self.devs])+"\n"
        if self.data!=[]:
            st+="data:"+str(self.data)+"\n"
        if self.action==self.N:
            st=f"cmd:{self.message['cmd']}"
        return f"Action => {self.action}\n{'Data' if self.status else 'Error'}   => {st if self.status else self.error}"