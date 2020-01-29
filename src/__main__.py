from os import getenv

from endpoints import *
from persistence import *
from runtimes import ticker, pubsub, webapi


AMQP_ADDRESS = getenv('AMQP_ADDRESS', default=None)
HOST = getenv('HOST', default='0.0.0.0')
PORT = getenv('PORT', default=8090)
TICK_INTERVAL = getenv('TICK_INTERVAL', default=5)


if __name__ == '__main__':
    callback_url = getenv('LOFARDOWNLOAD_SERVICE')
    if callback_url is None:
        print('Please set the LOFARDOWNLOAD_SERVICE (external URL) environment variable.')
        exit(1)

    ticker.start(TICK_INTERVAL, HOST, PORT)
    pubsub.start(AMQP_ADDRESS)
    webapi.start(HOST, PORT)

    exit(0)