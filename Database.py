import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        database="weatherdb",  
        user="root",         
        port=3306            
    )
    return conn