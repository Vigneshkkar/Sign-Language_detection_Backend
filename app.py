from flaskr.__init__ import create_app
# from flaskr.api.socket import init_socket

import os
import configparser
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory

_users_in_room = {} # stores room wise user list
_room_of_sid = {} # stores room joined by an used
_name_of_sid = {} # stores display name of users

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join("config.ini")))


app = create_app()
cors = CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
# socketio = SocketIO(app)
# socketio.init_app(app, cors_allowed_origins="*")

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['DEBUG'] = True
try:
    if os.environ['MODE'] == 'Production':
        app.config['MONGO_URI'] = config['PROD']['DB_URI']
    else:
        app.config['MONGO_URI'] = config['TEST']['DB_URI']
except:
    app.config['MONGO_URI'] = config['TEST']['DB_URI']

    
    



@socketio.on("connect")
def on_connect():
    sid = request.sid
    print("New socket connected ", sid)
    

@socketio.on("join-room")
def on_join_room(data):
    sid = request.sid
    room_id = data["room_id"]
    display_name =  data["display_name"] #session[room_id]["name"]
    
    # register sid to the room
    join_room(room_id)
    _room_of_sid[sid] = room_id
    _name_of_sid[sid] = display_name
    
    # broadcast to others in the room
    print("[{}] New member joined: {}<{}>".format(room_id, display_name, sid))
    emit("user-connect", {"sid": sid, "name": display_name}, broadcast=True, include_self=False, room=room_id)
    
    # add to user list maintained on server
    if room_id not in _users_in_room:
        _users_in_room[room_id] = [sid]
        emit("user-list", {"my_id": sid}) # send own id only
    else:
        usrlist = {u_id:_name_of_sid[u_id] for u_id in _users_in_room[room_id]}
        emit("user-list", {"list": usrlist, "my_id": sid}) # send list of existing users to the new member
        _users_in_room[room_id].append(sid) # add new member to user list maintained on server

    print("\nusers: ", _users_in_room, "\n")


@socketio.on("disconnect")
def on_disconnect():
    sid = request.sid
    room_id = _room_of_sid[sid]
    display_name = _name_of_sid[sid]

    print("[{}] Member left: {}<{}>".format(room_id, display_name, sid))
    emit("user-disconnect", {"sid": sid}, broadcast=True, include_self=False, room=room_id)

    _users_in_room[room_id].remove(sid)
    if len(_users_in_room[room_id]) == 0:
        _users_in_room.pop(room_id)

    _room_of_sid.pop(sid)
    _name_of_sid.pop(sid)

    print("\nusers: ", _users_in_room, "\n")


@socketio.on("data")
def on_data(data):
    sender_sid = data['sender_id']
    target_sid = data['target_id']
    if sender_sid != request.sid:
        print("[Not supposed to happen!] request.sid and sender_id don't match!!!")

    if data["type"] != "new-ice-candidate":
        print('{} message from {} to {}'.format(data["type"], sender_sid, target_sid))
    socketio.emit('data', data, room=target_sid)

@socketio.on("broadcast-predicted")
def on_broadcast_predicted(data):
    sid = request.sid
    room_id = _room_of_sid[sid]
    display_name = _name_of_sid[sid]

    emit("get-predicted", data, broadcast=True, include_self=False, room=room_id)

if __name__ == "__main__":
    
    socketio.run(app, debug=True)