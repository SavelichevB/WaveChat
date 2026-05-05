import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB

class GetConnect:
    _pool = None
    
    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            cls._pool = PooledDB(
                creator=pymysql,
                maxconnections=20,  
                mincached=5,           
                maxcached=10,          
                blocking=True,        
                ping=1,                
                host='localhost',
                user='root',
                password='',
                database='wave_chat',
                charset='utf8mb4',
                cursorclass=DictCursor,
                autocommit=True
            )
            print("✅ MySQL Start")
        return cls._pool
    
    def query(self, sql, params=None):
        conn = self.get_pool().connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                return cursor.fetchall()
        finally:
            conn.close()  # Возвращает в пул
    
    def execute(self, sql, params=None):
        conn = self.get_pool().connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                conn.commit()
                return cursor.lastrowid or True
        finally:
            conn.close()