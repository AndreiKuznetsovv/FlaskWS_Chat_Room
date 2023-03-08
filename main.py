from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
)
from flask_socketio import (
    join_room,
    leave_room,
    send,
    SocketIO,
)
from string import ascii_uppercase
import random

app = Flask(__name__)
# SECRET_KEY created with token_hex(16) function from secrets module
app.config["SECRET_KEY"] = "'1ca02e4e5824a74c78c4fe56f9f62442'"
socketio = SocketIO(app)

@app.route('/', methods=['POST','GET'])
@app.route('/home', methods=['POST','GET'])
def home():
    return render_template('home.html')


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5050)