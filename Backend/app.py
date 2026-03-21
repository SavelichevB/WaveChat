from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO, emit
from datetime import timedelta

from config import cookie_token
from models.auth import Auth
from models.message import GetMessage, PostMessage
from models.users import UserData

#Create app:
app = Flask(__name__)
app.config['SECRET_KEY'] = 'WaveMini'

#Cors:
CORS(app, 
     supports_credentials=True, 
     origins=["http://localhost:5173", "http://192.168.0.18:5173"],
     allow_headers=["Content-Type", "Authorization", "Cookie", "X-Requested-With"],
     expose_headers=["Set-Cookie"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
protocol = False  #HTTPS or HTTP, if HTTPS => true

#JWT Config:
app.config['JWT_SECRET_KEY'] = 'WaveMini'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
jwt = JWTManager(app)

#Objects:
auth = Auth()
gm = GetMessage()
pm = PostMessage()
ud = UserData()

#====Endpoints====: 
@app.route('/', methods=['GET'])
def Home():
 return jsonify({
   'service': 'WaveChat API',
   'status': 'online',
   'version': '1.0.0.0'
 }), 200  


#====Point==Auth=====:
@app.route('/auth/reg', methods=['POST'])
def registr_users():
  try:
    client_username = request.json.get('username')
    client_password = request.json.get('password')
    if not client_username or not client_password: return jsonify({'Info': 'Username or Password not found'}), 400

    data_reg, log = auth.Registation(client_username, client_password)
    if not data_reg: return jsonify({'Info': 'Username or Password incorrect for the registation', 'Log': log}), 400
    access_token = create_access_token(identity=str(log))
    if not access_token: return jsonify({'Info': 'Error app for regisration'}), 400

    response = make_response(jsonify({'Success': True}))
    response.set_cookie(
      'token',
      access_token,
      httponly=True,
      secure=protocol,
      samesite='Lax',
      max_age=timedelta(days=7),
      path='/',
      domain='localhost'
    )

    return response, 200
    
  except Exception as e:
    return jsonify({
      'Info': 'Error app for regisration'
    }), 500
  
@app.route('/auth/login', methods=['POST'])
def login_user():
  try:
    client_username = request.json.get('username')
    client_password = request.json.get('password')
    if not client_username or not client_password: return jsonify({'Info': 'Username or Password not found'}), 400

    data_reg, log = auth.Login(client_username, client_password)
    if not data_reg: return jsonify({'Info': 'Username or Password incorrect for the login', 'Log': log}), 400
    if int(log) < 0: return jsonify({'Info': 'Server Error for the login'})
    access_token = create_access_token(identity=str(log))
    if not access_token: return jsonify({'Info': 'Error app for login'}), 400

    response = make_response(jsonify({'Success': True}))
    response.set_cookie(
      'token',
      access_token,
      httponly=True,
      secure=protocol,
      samesite='Lax',
      max_age=timedelta(days=7),
      path='/',
      domain='localhost'
    )

    return response, 200

  except Exception as e:
    return jsonify({
      'Info': 'Error app for login'
    }), 500

@app.route('/auth/check', methods=['GET'])
@cookie_token
def verify_token():
  try:
    client_id = request.client_id
    if not client_id or int(client_id) < 0: return jsonify({'Info': 'Error verify token'}), 403
    return jsonify({'Success': True, 'Client_id': client_id}), 200
  except Exception as e:
    print(e)
    return jsonify({'Info': 'Fatal error verify token'}), 500

@app.route('/auth/logout', methods=['POST'])
def logout():
  try:
    if request.method == 'OPTIONS':
      return '', 200
    
    responce = make_response(jsonify({'Success': True}))
    responce.set_cookie(
      'token',
      '',
      httponly=True,
      secure=protocol,
      samesite='Lax',
      max_age=0,
      path='/',
      domain='localhost'      
    )
    return responce, 200
    
  except Exception as e:
    return jsonify({'Success': False, 'Info': 'Server Error logout'})

  
  
  
#====Point==Message====:

@app.route('/message/send/id', methods=['POST'])
@jwt_required()
def send_message():
  try:
    sender_id = get_jwt_identity()
    receiver_id = request.json.get('from')
    text = request.json.get('text')  

    check, log = pm.send_private_message(receiver_id, sender_id, text)  

    if not check: return jsonify({'Info': 'Error send message', 'Log': log}), 400

    return jsonify({
      'Success': True,
      'Info': 'Message was senden'
    }), 200
  
  except:
    return jsonify({'Info': 'Fatal error send message'}), 500

@app.route('/message/send/chat', methods=['POST'])
@jwt_required()
def send_message_chat():
  try:
     sender_id = get_jwt_identity()
     chat_id = request.json.get('chat_id')
     text = request.json.get('text')

     check, log = pm.send_chat_message(chat_id, sender_id, text)
     if not check: return jsonify({'Info': 'Error send message', 'Log': log}), 400
     if log == False: return jsonify({'Info': 'Error send message', 'Log': log}), 400

     return jsonify({
      'Success': True,
      'Info': 'Message was senden'
     }), 200
  except:
     return jsonify({'Info': 'Fatal error send message'}), 500
  
@app.route('/message/get', methods=['POST'])
@jwt_required()
def get_message():
  try:
    client_id = get_jwt_identity()
    chat_id = request.json.get('chat_id')

    check, data = gm.get_private_message(chat_id, client_id) 
    if not check: return jsonify({'Info': 'Error get messages'}), 400
    if not data: return jsonify({'Success': False}), 200

    return jsonify({
      'Success': True,
      'Data': data,
      'Count': len(data)
    }), 200
  except:
    return jsonify({'Info': 'Fatal error get message'}), 500
  
#====Point==Chats====:
@app.route('/chat/get', methods=['GET'])
@jwt_required()
def get_chat():
  try:
    client_id = get_jwt_identity()
    if not client_id: return jsonify({'Info': 'Forbidden'}), 403

    check, chats = gm.get_users_chats(client_id)
    if not check: return jsonify({'Info': 'Error Get user chats', 'Log': chats}), 400
    
    if not chats: return jsonify({'Success': True, 'Data': [], 'Count': 0}), 200
    return jsonify({
      'Success': True, 
      'Data': chats,
      'Count': len(chats)
    }), 200
  except:
    return jsonify({'Info': 'Fatal error get chats'}), 500
  
#====Point==User====:
@app.route('/users/me', methods=['GET'])
@jwt_required()
def get_users_me():
  try:
    client_id = get_jwt_identity()
    if not client_id: return jsonify({'Info': 'Forbidden'}), 403

    check, data = ud.get_all_data(client_id)
    if not check: return jsonify({'Info': 'Error Get user data', 'Log': data}), 400

    return jsonify({
      'Success': True, 
      'Data': data
    }), 200    
  except:
    return jsonify({'Info': 'Fatal error get chats'}), 500

@app.route('/users/get', methods=['POST'])
def get_users_open():
  try:
    client_id = request.json.get('id')
    if not client_id: return jsonify({'Info': 'Forbidden'}), 403

    check, data = ud.get_open_data(client_id)
    if not check: return jsonify({'Info': 'Error Get user data', 'Log': data}), 400

    return jsonify({
      'Success': True, 
      'Data': data
    }), 200    
  except:
    return jsonify({'Info': 'Fatal error get chats'}), 500

if __name__ == '__main__':
  app.run(debug=True, port=3333)