from http import HTTPStatus
from datetime import datetime
from loguru import logger
from orm.exceptions import NoMatch
from persistence import Download, Job, Partition, Transfer
from runtimes import pubsub, webapi
from scheduling import create_credential, create_scheduler, get_xenon_state, create_job

from starlette.background import BackgroundTask


@webapi.expose_get('/status/{identifier:int}')
async def cancel(payload):
    identifier = payload['identifier']

    try:
        download = await Download.objects.filter(identifier=identifier).get()
    except:
        return (None, HTTPStatus.BAD_REQUEST)

    result = {
        'identifier': download.identifier,
        'name': download.name,
        'status': download.status,
        'started': str(download.started),
        'stopped': str(download.stopped),
        'partitions': [{
            'identifier': p.identifier,
            'status': p.status,
            'started': str(p.started),
            'stopped': str(p.stopped),
            'transfers': [
                t.filename for t in await Transfer.objects.filter(partition=p).all()
            ]
        } for p in sorted(await
            (Partition
                .objects
                .filter(download=download)
                .all()),
            key=lambda partition: partition.status, reverse=True)
        ]
    }

    return (result, HTTPStatus.OK)
