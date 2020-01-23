from http import HTTPStatus

from persistence import Download, Partition, Transfer
from runtimes import pubsub, webapi
from scheduling import schedule


@pubsub.expose
@webapi.expose
async def download(payload):
    files, target, credentials, options = unpack_command(payload)

    # Divide file transfers into partitions.
    partitions = partitionize(files, options['partitions'])

    # Persist parameters.
    download = await Download.objects.create(
        certificate=credentials['certificate'],
        parallelism=options['parallelism'],
        target_directory=target['directory'],
        target_hostname=target['hostname'],
        target_password=credentials['password'],
        target_username=credentials['username'],
    )

    # Persist partitions.
    for files in partitions:
        partition = await Partition.objects.create(
            download=download,
        )

        for filename in files:
            await Transfer.objects.create(
                filename=filename, 
                partition=partition,
            )

    # Schedule the download.
    await schedule(download)

    # The identifier can be used to manage the download.
    output = {
        "identifier": download.identifier
    }
    return (output, HTTPStatus.ACCEPTED)


def unpack_command(payload):
    command = payload['cmd']

    files = command['files']
    target = command['target']
    credentials = command['credentials']
    options = command['options']

    return (files, target, credentials, options)


def partitionize(items, n):
    if items == []:
        return

    yield items[:n]
    yield from partitionize(items[n:], n)