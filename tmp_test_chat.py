import json
import urllib.request
import urllib.error

url = 'http://localhost:8002/chat'
data = json.dumps({
    'message': 'Olá Mamute, quais tabelas estão disponíveis?',
    'use_context': True
}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        print('STATUS', resp.status)
        print(resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('HTTP ERROR', e.code)
    print(e.read().decode('utf-8'))
except Exception as e:
    print('ERROR', type(e).__name__, e)
