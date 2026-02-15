from config import WorkData
from db import GetConnect

limit_message_chat = 1000 #Limit get message
limit_user_chats = 800 #Limit get chats

class GetMessage:
 def __init__(self):
    self.db = GetConnect()
    self.wd = WorkData()

 def get_private_chats(self, client_one, client_two): #Function for the GET PERSON CHATS 
   try:
     if not client_one or not client_two: return False, False

     chats_data = self.db.query('''SELECT rq1.chat_id
     FROM chat_participants rq1
     INNER JOIN chat_participants rq2 ON rq1.chat_id = rq2.chat_id
      WHERE rq1.user_id = %s AND
        rq2.user_id = %s AND
        rq1.user_id != rq2.user_id''', (client_one, client_two))
     
     if not chats_data or len(chats_data) < 1: return True, False

     return True, chats_data[0]['chat_id']
     
   except Exception as e:
     print(f"Error Get Private Chats -- {e}")
     return False, False
   
 def get_private_message(self, chat_id): #Function for the GET PERSON MESSAGES 
   try:
     if not chat_id: return False, "Error Chat_ID not found"

     chat_message = self.db.query('''SELECT id, from_id, text, time, is_read, is_edit
      FROM chat_message WHERE chat_id=%s 
      ORDER BY time DESC
      LIMIT %s''', (chat_id, limit_message_chat)) 
     if not chat_message: return True, False

     return True, chat_message
   except:
     return False, "Server Error"   
   
 def get_users_chats(self, client_id): #Function for the GET USER CHATS
   try:
     if not client_id: return False, "Client_ID not found"

     user_chats = self.db.query('''SELECT chat_id
       FROM chat_participants WHERE user_id=%s
        ORDER BY joined_at DESC
        LIMIT %s''', (client_id, limit_user_chats))
     if not user_chats or len(user_chats) < 1: return True, []

     return True, user_chats
   except:
     return False, "Server Error"
   
 def get_client_messages(self, client_one, client_two):
   try:
     if not client_one or not client_two: return False

     log, chat_id = self.get_private_chats(client_one, client_two)
     if log == False or chat_id == False: return False
     chat_id = int(chat_id)

     log, messages = self.get_private_message(chat_id)
     if log == False: return False
     if messages == False: return []
     return messages
   except:
     return False


class PostMessage(GetMessage):
  def __init__(self):
    self.db = GetConnect()
    self.wd = WorkData()

  def send_private_message(self, from_id, whom_id):
    None
