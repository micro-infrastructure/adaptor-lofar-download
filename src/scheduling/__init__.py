from persistence import Job
from runtimes import xenon

from hashlib import md5
from time import localtime

async def schedule(download):
    hostname = download.target_hostname
    password = download.target_password
    username = download.target_username

    job = await Job.objects.create(download=download)

    # Prepare Xenon objects
    credential = create_credential(username, password)
    remotefs = create_remotefs(hostname, credential)

    # Write bootstrap script to remote filesystem
    script = 'echo "hello, world!"'
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