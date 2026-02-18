from config import WorkData
from db import GetConnect
from encryption.encrypt import Encrypt

limit_message_chat = 1000 #Limit get message
limit_user_chats = 800 #Limit get chats

class GetMessage:
 def __init__(self):
    self.db = GetConnect()
    self.wd = WorkData()
    self.em = Encrypt()

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
      ORDER BY time ASC
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
   
 def get_client_messages(self, client_one, client_two): #Function for the GET MESSAGES
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
   
 def check_user_chat(self, client_id, chat_id):
   try:
     if not client_id or not chat_id: return False
     check = self.db.query('''SELECT 1
     FROM chat_participants WHERE chat_id=%s AND user_id=%s''', (chat_id, client_id))
     if not check: return False
     return True
   except:
     return False
    

class PostMessage(GetMessage):
  def __init__(self):
    super().__init__()

  def send_chat_message(self, chat_id, client_id, text):
    try:
       if not client_id or not chat_id or not text: return False, "ID or TEXT not found"

       if self.check_user_chat(client_id, chat_id) == False: return False, "Client not found in chat"

       encrypt_text = self.em.encrypt_message(text)
       if not encrypt_text: return False, 'Encryption Error'

       send_data = self.db.execute('''INSERT INTO chat_message
       (chat_id, from_id, text) VALUES (%s, %s, %s)''', (chat_id, client_id, encrypt_text))
       if not send_data: True, False

       return True, send_data
    except Exception as e:
      return False, 'Server Error'
    
  def create_private_chat(self, client_one, client_two):
    try:
      if not client_one or not client_two: return False, "Client One/Two not found"

      log, chat_id = self.get_private_chats(client_one, client_two)
      if log == False: return False, "Server Error"
      if chat_id != False: return False, "Chat was already created"

      new_chat_id = self.db.execute('''INSERT INTO chats 
        (type) VALUES (%s)''', (0,))
      
      if not new_chat_id: return False, "Server Error" 
      new_client = self.db.execute('''INSERT INTO chat_participants 
        (chat_id, user_id) VALUES (%s, %s)''', (new_chat_id, client_one))
      if not new_client: return False, "Server Error"
      new_client = self.db.execute('''INSERT INTO chat_participants 
        (chat_id, user_id) VALUES (%s, %s)''', (new_chat_id, client_two))
      if not new_client: return False, "Server Error"  

      return True, new_chat_id 
    except:
      return False, 'Server Error'

  def send_private_message(self, receiver_id, sender_id, text):
    try:
      if not receiver_id or not sender_id or not text: return False, "ID or TEXT not found"

      log, chat_id = self.get_private_chats(receiver_id, sender_id)
      if log == False: return False, "Server Error"

      if chat_id == False: 
        new_chat, chat_id = self.create_private_chat(receiver_id, sender_id)
        if not new_chat: return False, "Server Error"
        if not chat_id: return False, "Chat ID not found"
        chat_id = int(chat_id)

      res, log =  self.send_chat_message(chat_id, sender_id, text)
      if not res: return False, log

      return True, "Very Good"

    except Exception as e:
      return False, "Server Error"
