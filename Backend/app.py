from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO, emit
from datetime import timedelta
from models.auth import Auth

#Create app:
app = Flask(__name__)
app.config['SECRET_KEY'] = 'WaveMini'

#JWT Config:
app.config['JWT_SECRET_KEY'] = 'WaveMini'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=30)
jwt = JWTManager(app)

#Objects:
auth = Auth()

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
    return jsonify({
      'Success': True,
      'Token': access_token
      }), 200
    
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

    return jsonify({
      'Success': True,
      'Token': access_token      
    }), 200

  except Exception as e:
    return jsonify({
      'Info': 'Error app for login'
    }), 500

@app.route('/auth/check', methods=['GET'])
@jwt_required()
def verify_token():
  try:
    client_id = get_jwt_identity()
    if not client_id or int(client_id) < 0: return jsonify({'Info': 'Error verify token'}), 403
    return jsonify({'Success': True, 'Client_id': client_id}), 200
  except Exception as e:
    print(e)
    return jsonify({'Info': 'Fatal error verify token'}), 403
  
#====Point==Message====:



if __name__ == '__main__':
  app.run(debug=True, port=3333)