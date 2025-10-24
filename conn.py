import pymysql

conn = pymysql.connect(host='localhost', user='root', password='root0126', port=3306)
with conn.cursor() as cur:
    cur.execute("CREATE DATABASE IF NOT EXISTS jshoes_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
conn.commit()
conn.close()
print("jshoes_db created or already exists")