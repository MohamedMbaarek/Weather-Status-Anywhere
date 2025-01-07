import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost", 
        database="Weather",  
        user="postgres",  
        port=5432
    )
    return conn