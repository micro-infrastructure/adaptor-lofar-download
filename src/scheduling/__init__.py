from persistence import Job, Partition, Transfer
from runtimes import xenon

from base64 import b64decode, b64encode
from json import dumps
from hashlib import md5
from os import getenv
from time import localtime


IMAGE = 'docker://microinfrastructure/adaptor-lofar-download-hpc'


async def schedule(download):
    directory = download.target_directory
    hostname = download.target_hostname
    parallelism = download.parallelism
    password = download.target_password
    username = download.target_username
    
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
    script = f'singularity run -B {directory}:/local {IMAGE} {arguments}'
    script_path = create_unique_path('bootstrap.sh')
    script_lines = [l.encode('UTF-8') for l in script.splitlines(keepends=True)]

    remotefs.write_to_file(script_path, script_lines)

    # Submit bootstrap script as job.
    job_description = xenon.JobDescription(
        executable='/bin/bash',
        arguments=[script_path]
    )

    scheduler = create_scheduler(hostname, credential)
    xenon_job = scheduler.submit_batch_job(job_description)
    await job.update(xenon_id=xenon_job.id)

    # Cleanup
    remotefs.delete(script_path)


async def create_arguments(callback_url, download, identifier, proxy_file, parallelism):
    partitions = [{
        'identifier': p.identifier,
        'transfers': [
            t.filename for t in await Transfer.objects.filter(partition=p).all()
        ]
    } for p in await Partition.objects.filter(download=download).all()]

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
        location=f'ssh://{hostname}',
        password_credential=credential,
        properties={
            'xenon.adaptors.schedulers.ssh.strictHostKeyChecking': 'false'
        }
    )


def create_remotefs(hostname, credential):
    return xenon.FileSystem.create(
        'sftp',         
        location=hostname,
        password_credential=credential,
        properties={
            'xenon.adaptors.filesystems.sftp.strictHostKeyChecking': 'false'
        }
    )