from http import HTTPStatus
from datetime import datetime
from loguru import logger
from orm.exceptions import NoMatch
from persistence import Download, Job, Partition
from runtimes import pubsub, webapi
from scheduling import create_credential, create_scheduler, get_xenon_state, create_job

from starlette.background import BackgroundTask


@pubsub.expose
@webapi.expose
async def cancel(payload):
    identifier = payload['identifier']

    download = await Download.objects.filter(identifier=identifier).get()
    await download.update(status='canceled', stopped=datetime.now())

    jobs = Job.objects.filter(download=download).all()
    for job in jobs:
        if job.status != 'stopped':
            scheduler = create_scheduler(
                hostname=download.target_hostname,
                credential=create_credential(
                    username=download.target_username, 
                    password=download.target_password
                )
            )

            cancel_job(job.xenon_id, scheduler)

    return (None, HTTPStatus.OK)