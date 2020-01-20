from http import HTTPStatus

from starlette.responses import Response, JsonResponse

from runtimes import webapi

@webapi.route('/copy', methods=['POST'])
async def wrapper(request):
    payload = await request.json()
    result, status = copy(payload)

    if result is not None:
        return JsonResponse(result, status_code=status)
    else:
        return Response(status_code=status)

@pubsub.expose
async def copy(payload):
    return (None, HTTPStatus.NOT_IMPLEMENTED)