import urllib.request, json

# Start session
req = urllib.request.Request('http://127.0.0.1:8002/session/start', data=json.dumps({}).encode('utf-8'), headers={'Content-Type':'application/json'})
with urllib.request.urlopen(req, timeout=5) as r:
    print('SESSION START STATUS', r.getcode())
    print(r.read().decode())

# Send chat message
chat = {'message': 'Quais tabelas existem?'}
req2 = urllib.request.Request('http://127.0.0.1:8002/chat', data=json.dumps(chat).encode('utf-8'), headers={'Content-Type':'application/json'})
with urllib.request.urlopen(req2, timeout=10) as r2:
    print('CHAT STATUS', r2.getcode())
    resp = r2.read().decode()
    print(resp)
