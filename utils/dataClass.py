import json
from datetime import datetime, timedelta
from utils import logger, log_exceptions

class Action:
    def __init__(self, action) -> None:
        self.action = action

    def __str__(self) -> str:
        return self.action


class CounterData:  # TODO: refactor this shit
    GET_DEVICES = Action("get devices")
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
            self.action = self.GET_DEVICES
            for dev in self.message["devices_list"]:
                self.devices.append({"device_eui": dev["devEui"], "device": dev["devName"]})
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
            st += "devices:"+str([i["devEui"] for i in self.devices])
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

            # logger.debug(f"receive data from vega -> com: {com}, id: {id}")

            if id == 11:
                continue  # when id 11 different date format
            sec = int(data_part[4])
            min = int(data_part[5])
            hour = int(data_part[6])
            day = int(data_part[7])
            mon = int(data_part[8])
            year = int(data_part[9])

            dt = datetime(int("20" + str(year)),
                                 int(mon),
                                 int(day),
                                 int(hour),
                                 int(min),
                                 int(sec)) - timedelta(hours=3)

            counter_factory_id = int(''.join(data_part[3::-1]), 16)

            logger.debug(f"get data for counter {counter_factory_id} with timestamp {dt}")
            measurement = {
                "measurement": None,
                "tags": {"counter": counter_factory_id, "room": 0},
                "time": datetime(int("20" + str(year)),
                                 int(mon),
                                 int(day),
                                 int(hour),
                                 int(min),
                                 int(sec)) - timedelta(hours=3),
                "fields": None
            }

            if com == 1 and id == 1:
                measurement["fields"] = self.get_traffic(data_part)
                measurement["measurement"] = "traffic"
            elif com == 1 and id == 5:
                measurement["fields"] = self.get_power(data_part)
                measurement["measurement"] = "power"
            elif com == 1 and id == 13:
                pass
                # print(len("".join([str(bin(int(i,16)))[2:] for i in data_part[10:14]])), "".join([str(bin(int(i,16)))[2:] for i in data_part[10:14]]))
            if measurement.get("fields"):
                result.append(measurement)
        return result

    @log_exceptions
    def get_power(self, data_part) -> dict:
        total = int("".join(data_part[30:26:-1]), 16)
        phase_a = int("".join(data_part[34:30:-1]), 16)
        phase_b = int("".join(data_part[38:34:-1]), 16)
        phase_c = int("".join(data_part[42:38:-1]), 16)
        data = {"total": total, "phase_a": phase_a, "phase_b": phase_b, "phase_c": phase_c}
        logger.debug(f"power data: {data}")
        return {"total": total, "phase_a": phase_a, "phase_b": phase_b, "phase_c": phase_c}

    @log_exceptions
    def get_traffic(self, data_part) -> dict:
        traffic = int(data_part[11], 16)
        total = int("".join(data_part[15:11:-1]), 16)
        t1 = int("".join(data_part[19:15:-1]), 16)
        t2 = int("".join(data_part[23:19:-1]), 16)
        t3 = int("".join(data_part[27:23:-1]), 16)
        t4 = int("".join(data_part[31:27:-1]), 16)
        data = {"current_traffic": traffic, "total": total, "traffic_plan_1": t1, "traffic_plan_2": t2, "traffic_plan_3": t3, "traffic_plan_4": t4}
        logger.debug(f"traffic data: {data}")
        return {"current_traffic": traffic, "total": total, "traffic_plan_1": t1, "traffic_plan_2": t2, "traffic_plan_3": t3, "traffic_plan_4": t4}

if __name__ == "__main__":
    data_list = [{"ack":0,"data":"310001055f953e00544202190622000c13400807022081c006d1a0f7dd8000151f000082040000370a00005c1000002131","dr":"SF12 BW125 4/5","fcnt":423,"freq":864100000,"gatewayId":"00006CC3743EDEBB","port":4,"rssi":-101,"snr":8.1999999999999993,"ts":1655595884096,"type":"CONF_UP"},{"ack":0,"data":"260001015f953e0017250219062200022c6608070317b104294f570200000000000000000108","dr":"SF12 BW125 4/5","fcnt":422,"freq":868900000,"gatewayId":"00006CC3743EDEBB","port":4,"rssi":-72,"snr":10,"ts":1655594826776,"type":"CONF_UP"},{"ack":0,"data":"3200010e5f953e0047530119062288135703dd03e703ca0300470500660a005f0e000c1e002b1d00aa04000000000000f50c","dr":"SF12 BW125 4/5","fcnt":421,"freq":864100000,"gatewayId":"00006CC3743EDEBB","port":4,"rssi":-97,"snr":8.5,"ts":1655594206094,"type":"CONF_UP"},{"ack":0,"data":"3200010d5f953e004753011906222e5f565d585cb91500b12b00553d0000840400490a005e0e00bb0200870100680000d788","dr":"SF12 BW125 4/5","fcnt":419,"freq":864100000,"gatewayId":"00006CC3743EDEBB","port":4,"rssi":-97,"snr":8.5,"ts":1655592937108,"type":"CONF_UP"},{"ack":0,"data":"310001055f953e00484201190622000c13400807022081c006d1a0f7dd8000361d000084040000460a00006c0e00008d8b","dr":"SF12 BW125 4/5","fcnt":418,"freq":868900000,"gatewayId":"00006CC3743EDEBB","port":4,"rssi":-71,"snr":9.1999999999999993,"ts":1655592278095,"type":"CONF_UP"},{"ack":0,"data":"260001015f953e004820011906220002d94808070317b104d63157020000000000000000683d","dr":"SF12 BW125 4/5","fcnt":416,"freq":868900000,"gatewayId":"00006CC3743EDEBB","port":4,"rssi":-71,"snr":9.8000000000000007,"ts":1655590957771,"type":"CONF_UP"}]
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
