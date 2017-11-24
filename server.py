#!/usr/bin/env python3
import bottle

app = bottle.Bottle()

room_config = {
    '1F': {
        'floor': 1,
        'room_name': '休憩エリア',
        'free_space_img': '/img/1F_free_space.jpg',
    },
    '2F': {
        'floor': 2,
        'room_name': 'ROSE cafe',
        'inside_img': '/img/2F_inside.jpg',
        'counter_img': '/img/2F_counter.jpg',
        'ticket_counter_img': '/img/2F_ticket.jpg',
    },
    '3F-A': {
        'floor': 3,
        'room_name': 'スエヒロ',
        'inside_img': '/img/3F_A_inside.jpg',
        'counter_img': '/img/3F_A_counter.jpg',
        'ticket_counter_img': '/img/3F_A_ticket.jpg',
    },
    '3F-B': {
        'floor': 3,
        'room_name': '',
        'inside_img': '/img/3F_B_inside.jpg',
        'counter_img': '/img/3F_B_counter.jpg',
        'ticket_counter_img': '/img/3F_B_ticket.jpg',
    },
    '4F-C': {
        'floor': 4,
        'room_name': 'C食堂',
        'inside_img': '/img/4F_C_inside1.jpg',
        'inside2_img': '/img/4F_C_inside2.jpg',
        'counter_img': '/img/4F_C_counter.jpg',
        'ticket_counter_img': '/img/4F_C_ticket.jpg',
    },
    '4F-D': {
        'floor': 4,
        'room_name': 'D食堂',
        'inside_img': '/img/4F_D_inside1.jpg',
        'inside2_img': '/img/4F_D_inside2.jpg',
        'counter_img': '/img/4F_D_counter.jpg',
        'ticket_counter_img': '/img/4F_D_ticket.jpg',
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


app.run(host='0.0.0.0', port=8080)
