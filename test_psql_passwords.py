import psycopg2

candidates = ['postgres1', 'postgres@', 'postgres', 'postgres123', 'postgres@1']
ports = [5432, 5433]

for port in ports:
    print(f'=== port={port} ===')
    for pwd in candidates:
        try:
            conn = psycopg2.connect(host='localhost', port=port, user='postgres', password=pwd, database='postgres', connect_timeout=5)
            print(f'[OK] port={port} password={pwd}')
            conn.close()
        except Exception as e:
            msg = str(e).replace('\n', ' ')
            print(f'[FAIL] port={port} password={pwd} -> {msg}')
