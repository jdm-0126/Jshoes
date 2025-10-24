import pymysql

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='root0126',
    database='jshoes_db'
)

with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM product")
    count = cursor.fetchone()[0]
    print(f"Products in database: {count}")
    
    cursor.execute("SELECT name, price, category FROM product LIMIT 3")
    products = cursor.fetchall()
    print("Sample products:")
    for name, price, category in products:
        print(f"  - {name} (₱{price}) - {category}")

connection.close()