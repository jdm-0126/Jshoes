#!/usr/bin/env python3
"""
Check database schema and tables
"""

import pymysql

def check_database():
    try:
        # Direct MySQL connection
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root0126',
            database='jshoes_db'
        )
        
        with connection.cursor() as cursor:
            # Check current database
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()[0]
            print(f"SUCCESS: Connected to database: {current_db}")
            
            # Check tables
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            if tables:
                print(f"SUCCESS: Found {len(tables)} tables:")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("ERROR: No tables found in database")
                print("Need to create schema first")
                
        connection.close()
        
    except pymysql.Error as e:
        print(f"ERROR: MySQL Error: {e}")
        if "Unknown database" in str(e):
            print("Database 'jshoes_db' doesn't exist. Create it first:")
            print("CREATE DATABASE jshoes_db;")
    except Exception as e:
        print(f"ERROR: Connection failed: {e}")
        print("Make sure MySQL is running and credentials are correct")

if __name__ == '__main__':
    check_database()