from uvicorn import run
from starlette.applications import Starlette
from starlette.responses import Response, JSONResponse
from starlette.routing import Route


class WebApi():

    def __init__(self):
        self.__routes = []

    def start(self, host, port):
        app = Starlette(routes=self.__routes)
        run(app, host=host, port=int(port))

    def expose(self, function):
        name = function.__name__

        route = Route(f'/{name}', self.wrap(function), methods=['POST'])
        self.__routes.append(route)
        
        return function
        
    def wrap(self, function):
        async def wrapper(request):
            payload = await request.json()
            result, status = await function(payload)

            if result is not None:
                return JSONResponse(result, status_code=status)
            else:
                return Response(status_code=status)

        return wrapper


webapi = WebApi()