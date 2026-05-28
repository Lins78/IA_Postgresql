import urllib.request
import sys

url = 'http://127.0.0.1:8002'
try:
    with urllib.request.urlopen(url, timeout=5) as r:
        status = r.getcode()
        body = r.read(200).decode('utf-8', errors='ignore')
        print('STATUS', status)
        print('BODY_PREVIEW')
        print(body)
except Exception as e:
    print('ERROR', type(e).__name__, str(e))
    sys.exit(1)
