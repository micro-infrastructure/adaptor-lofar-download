from os import getenv
from loguru import logger
from endpoints import *
from persistence import *
from runtimes import ticker, pubsub, webapi


AMQP_ADDRESS = getenv('AMQP_ADDRESS', default=None)
CALLBACK_URL = getenv('LOFARDOWNLOAD_SERVICE')
HOST = getenv('HOST', default='0.0.0.0')
PORT = getenv('PORT', default=8090)
TICK_INTERVAL = getenv('TICK_INTERVAL', default=5)


if __name__ == '__main__':
    logger.debug(f'AMQP address is: {AMQP_ADDRESS}')
    logger.debug(f'Host is: {HOST}')
    logger.debug(f'Port is: {PORT}')
    logger.debug(f'Tick interval is: {TICK_INTERVAL} minutes')
    logger.debug(f'Callback URL is: {CALLBACK_URL}')

    if CALLBACK_URL is None:
        print('Please set the LOFARDOWNLOAD_SERVICE (callback URL) environment variable.')
        exit(1)

    ticker.start(TICK_INTERVAL, HOST, PORT)
    pubsub.start(AMQP_ADDRESS)
    webapi.start(HOST, PORT)

    exit(0)
