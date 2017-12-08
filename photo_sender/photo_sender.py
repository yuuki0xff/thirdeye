#!/usr/bin/env python2
import os
import time
import traceback
import logging as _logging
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

    ret, buf = cv2.imencode('.png', img)
    if not ret:
        raise EncodeError()
    return bytes(buf)


def send_photo(api, client_id, client_secret, buf):
    for i in range(10):
        try:
            ret = requests.post(api, data=buf, auth=(client_id, client_secret))
            if ret.ok:
                return
            raise SendError(ret.reason)
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
        client_id = os.environ['PHOTO_SENDER_CLIENT_ID']
        client_secret = os.environ['PHOTO_SENDER_CLIENT_SECRET']

        logger.debug('interval = {}'.format(interval))
        logger.debug('api = {}'.format(api))
        logger.debug('client_id = {}'.format(client_id))
        logger.debug('client_secret = {}'.format(client_secret))
        logger.debug('Configuration loaded')
    except KeyError as e:
        key_name = e.args[0]
        logger.critical('Should set the environment value named {}'.format(key_name))
        return 1
    is_first = True

    while True:
        try:
            if not is_first:
                logger.debug('Sleeping {}sec'.format(interval))
                time.sleep(interval)
            is_first = False

            logger.debug('Getting a camera device')
            camera = cv2.VideoCapture(0)
            try:
                logger.debug('Capturing a photo')
                buf = get_photo(camera)

                logger.debug('Sending a photo')
                send_photo(api, client_id, client_secret, buf)
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
