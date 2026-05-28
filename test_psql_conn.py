import psycopg2

try:
    conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='postgres@', database='postgres', connect_timeout=5)
    print('CONNECTED')
    conn.close()
except Exception as e:
    print(type(e).__name__, e)
