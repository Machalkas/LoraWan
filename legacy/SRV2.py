
from datetime import timedelta
import websocket
import json
import time
import base64
import json
import influxdb
try:
    import thread
except ImportError:
    import _thread as thread
import time
from lora.crypto import loramac_decrypt
# from datetime import datetime
# current_datetime = datetime.now()
# print(current_datetime)

TOKEN = ""
client = influxdb.InfluxDBClient(database="stats", host="192.168.0.123")

def selectCMD (message):
    msg = json.loads(message)
    cmd = msg["cmd"]
    if cmd=='auth_resp':
        procAuthResp(msg)
    if cmd == 'getUser':
        procUserResp(msg)
    if cmd == 'get_device_appdata_resp':
        procAppDataResp(msg)
    if cmd == 'get_devices_resp':
        procDevicesResp(msg)
    if cmd == 'get_data_resp':
        procDataResp(msg)

    
        
def procAuthResp (data):
    print('auth_resp')
    #print(data)
    
def procUserResp (data):
    print('getUser')
    #print(data)
    
def procAppDataResp (data):
    print('get_device_appdata_resp')
    #print(data)
    
def procDevicesResp (data):
    print('get_devices_resp')
    #print(data["devices_list"][0]["OTAA"]["appKey"])
    global appKey
    appKey  = data["devices_list"][0]["OTAA"]["appKey"]
    print (appKey)
    #print(data)
    
    return appKey
def procDataResp(data):
#print('get_data_resp')
#payload = MyData['data']
    print("------------------------------------------------")
    #print(data["data_list"][0]["data"].encode())
    #with open('data.txt', 'a') as f:
    #    json.dump(data, f, ensure_ascii=False)
    global dataPyLoad
    dataPyLoad = data["data_list"][0]["data"]
    #with open('data.txt', 'a') as f:
    #    json.dump(dataPyLoad, f, ensure_ascii=False)
    #print(data["data_list"][0]["data"].encode('utf-16'))
    print(dataPyLoad)
    
    from datetime import datetime
    current_datetime = datetime.now()
    print(current_datetime)
    mes = data["data_list"][0]["data"]
    #print(mes.encode('utf-8'))
    N = int(mes[0:2],16)
    #print(N)
    FrameID = int(mes[2:4],16)
    #print(FrameID)
    COM = int(mes[4:6],16)
    #print(COM)
    ID = int(mes[6:8],16)
    #print(ID)
    DATA = mes[8:]
    #print(DATA)   
    if ((COM == 1) & (ID == 1)):
    # Пакет #2 Команда чтения текущих накоплений энергии нарастающим итогом по тарифам
        mes = data["data_list"][0]["data"]
    #print(len(mes))
    #print(mes.encode('utf-8'))
        N = int(mes[0:2], 16)
    #print(N)
        FrameID = int(mes[2:4], 16)
    #print(FrameID)
        COM = int(mes[4:6], 16)
    #print(COM)
        ID = int(mes[6:8], 16)
    #print(ID)
        DATA = mes[8:]
    #print(DATA)
        NumSch = int(DATA[0:8], 16)
        print("Заводской номер счетчика ", NumSch)
        SEC = DATA[8:10]
    # print(SEC)
        MIN = DATA[10:12]
    # print(MIN)
        HOUR = DATA[12:14]
        print("ВРЕМЯ ", SEC, MIN, HOUR)
        DAY = DATA[14:16]
        MON = DATA[16:18]
        YEAR = DATA[18:20]
        print("ДАТА ДЕНЬ/МЕСЯЦ/ГОД ", DAY, MON, YEAR)
        NumTarif = int(DATA[22:24], 16)
        print("Номер текущего тарифа от 1 до 4 ", NumTarif)
        SUMT = int(DATA[24:32], 16)
        print("Энергия нарастающим итогом в Вт*ч.(суммарный тариф) ", SUMT / 1000)
        TARIF1 = int(DATA[32:40], 16)
        print("Энергия нарастающим итогом по 1-му тарифу в Вт*ч.", TARIF1 / 1000)

        TARIF2 = int(DATA[40:48], 16)
        print("Энергия нарастающим итогом по 2-му тарифу в Вт*ч.", TARIF2 / 1000)

        TARIF3 = int(DATA[48:56], 16)
        print("Энергия нарастающим итогом по 3-му тарифу в Вт*ч.", TARIF3 / 1000)

        TARIF4 = int(DATA[56:64], 16)
        print("Энергия нарастающим итогом по 3-му тарифу в Вт*ч.", TARIF4 / 1000)

        CRC16 = DATA[64:68]
        print(CRC16)

        point = [
            {
                "measurement": "traffic",
                "tags": {"counter": NumSch, "room": 0, "current_traffic_plan": int(NumTarif)},
                "time": datetime(int("20" + YEAR), int(MON), int(DAY), int(HOUR), int(MIN), int(SEC)) - timedelta(hours=3),
                "fields": {
                    "total": SUMT / 1000.0,
                    "traffic_plan_1": TARIF1 / 1000.0,
                    "traffic_plan_2": TARIF2 / 1000.0,
                    "traffic_plan_3": TARIF3 / 1000.0,
                    "traffic_plan_4": TARIF4 / 1000.0,
                }
            }
        ]

        try:
            client.write_points(point, database="stats")
        except Exception as err:
            print("Exception occurred while trying to send the data", err)
        
        # DataT = str(current_datetime)
        # Number = str(NumSch)
        # TarifAll = str(SUMT / 1000)
        # Tarif1 = str(TARIF1 / 1000)
        # Tarif2 = str(TARIF2 / 1000)
        # Tarif3 = str(TARIF3 / 1000)
        # Tarif4 = str(TARIF4 / 1000)
    
        # import sqlite3
        # con = sqlite3.connect('example.db')   
        # cur = con.cursor()
        # cur.execute('''CREATE TABLE indications_by_tariffs(DataT text, Number text, TarifAll text, Tarif1 text, Tarif2 text, Tarif3 text, Tarif4 text)''')
        # cur.execute("INSERT INTO indications_by_tariffs VALUES (?,?,?,?,?,?,?)",(DataT, Number, TarifAll, Tarif1, Tarif2, Tarif3, Tarif4))
        # con.commit()
        # con.close()    
        # import sqlite3
        # con = sqlite3.connect('example.db')
        # cur = con.cursor()
        # for row in cur.execute('SELECT * FROM indications_by_tariffs ORDER BY Number'):
            # print(row)
        
    if ((COM == 1) & (ID == 5)):
    # Пакет №5. Текущая мощность и состояние реле управления нагрузкой
        mes = data["data_list"][0]["data"]
    #print(int(len(mes)))
    #print(mes.encode('utf-8'))
        N = int(mes[0:2], 16)
    #print(N)
        FrameID = int(mes[2:4], 16)
    #print(FrameID)
        COM = int(mes[4:6], 16)
    #print(COM)
        ID = int(mes[6:8], 16)
    #print(ID)
        DATA = mes[8:]
    #print(DATA)
        NumSch = int(DATA[0:8], 16)
        print("Заводской номер счетчика ", NumSch)
        SEC = DATA[8:10]
    # print(SEC)
        MIN = DATA[10:12]
    # print(MIN)
        HOUR = DATA[12:14]
        print("ВРЕМЯ ", SEC, MIN, HOUR)
        DAY = DATA[14:16]
        MON = DATA[16:18]
        YEAR = DATA[18:20]
        print("ДАТА ДЕНЬ/МЕСЯЦ/ГОД ", DAY, MON, YEAR)
        print(DATA[38:])
        MSUM = int(DATA[38:46], 16)
        print("Мощность суммарная по всем фазам в Вт ", MSUM / 1000)
        MFA = int(DATA[46:54], 16)
        print("Мощность в Вт. Фаза A ", MFA / 1000)
        MFB = int(DATA[54:62], 16)
        print("Мощность в Вт. Фаза B ", MFB / 1000)
        MFC = int(DATA[62:70], 16)
        print("Мощность в Вт. Фаза C ", MFC / 1000)

        point = [
            {
                "measurement": "power",
                "tags": {"counter": NumSch, "room": 0},
                "time": datetime(int("20" + YEAR), int(MON), int(DAY), int(HOUR), int(MIN), int(SEC)) - timedelta(hours=3),
                "fields": {
                    "total": MSUM / 1000.0,
                    "phase_a": MFA / 1000.0,
                    "phase_b": MFB / 1000.0,
                    "phase_c": MFC / 1000.0,
                }
            }
        ]
        try:
            client.write_points(point, database="stats")
        except Exception as err:
            print("Exception occurred while trying to send the data", err)

    if ((COM == 1) & (ID == 16)):
    # Чтение информации о счетчике. Короткий вариант
        mes = data["data_list"][0]["data"]
    #print(int(len(mes)))
    #print(mes.encode('utf-8'))
        N = int(mes[0:2], 16)
    #print(N)
        FrameID = int(mes[2:4], 16)
    #print(FrameID)
        COM = int(mes[4:6], 16)
    #print(COM)
        ID = int(mes[6:8], 16)
    #print(ID)
        DATA = mes[8:]
    #print(DATA)

    if ((COM == 1) & (ID == 16)):
    #Команда чтения журнала накоплений энергии, зафиксированных за последние 36 месяцев
        mes = data["data_list"][0]["data"]
    #print(int(len(mes)))
    #print(mes.encode('utf-8'))
        N = int(mes[0:2], 16)
    #print(N)
        FrameID = int(mes[2:4], 16)
    #print(FrameID)
        COM = int(mes[4:6], 16)
    #print(COM)
        ID = int(mes[6:8], 16)
    #print(ID)
        DATA = mes[8:]
    #print(DATA)
        NumSch = int(DATA[0:8], 16)
        print("Заводской номер счетчика ", NumSch)
        DATA_TIME = DATA[8:22]
        print(DATA_TIME)
        INDX = DATA[22:24]
        MON = DATA[24:26]
        print(MON)
        YEAR = DATA[26:28]
        print(YEAR)
        slBYTE = DATA[28:30]
        REZ = DATA[30:32]
        ESUM = int(mes[32:40], 16)
        print("Энергия нарастающим итогом в Вт*ч.(суммарный тариф) ", ESUM / 1000)
        ET1 = int(mes[40:48], 16)
        print("Энергия нарастающим итогом по 1-му тарифу в Вт*ч. ", ET1 / 1000)
        ET2 = int(mes[48:56], 16)
        print("Энергия нарастающим итогом по 2-му тарифу в Вт*ч. ", ET2 / 1000)
        ET3 = int(mes[56:64], 16)
        print("Энергия нарастающим итогом по 3-му тарифу в Вт*ч. ", ET3 / 1000)
        ET4 = int(mes[64:72], 16)
        print("Энергия нарастающим итогом по 4-му тарифу в Вт*ч. ", ET4 / 1000)
    if ((COM == 1) & (ID == 11)):
    #Чтение получасовых срезов
        mes = data["data_list"][0]["data"]
    #print(int(len(mes)))
    #print(mes.encode('utf-8'))
        N = int(mes[0:2], 16)
    #print(N)
        FrameID = int(mes[2:4], 16)
    #print(FrameID)
        COM = int(mes[4:6], 16)
    #print(COM)
        ID = int(mes[6:8], 16)
    #print(ID)
        DATA = mes[8:]
    #print(DATA)
        NumSch = int(DATA[0:8], 16)
        print("Заводской номер счетчика ", NumSch)
        INDX = DATA[8:10]
        DATA_TIME = DATA[10:16]
        print(DATA_TIME)
        SREZ1 = int(DATA[16:22], 16)
        print("Первый получасовой срез  ", SREZ1)
        SREZ2 = int(DATA[22:28], 16)
        print("Второй получасовой срез  ", SREZ2)
        SREZ3 = int(DATA[28:34], 16)
        print("Третий получасовой срез  ", SREZ3)
        SREZ4 = int(DATA[34:40], 16)
        print("Четвертый получасовой срез  ", SREZ4)
        SREZ5 = int(DATA[40:46], 16)
        print("Пятый получасовой срез  ", SREZ5)
        SREZ6 = int(DATA[46:52], 16)
        print("Шестой получасовой срез  ", SREZ6)    

        SREZ7 = int(DATA[52:58], 16)
        print("Седьмой получасовой срез  ", SREZ7)
        SREZ8 = int(DATA[58:64], 16)
        print("Восьмой получасовой срез  ", SREZ8)
        SREZ9 = int(DATA[64:70], 16)
        print("Девятый получасовой срез  ", SREZ9)
        SREZ10 = int(DATA[70:76], 16)
        print("Десятый получасовой срез  ", SREZ10)
        SREZ11 = int(DATA[76:82], 16)
        print("Одинадцатый получасовой срез  ", SREZ11)
        SREZ12 = int(DATA[82:88], 16)
        print("Двенадцатый получасовой срез  ", SREZ12)


def procPackInfo (data):
    print(data)
def on_message(ws, message):
    selectCMD(message)


def on_error(ws, error):
    print("ws error:",error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        devInfo = {}
        devEui = ['70B3D58FF0038598','70B3D58FF1015023','70B3D58FF1014756','70B3D58FF101497F','70B3D58FF1014704','70B3D58FF101470F','70B3D58FF1014754','70B3D58FF10146FD']     
        getAuth = json.dumps({'cmd': 'auth_req', 'login': 'root', 'password': '123'})
        ws.send(getAuth)
            
            # getUser = json.dumps({'cmd':'get_users_req'})
            # ws.send(getUser)
            
            # appData = json.dumps({'cmd': 'get_device_appdata_req'})
            # ws.send(appData)
            
        import time
        starttime=time.time()
        while True:
            print("Чтение данных")

            for dev in devEui:
                # get_devices_req = json.dumps({'cmd': 'get_devices_req'})
                # ws.send(get_devices_req)
                
                get_data_req = json.dumps({'cmd': 'get_data_req','devEui':dev,'select':{'direction':'UPLINK'}})
                ws.send(get_data_req)
                
            
            time.sleep(5)
        
        time.sleep(1)
        ws.close()
        print("thread terminating...")

    thread.start_new_thread(run, ())

if __name__ == "__main__":
    websocket.enableTrace(not True)

    ws = websocket.WebSocketApp("ws://192.168.0.183:8002",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    
    ws.run_forever() 
