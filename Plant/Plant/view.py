from run import IMAGE
from socket import socket
import threading
from socketserver import BaseRequestHandler, ThreadingTCPServer
import django
from django.http import request
from django.shortcuts import redirect, render
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
import time
import hashlib
import base64

from dates.models import *

DT_DATA = '1'
DT_STATUS = '2'
DT_TCP_REQUIRE = '3'
DT_IMAGE = '4'

GET_CONTROL = '1'
GET_DATA = '2'
GET_CONPONENT = '3'
GET_DEIVCE = '4'

GET = '0'
SET = '1'
NEW = '2'

SUCCESS = 200
UNKNOWN_ERROR = 1
REQUEST_TYPE_ERROR = 10
LACK_OF_PARAMETER = 11
USER_OR_PASSWORD_ERROR = 12
CONPONENT_NOT_RECALL = 13
DEVICE_ALREADY_EXIST = 14
WRONG_DEVICE_CODE = 15
WRONG_DATABASE_FIELD = 16

FAN = 1
LIGHT = 2
WATER = 3
CAMERA = 4

ON = 1
OFF = 0

uptime = []

#--------------------------TCP服务器部分开始------------------------------------------
class server_flag():
    server_on = False
    message_list = []
    read_lock = threading.Lock()
    socket = None
    server = None

class Tcp_Handle(BaseRequestHandler):
    def handle(self):
        self.t = 0
        while(True):
            device = self.request.recv(1024).decode()
            device = device.split(',')
            if(len(device) == 3 and device[0] == 'device' and device[2] == 'fin'):
                self.device = device[1]
                self.request.send('recv'.encode('utf-8'))
                if(self.request.recv(1024).decode() == 'recv'):
                    print(f'设备{self.device}验证成功')
                    break

        while(True):
            self.t = self.t + 1
            if(self.t > 60):
                try:
                    self.request.send('beat'.encode('utf-8'))
                    msg = self.request.recv(1024).decode()
                    if(msg != "beat"):
                        print(f"设备{self.device}已断开")
                        self.request.close()
                        break
                except:
                    print(f"设备{self.device}已断开")
                    return
                    
            time.sleep(2)
            server_flag.read_lock.acquire()
            if(len(server_flag.message_list) == 0):
                server_flag.read_lock.release()
                continue
            for i in range(len(server_flag.message_list)):
                if(server_flag.message_list[i]['device'] == self.device and server_flag.message_list[i]['process'] == False):
                    print(f'检测到指令{server_flag.message_list[i]}')
                    info = server_flag.message_list[i]
                    component_type = server_flag.message_list[i]['type']
                    control_type = server_flag.message_list[i]['switch']
                    server_flag.read_lock.release()
                    while(True):
                        try:
                            self.request.send(json.dumps({'type':component_type, 'switch': control_type}).encode('utf-8'))
                            rec = self.request.recv(1024)
                            if(rec == b''):
                                self.request.close()
                                print(f'{self.device}已断开')
                                return
                            else:
                                rec = rec.decode()
                                if(rec == 'SUCCESS'):
                                    print('指令发送成功')
                                    server_flag.read_lock.acquire()
                                    server_flag.message_list.remove(info)
                                    info['process'] = True
                                    server_flag.message_list.append(info)
                                    server_flag.read_lock.release()
                                    break
                        except ConnectionResetError as e:
                            print(f'{self.device}已断开')
                            return
                        except:
                            print(f'未知错误')
                            return
                        

class server(threading.Thread):
    def __init__(self):
        super().__init__()
        self.name="TCP"

    def run(self):
        server_flag.server_on = True
        server_flag.socket = ThreadingTCPServer(('0.0.0.0',8778),Tcp_Handle)
        server_flag.socket.serve_forever()

def start_server():
    print('TCP服务启动')
    server_flag.server = server()
    server_flag.server.start()

def command(conponent,switch,device = '00:00:00:00:00:00'):
    print('加入消息队列{}'.format({'device': device,'type':conponent,'switch':switch,'process':False}))
    server_flag.read_lock.acquire()
    server_flag.message_list.append({'device': device,'type':conponent,'switch':switch,'process':False})
    server_flag.read_lock.release()
    time.sleep(2)
    print(wait_recieve(conponent,switch,device))

def wait_recieve(conponent,switch,device = '00:00:00:00:00:00'):
    server_flag.read_lock.acquire()
    for i in server_flag.message_list:
        if(i['device'] == device and i['type'] == conponent and i['switch'] == switch and i['process'] == True):
            server_flag.message_list.remove(i)
            print('已删除')
            server_flag.read_lock.release()
            return True
    server_flag.read_lock.release()
    return False
#--------------------------TCP服务器部分结束---------------------------------------

#--------------------------身份验证部分开始-----------------------------------------
def refresh_uuid(uid,u):
    flag = False
    for i in range(len(uptime)):
        if(uptime[i]['uuid'] == str(uid)):
            uptime[i]['t'] = time.time() + 900
            flag = True
    if(flag == False):
        uptime.append({'uuid': str(uid), 'user':u, 't': time.time()+900})


def del_uuid():
    for i in range(len(uptime)):
        if(time.time()-uptime[i]['t'] >= 900):
            del uptime[i]


def check_uuid(uid):
    del_uuid()
    for i in range(len(uptime)):
        if(uptime[i]['uuid'] == uid):
            if(uptime[i]['t'] - time.time() <= 900):
                return True
    return False

def trans_to_bool(source,target):
    if(source == target):
        return True
    else:
        return False

def get_user(uid):
    del_uuid()
    for i in range(len(uptime)):
        if(uptime[i]['uuid'] == uid):
            return uptime[i]['user']
    else:
        return None


#-----------------------身份验证部分结束-------------------------------------------------


def main(request: HttpRequest):
    if(request.method == 'GET'):
        return render(request, 'Test.html')

#-------------模拟机部分----------------
class reader(threading.Thread):
    def __init__(self):
        super().__init__()
        print('模拟机已启动')

    def run(self):
        while(True):
            s = input('>')
            s = s.split(' ')
            if(s[0] == 'fan'):
                if(s[1] == 'on'):
                    command(FAN, ON)
                if(s[1] == 'off'):
                    command(FAN, OFF)
            if(s[0] == 'light'):
                if(s[1] == 'on'):
                    command(LIGHT, ON)
                if(s[1] == 'off'):
                    command(LIGHT, OFF)
            if(s[0] == 'water'):
                if(s[1] == 'on'):
                    command(WATER, ON)
                if(s[1] == 'off'):
                    command(WATER, OFF)
            if(s[0] == 'image'):
                command(IMAGE,ON)

c = reader()
c.start()
#-----------------------------

#---------设备验证信息---------

def device_code(device):
    return str(int(hashlib.md5(device.encode('utf-8')).hexdigest()[-6:],16) + 10000000)

#-------设备验证信息结束---------


@csrf_exempt
def api(request: HttpRequest):
    if(request.method == 'POST'):
        if(request.POST.get('type') == DT_DATA):
            try:
                carbon_dioxide = request.POST['co2']
                soil_temperature = request.POST['stemp']
                air_temperature = request.POST['atemp']
                humidity = request.POST['humid']
                device = request.POST['device']
                t = request.POST['t']
            except django.utils.datastructures.MultiValueDictKeyError as e:
                return JsonResponse({'code': LACK_OF_PARAMETER})
            except:
                return JsonResponse({'code': UNKNOWN_ERROR})

            date = plantInfo(time=float(t),\
                         dirt_temperature=float(soil_temperature),\
                         air_temperature=float(air_temperature),\
                         humidity=float(humidity),\
                         carbon_dioxide=float(carbon_dioxide),\
                         device=device
                         )
            date.save()
            return JsonResponse({'code': SUCCESS})

        elif(request.POST.get('type') == DT_STATUS):
            try:
                fan = trans_to_bool(request.POST['fan'],'1')
                light = trans_to_bool(request.POST['light'],'1')
                water = trans_to_bool(request.POST['water'],'1')
                device = request.POST['device']
                t = request.POST['t']
            except django.utils.datastructures.MultiValueDictKeyError as e:
                return JsonResponse({'code': LACK_OF_PARAMETER})
            except:
                return JsonResponse({'code': UNKNOWN_ERROR})

            date = component(device=device, time=float(t), fan=fan, light=light, water=water)
            date.save()
            return JsonResponse({'code': SUCCESS})
            
        elif(request.POST.get('type') == DT_TCP_REQUIRE):
            if(server_flag.server_on == False):
                start_server()
            return JsonResponse({'code': SUCCESS})
        elif(request.POST.get('type') == DT_IMAGE):
            try:
                image = request.POST.get('data')
            except django.utils.datastructures.MultiValueDictKeyError as e:
                return JsonResponse({'code': LACK_OF_PARAMETER})
            except:
                return JsonResponse({'code': UNKNOWN_ERROR})
            image = base64.urlsafe_b64decode(image)
            with open(f'{time.time()}.jpg','wb') as f:
                f.write(image)
            return JsonResponse({'code': SUCCESS})

@csrf_exempt
def get(request:HttpRequest):
    if(request.method == 'POST'):
        get_type = request.POST.get('type')
        if(get_type == GET_CONTROL):
            try:
                device = request.POST['device']
                conponent = request.POST['conponent']
                switch = request.POST['switch']
            except django.utils.datastructures.MultiValueDictKeyError as e:
                return JsonResponse({'code': LACK_OF_PARAMETER})
            command(int(conponent), int(switch), device)
            i = 0
            while(not wait_recieve(int(conponent), int(switch), device)):
                i = i + 1
                if(i >= 5):
                    return JsonResponse({'code':CONPONENT_NOT_RECALL})
            return JsonResponse({'code':SUCCESS})
        elif(get_type == GET_CONPONENT):
            pass #数据库支持
        elif(get_type == GET_DATA):
            try:
                device = request.POST['device']
                t = request.POST['t']
            except django.utils.datastructures.MultiValueDictKeyError as e:
                return JsonResponse({'code': LACK_OF_PARAMETER})
            try:
                send_data = []
                data = plantInfo.objects.filter(time__gte=float(t),device=device)
                for i in data:
                    send_data.append({'t':int(i.time),'s':float(i.dirt_temperature), 'a':float(i.air_temperature), 'h':float(i.humidity), 'c': float(i.carbon_dioxide)})
                return JsonResponse({'code':SUCCESS, 'data':send_data})
            except:
                return JsonResponse({'code':WRONG_DATABASE_FIELD})
            
        elif(get_type == GET_DEIVCE):
            try:
                method = request.POST['method']
                user = request.POST['u']
                register_code = ''
                device = ''
                name = ''
                if(method == NEW):
                    device = request.POST['device']
                    register_code = request.POST['code']
                    name = request.POST['name']
            except django.utils.datastructures.MultiValueDictKeyError as e:
                return JsonResponse({'code': LACK_OF_PARAMETER})
            if(method == NEW):
                try:
                    if(register_code == device_code(device)):
                        data = userDevice(user=get_user(user), device=device, name=name)
                        data.save()
                        return JsonResponse({'code': SUCCESS})
                    else:
                        return JsonResponse({'code': WRONG_DEVICE_CODE})
                except django.db.IntegrityError:
                    return JsonResponse({'code': DEVICE_ALREADY_EXIST})
                
            elif(method == GET):
                u = get_user(user)
                data = userDevice.objects.all()
                datas = []
                for i in data:
                    datas.append({'id':i.device,'name':i.name})
                return JsonResponse({'code': SUCCESS, 'data':{'device':datas}})

        else:
            
            return JsonResponse({'code': LACK_OF_PARAMETER,'data':str(request.POST)})

@csrf_exempt
def login(request: HttpRequest):
    if(request.method == 'GET'):
        # web page
        return render(request, 'login.html')
    elif(request.method == 'POST'):
        try:
            i = json.loads(request.body.decode('utf-8'))
            user = i.get("user")
            p = i.get("password")
            if(user == '1' and p == '1'):
                u = uuid.uuid1()
                refresh_uuid(str(u),user)
                return JsonResponse({'code': SUCCESS, 'id': u})
            else:
                return JsonResponse({'code': USER_OR_PASSWORD_ERROR})
        except Exception as e:
            print(e)
            return JsonResponse({'code':UNKNOWN_ERROR})


def index(request: HttpRequest):
    if(request.method == 'GET'):
        print(request.GET.get("uuid"))
        if(check_uuid(request.GET.get("uuid"))):
            return render(request, 'index.html')
        else:
            return redirect("/login")
