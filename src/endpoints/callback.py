from http import HTTPStatus
from datetime import datetime

from persistence import Attempt, Job, Partition
from runtimes import pubsub, webapi


@pubsub.expose
@webapi.expose
async def callback(payload):
    identifier, job, status, subject = unpack_command(payload)
    job = await Job.objects.filter(identifier=job).get()

    if subject == 'job':
        if status == 'started':
            await job.update(status=status, started=datetime.now())

        if status == 'stopped':
            await job.update(status=status, xenon_state='COMPLETED', stopped=datetime.now())

    if subject == 'partition':
        partition = await Partition.objects.filter(identifier=identifier).get()

        if status == 'started':
            if partition.status == 'created':
                await partition.update(status='started', started=datetime.now())

            # Update previous attempts to failed, if exists
            existing_attemps = await Attempt.objects.filter(job=job, partition=partition).all()
            for attempt in existing_attemps:
                await attempt.update(status='failed', stopped=datetime.now())

            # Create new attempt
            await Attempt.objects.create(job=job, partition=partition)

        # Othwerise, status is 'complete' or 'failed'
        else:
            if status == 'complete':
                await partition.update(status='complete', stopped=datetime.now())
 
            attempt = await (Attempt.objects
                .filter(job=job, partition=partition, status='started')
                .get())

            await attempt.update(status='stopped', stopped=datetime.now())

    return (None, HTTPStatus.ACCEPTED)


def unpack_command(payload):
    identifier = payload['identifier']
    job = payload['job']
    status = payload['status']
    subject = payload['subject']

    return (identifier, job, status, subject)    