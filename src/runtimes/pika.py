from os import getenv
from threading import Thread

from loguru import logger
from pika import BlockingConnection, ConnectionParameters


class PubSub():

    def __init__(self, exchange, routing_key):
        self.exchange = exchange
        self.routing_key = routing_key

        self.__functions = {}

    def start(self, amqp_host):
        if amqp_host is None:
            return

        connection = BlockingConnection(ConnectionParameters(host=amqp_host))
        channel = connection.channel()
        channel.exchange_declare(self.exchange, 'topic')

        result = channel.queue_declare(queue='', exclusive=True)
        queue = result.method.queue
        channel.queue_bind(queue, self.exchange, self.routing_key)

        def callback(_ch, method, properties, message):
            logger.debug(f'Incoming AMQP message: {message}.')

            message = loads(message)
            function_name = method.routing_key.split('.')[-1]

            function = self.__functions[function_name]
            result, status = function(message['payload'])

            # Reply to sender over message queue
            reply = dumps({
                'id': message['id'],
                'status': status,
                'payload': result,
            })
            channel.basic_publish(self.exchange, message['replyTo'], reply)

        channel.basic_consume(queue, callback, auto_ack=True)
        Thread(target=channel.start_consuming).start()

    def expose(self, reference):
        name = reference.__name__
        self.__functions[name] = reference

        return reference    


pubsub = PubSub('function_proxy', 'functions.lofar-download.*')
