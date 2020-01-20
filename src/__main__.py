
from endpoints import *
from persistence import *
from runtimes import pubsub, webapi


AMQP_ADDRESS = getenv('AMQP_ADDRESS', default=None)
HOST = getenv('HOST', default='0.0.0.0')
PORT = getenv('PORT', default=8090)


if __name__ == '__main__':
    pubsub.start(AMQP_ADDRESS)
    webapi.start(HOST, PORT)

    exit(0)