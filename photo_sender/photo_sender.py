#!/usr/bin/env python2
import logging as _logging
import os
import time
import traceback

import cv2
import requests

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s:%(filename)s:%(lineno)d %(msg)s'
_logging.basicConfig(format=LOG_FORMAT)
logger = _logging.getLogger(__name__)


class Error(Exception): pass


class ReadError(Error): pass


class EncodeError(Error): pass


class SendError(Error): pass


def get_photo(camera):
    ret, img = camera.read()
    if not ret:
        raise ReadError()

    # type(buf) will be numpy array
    ret, buf = cv2.imencode('.png', img)
    if not ret:
        raise EncodeError()
    return bytes(buf.tostring())


def send_photo(session, url, buf):
    for i in range(10):
        try:
            ret = session.put(url, data=buf)
            if ret.ok:
                return
            raise SendError(ret.status_code, ret.reason, ret.text)
        except Exception:
            logger.error('Failed to send a photo: {}'.format(traceback.format_exc()))

        time.sleep(10)
    raise SendError('Failed to send a photo')


def main():
    logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))
    logger.info('Starting photo sender')

    logger.debug('Loading configuration')
    try:
        interval = int(os.environ.get('PHOTO_SENDER_INTERVAL', '60'))
        api = os.environ['PHOTO_SENDER_API']
        sender_id = int(os.environ['PHOTO_SENDER_ID'])
        camera_id = int(os.environ['PHOTO_CAMERA_ID'])
        sender_secret = os.environ['PHOTO_SENDER_SECRET']

        logger.debug('interval = {}'.format(interval))
        logger.debug('api = {}'.format(api))
        logger.debug('sender_id = {}'.format(sender_id))
        logger.debug('camera_id = {}'.format(camera_id))
        logger.debug('secret = {}'.format(sender_secret))
        logger.debug('Configuration loaded')
    except KeyError as e:
        key_name = e.args[0]
        logger.critical('Should set the environment value named {}'.format(key_name))
        return 1

    session = requests.Session()
    session.headers.update({
        'X-ThirdEye-Photo-Sender-ID': sender_id,
        'X-ThirdEye-Photo-Sender-Secret': sender_secret,
    })
    url = '{base_url}/images/{sender_id}/cameras/{camera_id}.png'.format(
        base_url=api,
        sender_id=sender_id,
        camera_id=camera_id,
    )

    is_first = True
    while True:
        try:
            if not is_first:
                logger.debug('Sleeping {}sec'.format(interval))
                time.sleep(interval)
            is_first = False

            logger.debug('Getting a camera device')
            camera = cv2.VideoCapture(camera_id)
            try:
                logger.debug('Capturing a photo')
                buf = get_photo(camera)

                logger.debug('Sending a photo')
                send_photo(session, url, buf)
            finally:
                camera.release()
            logger.info('Sended a photo')
        except KeyboardInterrupt:
            return 0
        except Exception:
            logger.debug('Releasing a camera device')
            logger.error(traceback.format_exc())


if __name__ == '__main__':
    exit(main())
