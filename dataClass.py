import json
from datetime import datetime, timedelta

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
            st+="data:"+str(self.data)[:100]+"\n"
        if self.action==self.N:
            st=f"cmd:{self.message['cmd']}"
        return f"Action => {self.action}\n{'Data' if self.status else 'Error'}   => {st if self.status else self.error}"
    
    def get(self) -> list:
        if self.data==[] or self.data[0].get("data")==None:
            return []
        result=[]
        data=self.data[0]["data"]
        for d in data:
            if d=="": continue
            com = int(d[4:6], 16)
            id = int(d[6:8], 16)
            if id == 11: continue #when id 11 different date format
            d=d[8:]
            day = int(d[14:16])
            mon = int(d[16:18])
            year = int(d[18:20])
            sec = int(d[8:10])
            min = int(d[10:12])
            hour = int(d[12:14])
            cid = int(d[0:6], 16)
            print("cid",cid)
            if com==1 and id==1:
                traffic = int(d[22:24], 16)
                total = int(d[24:32], 16)
                t1 = int(d[32:40], 16)
                t2 = int(d[40:48], 16)
                t3 = int(d[48:56], 16)
                t4 = int(d[56:64], 16)
                meas={
                    "measurement": "traffic",
                    "tags": {"counter": cid, "room": 0, "current_traffic_plan": traffic},
                    "time": datetime(int("20" + str(year)), mon, day, hour, min, sec) - timedelta(hours=3),
                    "fields": {
                            "total": total / 1000.0,
                            "traffic_plan_1": t1 / 1000.0,
                            "traffic_plan_2": t2 / 1000.0,
                            "traffic_plan_3": t3 / 1000.0,
                            "traffic_plan_4": t4 / 1000.0,
                        }
                }
                result.append(meas)
            elif com==1 and id==5:
                total = int(d[38:46], 16)
                phase_a = int(d[46:54], 16)
                phase_b = int(d[54:62], 16)
                phace_c = int(d[62:70], 16)
                meas={
                    "measurement": "power",
                    "tags": {"counter": cid, "room": 0},
                    "time": datetime(int("20" + str(year)), mon, day, hour, min, sec) - timedelta(hours=3),
                    "fields": {
                        "total": total / 1000.0,
                        "phase_a": phase_a / 1000.0,
                        "phase_b": phase_b / 1000.0,
                        "phase_c": phace_c / 1000.0,
                    }
                }
                result.append(meas)
        return result
    


        [{'dev_id': '70B3D58FF1014704', 'data': ['260001015c953e00024514270322000173190a00d84e08009bca01000000000000000000dea9', 
'3200010e5c953e003223142703228a134d01b400c100de00001b00003200001f00006c00001800006a00000000000000b80a', '3200010d5c953e00322314270322395717577d58890000f00000970000000900000900000600001a00003100001f00000dad']}]