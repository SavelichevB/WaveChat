from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)

socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('i.html')

@socketio.on('connect')
def load():
    print("Пользователь подключился к сокету")

@socketio.on('message')
def send_message(msg):
    print(f"Новое сообщение: {msg}")
    emit('message', msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=2100)