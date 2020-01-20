from uvicorn import run
from starlette.applications import Starlette


class WebApi():

    def __init__(self):
        self.__app = Starlette()

    def start(self, host, port):
        run(service, host=host, port=int(port), workers=2)

    
