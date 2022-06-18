import json
from datetime import datetime, timedelta


class Action:
    def __init__(self, action) -> None:
        self.action = action

    def __str__(self) -> str:
        return self.action


class CounterData:  # TODO: refactor this shit
    GET_DEV = Action("get devices")
    GET_DATA = Action("get data")
    CONSOLE = Action("console")
    RX = Action("corresponding device")
    AUTH = Action("auth response")
    N = Action("unknown action")

    def __init__(self, message: str) -> None:
        self.action = self.N
        self.devices = []  # TODO: отказаться от параметра devs
        self.data = []
        self.status = False
        self.error = ""
        self.message: dict = json.loads(message)
        self.status = self.message["status"]
        if not self.status:
            self.error = self.message["err_string"]
        if self.message["cmd"] == 'get_devices_resp':
            self.action = self.GET_DEV
            for dev in self.message["devices_list"]:
                self.devices.append({"id": dev["devEui"], "name": dev["devName"]})
        elif self.message["cmd"] == "get_data_resp":
            self.action = self.GET_DATA
            self.data.append({'dev_id': self.message["devEui"],
                              'data': [i["data"] for i in self.message["data_list"]]})
        elif self.message["cmd"] == "rx":
            self.action = self.RX
            self.data.append(
                {'dev_id': self.message["devEui"],
                 'data': self.message["data"]})
        elif self.message["cmd"] == "auth_resp":
            self.action = self.AUTH
            self.data.append({"status": self.message["status"],
                              "error": self.message.get("err_string", ""),
                              "token": self.message.get("token", "")})
        elif self.message["cmd"] == "console":
            self.action = self.CONSOLE
            self.data.append(
                {"mess": self.message["message"],
                 "color": self.message["color"]})

    def __str__(self) -> str:
        st = ""
        if self.devices != []:
            st += "devices:"+str([i["id"] for i in self.devices])
        if self.data != []:
            st += "data:"+str(self.data)
        if self.action == self.N:
            st = f"cmd:{self.message['cmd']}"
        return f"Action => {self.action} | {'Data' if self.status else 'Error'} => {st if self.status else self.error}"

    def get(self) -> list:
        """
        decode string to list of bytes
        * 1 byte - N (number of all bytes in message, including N)
        * 2 byte - FrameId
        * 3 byte - com (command type)
        * 4 byte - id (command id)
       \n\n com can be :
        * 0x01 - read
        * 0x03 - write
        * 0x0A - exchange error
        * 0xB - submit write command
        """

        if self.data == [] or self.data[0].get("data") is None:
            return []
        result = []
        data_list = self.data[0]["data"]
        for data_string in data_list:
            if data_string == "":
                continue
            byte_data = [data_string[i:i+2] for i in range(0, len(data_string)-2, 2)]
            command_part = [int(i, 16) for i in byte_data[:4]]
            data_part = byte_data[4:]

            N = command_part[0]
            frame_id = command_part[1]
            com = command_part[2]
            id = command_part[3]

            if id == 11:
                continue  # when id 11 different date format
            sec = int(data_part[4])
            min = int(data_part[5])
            hour = int(data_part[6])
            day = int(data_part[7])
            mon = int(data_part[8])
            year = int(data_part[9])

            counter_factory_id = int(''.join(data_part[3::-1]), 16)
            # print("cid", counter_factory_id)
            if com == 1 and id == 1:
                traffic = int(data_string[22:24], 16)
                total = int(data_string[24:32], 16)
                t1 = int(data_string[32:40], 16)
                t2 = int(data_string[40:48], 16)
                t3 = int(data_string[48:56], 16)
                t4 = int(data_string[56:64], 16)
                meas = {
                    "measurement": "traffic",
                    "tags": {"counter": counter_factory_id, "room": 0,
                             "current_traffic_plan": traffic},
                    "time": datetime(int("20" + str(year)),
                                     mon,
                                     day,
                                     hour,
                                     min,
                                     sec) - timedelta(hours=3),
                    "fields": {
                        "total": total / 1000.0,
                        "traffic_plan_1": t1 / 1000.0,
                        "traffic_plan_2": t2 / 1000.0,
                        "traffic_plan_3": t3 / 1000.0,
                        "traffic_plan_4": t4 / 1000.0,
                    }
                }
                result.append(meas)
            elif com == 1 and id == 5:
                total = int(data_string[38:46], 16)
                phase_a = int(data_string[46:54], 16)
                phase_b = int(data_string[54:62], 16)
                phase_c = int(data_string[62:70], 16)
                meas = {
                    "measurement": "power",
                    "tags": {"counter": counter_factory_id, "room": 0},
                    "time": datetime(int("20" + str(year)),
                                     int(mon),
                                     int(day),
                                     int(hour),
                                     int(min),
                                     int(sec)) - timedelta(hours=3),
                    "fields": {
                        "total": total / 1000.0,
                        "phase_a": phase_a / 1000.0,
                        "phase_b": phase_b / 1000.0,
                        "phase_c": phase_c / 1000.0,
                    }
                }
                result.append(meas)
        return result

if __name__ == "__main__":
    data_list = [{"data": "310001055f953e00093517030522020c13400807022081c006d1a0f7dd800046170000500500007a0a00007c070000c6aa"}]
    raw_data = {
        "cmd": "get_data_resp",
        "devEui": "1",
        "data_list": data_list,
        "status": True
    }
    raw_data = json.dumps(raw_data)
    print(CounterData(raw_data).get())
    cd = CounterData(raw_data).get()[0]
    total = cd["fields"].get("phase_a")+cd["fields"].get("phase_b")+cd["fields"].get("phase_c")
    print(cd["fields"]["total"], total)
