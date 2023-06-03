import base64
import requests

image = None

with open('example.jpg','rb') as f:
    image = f.read()

image = base64.urlsafe_b64encode(image)
print(requests.post('http://localhost/api/',{'type': 4, 'data': image}).text)
