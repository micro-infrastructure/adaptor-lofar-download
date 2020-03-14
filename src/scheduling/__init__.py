from persistence import Job, Partition, Transfer
from runtimes import xenon
from .boostrap import get_bootstrap_generator

from operator import attrgetter
from base64 import b64decode, b64encode
from json import dumps
from loguru import logger
from hashlib import md5
from os import getenv
from time import localtime


IMAGE = 'docker://microinfrastructure/adaptor-lofar-download-hpc'


def get_xenon_state(xenon_id, scheduler):
    return scheduler.get_job_status(xenon.Job(xenon_id))


def cancel_job(xenon_id, scheduler):
    return scheduler.cancel_job(xenon.Job(xenon_id))


async def create_job(download):
    directory = download.target_directory
    hostname = download.target_hostname
    name = download.name
    parallelism = download.parallelism
    password = download.target_password
    username = download.target_username
    queue = download.queue
    log = download.log

    job = await Job.objects.create(download=download)

    # Prepare Xenon objects
    credential = create_credential(username, password)
    remotefs = create_remotefs(hostname, credential)

    # Write proxy certificate to remote filesystem
    proxy = b64decode(download.certificate).decode('UTF-8')
    proxy_path = create_unique_path('proxy.crt')
    proxy_lines = [l.encode('UTF-8') for l in proxy.splitlines(keepends=True)]

    remotefs.write_to_file(proxy_path, proxy_lines)

    # Prepare arguments
    callback_url = getenv('LOFARDOWNLOAD_SERVICE') + '/callback'
    arguments = await create_arguments(
        callback_url,
        download,
        job.identifier,
        str(proxy_path),
        parallelism
    )

    # Write bootstrap script to remote filesystem
    generate_bootstrap = get_bootstrap_generator(hostname)

    script = generate_bootstrap(directory, IMAGE, arguments)
    script_path = create_unique_path('bootstrap.sh')
    script_lines = [l.encode('UTF-8') for l in script.splitlines(keepends=True)]

    remotefs.write_to_file(script_path, script_lines)

    # Submit bootstrap script as job.
    job_description = xenon.JobDescription(
        arguments=[str(script_path)],
        cores_per_task=8,
        executable='/bin/bash',
        max_memory=8192,
        max_runtime=300,
        name=name
    )

    if log:
        out_file = create_unique_path(f'd#{download.identifier}.txt')
        job_description.stdout = f'stdout-{out_file}'
        job_description.stderr = f'stderr-{out_file}'

    if queue is not None:
        job_description.queue_name=queue
        logger.info(f'Using {queue} instead of default queue')

    scheduler = create_scheduler(hostname, credential)
    xenon_job = scheduler.submit_batch_job(job_description)
    await job.update(xenon_id=xenon_job.id)

    try:
        remotefs.delete(script_path)
    except Exception:
        logger.exception(f'Failed to delete file: {script_path}')


async def create_arguments(callback_url, download, identifier, proxy_file, parallelism):
    partitions = [{
        'identifier': p.identifier,
        'transfers': [
            t.filename for t in await Transfer.objects.filter(partition=p).all()
        ]
    } for p in sorted(await
        (Partition
            .objects
            .filter(download=download, status__in=['created', 'started'])
            .all()),
        key=lambda partition: partition.status, reverse=True)
    ]

    return b64encode(dumps({
        'callback_url': callback_url,
        'parallelism': parallelism,
        'partitions': partitions,
        'identifier': identifier,
        'proxy_file': proxy_file
    }).encode('UTF-8')).decode('UTF-8')


def create_unique_path(filename):
    random = md5(str(localtime()).encode('UTF-8')).hexdigest()[:8]

    return xenon.Path(f'{random}_{filename}')


def create_credential(username, password):
    return xenon.PasswordCredential(
        username=username,
        password=password
    )


def create_scheduler(hostname, credential):
    return xenon.Scheduler.create(
        adaptor='slurm',
        location=f'ssh://{hostname}:22',
        password_credential=credential,
        properties={
            'xenon.adaptors.schedulers.ssh.strictHostKeyChecking': 'false'
        }
    )


def create_remotefs(hostname, credential):
    return xenon.FileSystem.create(
        'sftp',
        location=f'{hostname}:22',
        password_credential=credential,
        properties={
            'xenon.adaptors.filesystems.sftp.strictHostKeyChecking': 'false'
        }
    )
