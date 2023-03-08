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
    leave_room,
    join_room,
    send,

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
        if join != False:
            if not code:
                return render_template('home.html',
                                       error="Please enter a room code", code=code, name=name)
            elif code not in rooms:
                return render_template('home.html',
                                       error="Room does not exists", code=code, name=name)

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
    room = session.get('room')
    # user can't directly go to the /room route, first he needs to visit /home
    if room is None or session.get('name') is None or room not in rooms:
        return redirect(url_for('home'))

    return render_template('room.html', room=room, messages=rooms[room]["messages"])


@socketio.on('message')
def message(data):
    room = session.get("room")
    if room not in rooms:
        return redirect(url_for('home'))

    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")


@socketio.on("connect")
def connect(auth):
    room = session.get('room')
    name = session.get('name')
    if not room or not name:
        return redirect(url_for('home'))
    if room not in rooms:
        leave_room(room)
        return redirect(url_for('home'))

    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f'{name} joined room {room}')


@socketio.on("disconnect")
def disconnect():
    room = session.get('room')
    name = session.get('name')
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]

    send({"name": name, "message": "has left the room"}, to=room)
    print(f'{name} has left the room {room}')


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5050)
