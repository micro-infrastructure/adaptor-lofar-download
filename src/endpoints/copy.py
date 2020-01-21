from http import HTTPStatus

from runtimes import pubsub, webapi

@pubsub.expose
@webapi.expose
async def copy(payload):
    return (None, HTTPStatus.NOT_IMPLEMENTED)