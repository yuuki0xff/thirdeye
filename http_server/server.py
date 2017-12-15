#!/usr/bin/env python3
import gevent.monkey

gevent.monkey.patch_all()

import os
import sys
import tempfile

import bottle
import yaml

app = bottle.Bottle()

room_config = {}
senders = {}


def load_config():
    global room_config
    global senders

    try:
        config_file = os.environ['THIRD_EYE_CONFIG']
    except KeyError:
        print('Should set the "THIRD_EYE_CONFIG" environment value', file=sys.stderr)
        sys.exit(1)

    with open(config_file, 'r') as f:
        config = yaml.load(f)
    room_config = config['room_config']
    senders = config['senders']


load_config()


def has_auth(sender_id: str, sender_secret: str) -> bool:
    try:
        sender = senders[sender_id]
        return sender['secret'] == sender_secret
    except KeyError:
        return False


class ImageStore:
    def __init__(self, root_dir: str):
        self._root = root_dir
        try:
            os.mkdir(self._root, 0o700)
        except FileExistsError:
            # ディレクトリが存在していた
            pass

    def _get_filepath(self, sender_id: int, camera_id: int) -> str:
        basename = '{}_{}.png'.format(int(sender_id), int(camera_id))
        filepath = os.path.join(self._root, basename)
        return filepath

    def get(self, sender_id: int, camera_id: int) -> bytes:
        fpath = self._get_filepath(sender_id, camera_id)
        with open(fpath, 'rb') as f:
            return f.read()

    def set(self, sender_id: int, camera_id: int, data: bytes):
        """
        既存の画像を新しい画像で置き換える。古い画像は "~.png.old" という名前で保存される。

        sender_id, camera_idが同じ画像に対して同時に更新を行うと、最新の画像と古いファイルの内容は不定。
        しかし、保存されている画像が破損することはない。
        """
        fpath = self._get_filepath(sender_id, camera_id)
        _, tmpfpath = tempfile.mkstemp(prefix=os.path.basename(fpath) + '.tmp', dir=self._root)
        oldfpath = fpath + '.old'

        with open(tmpfpath, 'wb') as f:
            f.write(data)

        try:
            os.unlink(oldfpath)
        except FileNotFoundError:
            # 1回目と2回目の更新では、oldfpathが存在しない。
            pass

        try:
            os.link(fpath, oldfpath)
        except FileNotFoundError:
            # 1回目の更新では、fpathが存在しない
            pass
        except FileExistsError:
            # oldfpathが存在した。レースコンディション発生？
            # fpathの中身が、更新処理中の複数の画像のどれになるのか予測がつかない。
            # しかし、実害はないので処理を続行。
            pass
        os.rename(tmpfpath, fpath)


images = ImageStore('/var/tmp/thirdeye-images')


@app.get('/status/<room_id>.html')
def show_room(room_id: str):
    if room_id in room_config:
        return bottle.jinja2_template('room-status.html', **room_config[room_id])
    return bottle.abort(404, 'Not Found')


@app.get('/')
@app.get('/<filepath>')
@app.get('/<filepath:re:img/.*\.jpg>')
def static(filepath: str = 'index.html'):
    return bottle.static_file(filepath, root='./static/')


@app.get('/images/<sender_id:int>/cameras/<camera_id:int>.png')
def show_image(sender_id: int, camera_id: int):
    try:
        img = images.get(sender_id, camera_id)
        res = bottle.HTTPResponse(status=200, body=img)
        res.content_type = 'image/png'
        return res
    except FileNotFoundError:
        return bottle.HTTPResponse(status=404)


@app.put('/images/<sender_id:int>/cameras/<camera_id:int>.png')
def update_image(sender_id: int, camera_id: int):
    """ 画像を更新する。

    :param sender_id:
    :param camera_id:
    :return:
    """
    if str(sender_id) != bottle.request.headers.get('X-ThirdEye-Photo-Sender-ID'):
        return bottle.HTTPResponse(status=400, body='SenderID mismatch')

    sender_secret = bottle.request.headers.get('X-ThirdEye-Photo-Sender-Secret')
    if not has_auth(str(sender_id), sender_secret):
        return bottle.HTTPResponse(status=401, body='SenderID or Secret incorrect')

    img = bottle.request.body.read()
    images.set(sender_id, camera_id, img)
    return bottle.HTTPResponse(status=204)


app.run(host='0.0.0.0', port=8080, server='gevent')
