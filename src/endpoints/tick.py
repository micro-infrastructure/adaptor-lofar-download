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
async def tick(payload):
    await review_downloads()

    return (None, HTTPStatus.ACCEPTED)


async def review_downloads():
    downloads = await Download.objects.filter(status='started').all()
    downloads_n = len(downloads)

    logger.debug(f'Reviewing {downloads_n} downloads...')
    
    for download in downloads:
        # Perhaps is finished?
        non_complete = await Partition.objects.filter(status__in=['created', 'started']).all()
        if len(non_complete) == 0:
            await download.update(status='complete', stopped=datetime.now())
            logger.info(f'Download {download.identifier} is complete!')
            continue
        
        scheduler = create_scheduler(
            hostname=download.target_hostname,
            credential=create_credential(
                username=download.target_username, 
                password=download.target_password
            )
        )

        logger.debug(f'Updating job(s) of download {download.identifier}...')
        await update_jobs(download, scheduler)
        scheduler.close()
        
        # Ensure there is an active job.
        try:
            await Job.objects.filter(
                download=download,
                status__in=['created', 'started']
            ).get()
        except NoMatch:
            logger.info(f'No active job for download {download.identifier}, creating one...')
            await create_job(download)


STOPPED_STATES = [
    'CANCELLED', 
    'FAILED', 
    'NODE_FAIL', 
    'OUT_OF_MEMORY', 
    'PREEMPTED', 
    'TIMEOUT'
]

async def update_jobs(download, scheduler):
    jobs = await Job.objects.filter(
        download=download, 
        status__in=['created', 'started']
    ).all()

    for job in jobs:
        if job.xenon_id is None:
            continue

        state = get_xenon_state(job.xenon_id, scheduler).state
        await job.update(xenon_state=state, updated=datetime.now())

        if state in STOPPED_STATES or state.startswith('CANCELLED'):
            logger.info(f'Job {job.identifier} has stopped with state: {state}')
            await job.update(status='stopped', stopped=datetime.now())
    