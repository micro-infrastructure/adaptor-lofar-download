from http import HTTPStatus
from datetime import datetime

from persistence import Attempt, Job, Partition
from runtimes import pubsub, webapi
from scheduling import schedule


@pubsub.expose
@webapi.expose
async def callback(payload):
    identifier, job, status, subject = unpack_command(payload)
    job = await Job.objects.get(identifier=job)

    if subject == 'job':
        if status == 'started':
            await job.update(status=status, started=datetime.now())

        if status == 'stopped':
            await job.update(status=status, stopped=datetime.now())

    if subject == 'partition':
        partition = await Partition.get(identifier=identifier)

        if status == 'started':
            await Attempt.objects.create(job=job, partition=partition)
        else:
            attempt = await Attempt.get(identifier=identifier)
            await attempt.update(status=status, stopped=datetime.now())

    return (None, HTTPStatus.ACCEPTED)


def unpack_command(payload):
    identifier = payload['identifier']
    job = payload['job']
    status = payload['status']
    subject = payload['subject']

    return (identifier, job, status, subject)    