#!/usr/bin/env python3
import bottle

app = bottle.Bottle()

room_config = {
    '1F': {
        'floor': 1,
        'room_name': '休憩エリア'
    },
    '2F': {
        'floor': 2,
        'room_name': '2階の食堂',
        'room_img': '/shokudo01-1.png',
    },
    '3F-A': {
        'floor': 3,
        'room_name': '3階のA食堂',
    },
    '3F-B': {
        'floor': 3,
        'room_name': '3階のB食堂',
    },
    '4F-A': {
        'floor': 4,
        'room_name': '4階のA食堂',
    },
}


@app.get('/status/<room_id>.html')
def show_room(room_id: str):
    if room_id in room_config:
        return bottle.jinja2_template('room-status.html', **room_config[room_id])
    return bottle.abort(404, 'Not Found')


@app.get('/')
@app.get('/<filepath>')
def static(filepath: str = 'index.html'):
    return bottle.static_file(filepath, root='./static/')


app.run(host='localhost', port=8080)
