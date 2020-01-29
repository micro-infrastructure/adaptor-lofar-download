from apscheduler.schedulers.background import BackgroundScheduler
from requests import post

class Ticker():

    def __init__(self):
        self.__scheduler = BackgroundScheduler()

    def start(self, interval, host, port):
        self.__scheduler.add_job(Ticker.tick, 'interval', args=(host, port), minutes=int(interval))
        self.__scheduler.start()

    @staticmethod
    def tick(host, port):
        post(f'http://{host}:{port}/tick')
    

ticker = Ticker()
