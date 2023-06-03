import hashlib

def device_code(device):
    return str(int(hashlib.md5(device.encode('utf-8')).hexdigest()[-6:],16) + 10000000)

while(True):
    c = input()
    print(device_code(c))