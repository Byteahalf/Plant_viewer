import serial
import time
import re
import requests, json

URL = 'http://localhost:8000/api/upload/'

ser = serial.Serial('COM6',9600)
print('Starting')
pattern = re.compile(r'H:(?P<hum>\d+)C:(?P<tem>\d+).')
while(True):
    ser.write('s'.encode('utf-8'))
    time.sleep(5)
    s = ser.read_all().decode()
    r = pattern.match(s)
    if(r != None):
        device = '70:85:c2:3b:b4:50'
        hum = r.group("hum")
        tem = r.group("tem")
        co2 = 0.66
        t = time.time()
        print(f'温度：{tem}°C 湿度：{hum}%')
        print("正在上传", end='')
        p = requests.post(URL,{'device':device,'tem':tem,'hum':hum,'co2':co2,'t':t})
        code = json.loads(p.text)['code']
        if(code == 200):
            print('\r上传成功')
        else:
            print(f'\r上传失败，错误代码{code}')
    time.sleep(1)