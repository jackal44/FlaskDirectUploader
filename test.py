import requests

print('Beginning file download with requests')

url='http://i3.ytimg.com/vi/J---aiyznGQ/mqdefault.jpg'

r=requests.get(url)

with open('Users/User/Downloads/cat3.jpg', 'wb') as f:
    f.write(r.content)

print(r.status_code)
print(r.headers['content-type'])
print(r.encoding)