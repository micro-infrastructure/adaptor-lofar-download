from http import HTTPStatus
from datetime import datetime

from orm.exceptions import NoMatch
from persistence import Download, Job
from runtimes import pubsub, webapi
from scheduling import create_credential, create_scheduler, get_xenon_state, create_job

from starlette.background import BackgroundTask


@pubsub.expose
@webapi.expose
async def tick(payload):
    await review_downloads()

    return (None, HTTPStatus.ACCEPTED)


async def review_downloads():
    downloads = await Download.objects.filter(status='started').all()
    
    for download in downloads:
        scheduler = create_scheduler(
            hostname=download.target_hostname,
            credential=create_credential(
                username=download.target_username, 
                password=download.target_password
            )
        )

        print('Updating jobs...')
        await update_jobs(download, scheduler)
        
        # Get active job
        try:
            await Job.objects.filter(
                download=download,
                status__in=['created', 'started']
            ).get()
        except NoMatch:
            print('No active jobs!')
            await create_job(download)


async def update_jobs(download, scheduler):
    jobs = await Job.objects.filter(
        download=download, 
        status__in=['created', 'started']
    ).all()

    for job in jobs:
        if job.xenon_id is None:
            continue

        state = get_xenon_state(job.xenon_id, scheduler)
        await job.update(xenon_state=state, updated=datetime.now())

        if state in ['CANCELLED', 'COMPLETED', 'FAILED']:
            await job.update(status='stopped', stopped=datetime.now())
    