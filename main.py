from random import choice
from string import ascii_uppercase

from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
)
from flask_socketio import (
    SocketIO,
)

app = Flask(__name__)
# SECRET_KEY created with token_hex(16) function from secrets module
app.config["SECRET_KEY"] = "'1ca02e4e5824a74c78c4fe56f9f62442'"
socketio = SocketIO(app)

rooms = {}


def generate_unique_code(length: int):
    while True:
        code = ""
        for _ in range(length):
            code += choice(ascii_uppercase)

        if code not in rooms:
            break

    return code


@app.route('/', methods=['POST', 'GET'])
@app.route('/home', methods=['POST', 'GET'])
def home():
    session.clear()
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        join = request.form.get('join', False)
        create = request.form.get('create', False)

        if not name:
            return render_template('home.html',
                                   error="Please enter a name", code=code, name=name)
        if join != False and not code:
            return render_template('home.html',
                                   error="Please enter a room code", code=code, name=name)
        if code not in rooms:
            return render_template('home.html',
                                   error="Room does not exists", code=code, name=name)
        # for case were create is equal to False
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        # if we're not creating new room, variable room will be equal to code - the code of existing room

        # in this small project we'll just store data in a session
        session["room"] = room
        session["name"] = name
        return redirect(url_for('room'))

    return render_template('home.html')


@app.route('/room')
def room():
    render_template('room.html')


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5050)
