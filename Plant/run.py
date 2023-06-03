import base64
from random import randint
import time,sys
import os
import requests
import json
import socket

import random
import threading

#--------------------------------
#使用代码之前请确认时间正确
#如有自动对时的指令请填写到下面
#--------------------------------

#----------可修改部分-------------
addr_port = 'http://127.0.0.1/api/'
addr_tcp = '127.0.0.1'
port_tcp = 8778
ntp_command = 'echo 客户端启动' #自动对时指令
upload_time = 60    #数据上报时间间隔(s)
image_path = 'example.jpg'
#--------可修改部分结束-----------

#--------常数定义，不可修改-------
DT_DATA = 1
DT_STATUS = 2
DT_TCP_REQUIRE =3

SUCCESS = 200
UNKNOWN_ERROR = 1
REQUEST_TYPE_ERROR = 10
LACK_OF_PARAMETER = 11
USER_OR_PASSWORD_ERROR = 12
#---------常数定义结束-----------

#----------以下为模拟部分---------
device = '00:00:00:00:00:00'

fan = 0
light = 0
water = 0

def air_temperature():
    return random.randrange(100,300,5) / 10
def soil_temperature():
    return random.randrange(100,300,5) / 10
def humidity():
    return random.randrange(0,100,5) / 100
def carbon_dioxide():
    return random.randrange(0,100,5) / 100

def fan_on():
    global fan
    fan = 1
    print('风扇打开')

def fan_off():
    global fan
    fan = 0
    print('风扇关闭')

def light_on():
    global light
    light = 1
    print('灯打开')

def light_off():
    global light
    light = 0
    print('灯关闭')

def water_on():
    global water
    water = 1
    print('水打开')

def water_off():
    global water
    water = 0
    print('水关闭')

def cemara_open():
    pass

class reader(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        while(True):
            s = input('>')
            if(s == 'fan'):
                print(fan)
            elif(s == 'light'):
                print(light)
            elif(s == 'water'):
                print(water)
#--------模拟部分结束--------------

#--------TCP部分-------------
FAN = 1
LIGHT = 2
WATER = 3
IMAGE = 4

ON = 1
OFF = 0

TCP_on = False
class TCP_connect(threading.Thread):
    def __init__(self,addr:str,port:int,methed_list:dict,device:str):
        super().__init__()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr_port = (addr,port)
        self.method_list = methed_list
        self.device = device

    def run(self):
        self.s.connect(self.addr_port)
        self.s.send(f'device,{self.device},fin'.encode('utf-8'))
        if(self.s.recv(1024).decode() == 'recv'):
            self.s.send('recv'.encode('utf-8'))
        self.TCP_on = True
        while(True):
            u = self.s.recv(1024).decode()
            if(u == 'beat'):
                continue
            msg = json.loads(u)
            try:
                if(msg['type'] == FAN):
                    if(msg['switch'] == ON):
                        self.method_list['fan_on']()
                        self.s.send('SUCCESS'.encode('utf-8'))
                        print('指令成功')
                    elif(msg['switch'] == OFF):
                        self.method_list['fan_off']()
                        self.s.send('SUCCESS'.encode('utf-8'))
                        print('指令成功')
                if(msg['type'] == LIGHT):
                    if(msg['switch'] == ON):
                        self.method_list['light_on']()
                        self.s.send('SUCCESS'.encode('utf-8'))
                        print('指令成功')
                    elif(msg['switch'] == OFF):
                        self.method_list['light_off']()
                        self.s.send('SUCCESS'.encode('utf-8'))
                        print('指令成功')
                if(msg['type'] == WATER):
                    if(msg['switch'] == ON):
                        self.method_list['water_on']()
                        self.s.send('SUCCESS'.encode('utf-8'))
                        print('指令成功')
                    elif(msg['switch'] == OFF):
                        self.method_list['water_off']()
                        self.s.send('SUCCESS'.encode('utf-8'))
                        print('指令成功')
                if(msg['type'] == IMAGE):
                    cemara_open()
                    with open('example.jpg','rb') as f:
                        while(True):
                            res = requests.post(addr_port,{'type': 4, 'data': base64.urlsafe_b64encode(f.read())}).text
                            if(json.loads(res)['code'] == 200):
                                print('指令成功')
                                break
                            else:
                                print('指令失败')
                                break
                        self.s.send('SUCCESS'.encode('utf-8'))
                        print('ss')

                    
            except:
                print('Command Error: Socket will close')
                self.s.close()
                self.TCP_on = False
                start()
                break

def start(addr:str,port:str,method_list:dict,device:str):
    c = TCP_connect(addr,port,method_list,device)
    c.daemon = True
    c.start()

def is_connected():
    return TCP_on
#------TCP部分结束-----------

def report_component():
    while(True):
        u = requests.post(addr_port,{'type':DT_STATUS,'t':time.time(),'device':device,'fan':fan,'light': light,'water': water}).text
        u = json.loads(u)
        if(u['code'] == 200):
            print('组件数据上报成功')
            break
        else:
            print(u['code'])

def check_component():
    if(randint(0,2 != 1)):
        return
    #这里写的是界定是否需要组件启动的代码
    #启动完调用上面那个函数上报一次数据
    #------------模拟数据--------------
    global fan,light,water
    fan = random.randint(0,1)
    light = random.randint(0,1)
    water = random.randint(0,1)
    #---------------------------------
    report_component()
    pass

def report_data():
    air_temperature_data = air_temperature()
    soil_temperature_data = soil_temperature()
    humidity_data = humidity()
    carbon_dioxide_data = carbon_dioxide()
    check_component()
    while(True):
        u = requests.post(addr_port,{'type': DT_DATA,'t':time.time(),'device':device,'atemp':air_temperature_data,'stemp':soil_temperature_data,'co2':carbon_dioxide_data,'humid':humidity_data}).text
        u = json.loads(u)
        if(u['code'] == 200):
            print('数据上报成功')
            break
    

def main():
    try:
        #模拟机准备，正式产品务必删除
        r = reader()
        r.daemon = True
        r.start()
        print('模拟机正在运行')

        #设备准备
        os.system(ntp_command)

        #设备TCP连接部分
        method_list={
        'fan_on':fan_on,
        'fan_off':fan_off,
        'light_on':light_on,
        'light_off':light_off,
        'water_on':water_on,
        'water_off':water_off
        }
        requests.post(addr_port,{'type':DT_TCP_REQUIRE})
        start(addr_tcp,port_tcp,method_list,device)

        #正常数据上报部分
        while(True):
            report_data()
            time.sleep(upload_time)

    except KeyboardInterrupt:
        sys.exit(0)

    
if(__name__ == '__main__'):
    main()
