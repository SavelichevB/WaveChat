import pymysql
from pymysql.cursors import DictCursor

class GetDB: # -- Config Class DataBase
    def __init__(self):
        self.__dbdata = ['localhost', 'root', '', 'wavechat']
        self._con = None

    def host(self):
        return self.__dbdata[0]
    def user(self):
        return self.__dbdata[1]
    def password(self):
        return self.__dbdata[2]
    def name(self):
        return self.__dbdata[3]
    
class GetConnect(GetDB): # -- Get Connect to DataBase
    def connectDB(self):
        try:
           self._con = pymysql.connect(
               host=self.host(),
               user=self.user(),
               password=self.password(),
               database=self.name(),
               charset='utf8mb4',
               cursorclass=DictCursor
           )
           print("MySQL connected!")
           return self._con
        except Exception as e:
            print(f"Error Connect to DataBase: {e}")
            return None
    
    def query(self, sql, params=None): # -- Request to DataBase
        if not self._con:
            self.connectDB()
        with self._con.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()
        
    def close(self): # -- Close connect to DataBase
        if self._con:
            self._con.close()
            self._con = None
            print("MySQL Disconnected")
