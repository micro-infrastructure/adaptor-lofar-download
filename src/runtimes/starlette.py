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

        route = Route(f'/{name}', self.wrap_post(function), methods=['POST'])
        self.__routes.append(route)
        
        return function
    
    def expose_get(self, path):
        def outer(function):
            name = function.__name__

            route = Route(path, self.wrap_get(function), methods=['GET'])
            self.__routes.append(route)
            
            return function

        return outer

    def wrap_get(self, function):
        async def wrapper(request):
            result, status = await function(request.path_params)

            if result is not None:
                return JSONResponse(result, status_code=status)
            else:
                return Response(status_code=status)

        return wrapper  

    def wrap_post(self, function):
        async def wrapper(request):
            body = await request.body()
            if len(body) > 0:
                payload = await request.json()
            else:
                payload = {}

            result, status = await function(payload)

            if result is not None:
                return JSONResponse(result, status_code=status)
            else:
                return Response(status_code=status)

        return wrapper


webapi = WebApi()

def decorator_function_with_arguments(arg1, arg2, arg3):
    def wrap(f):
        print("Inside wrap()")
        def wrapped_f(*args):
            print("Inside wrapped_f()")
            print("Decorator arguments:", arg1, arg2, arg3)
            f(*args)
            print("After f(*args)")
        return wrapped_f
    return wrap