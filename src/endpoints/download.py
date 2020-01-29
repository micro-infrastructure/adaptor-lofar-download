from http import HTTPStatus

from persistence import Download, Partition, Transfer
from runtimes import pubsub, webapi


@pubsub.expose
@webapi.expose
async def download(payload):
    name, files, target, credentials, options, webhook = unpack_command(payload)

    # Divide file transfers into partitions.
    partitions = partitionize(files, options['partitions'])

    # Persist parameters.
    download = await Download.objects.create(
        certificate=credentials['certificate'],
        name=name,
        parallelism=options['parallelism'],
        target_directory=target['path'],
        target_hostname=target['host'],
        target_password=credentials['password'],
        target_username=credentials['username'],
        webhook_url=webhook.get('url', None)
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

    # The identifier can be used to manage the download.
    output = {
        "identifier": download.identifier
    }

    return (output, HTTPStatus.ACCEPTED)


def unpack_command(payload):
    name = payload['id']
    command = payload['cmd']

    files = command['src']['paths']
    target = command['dest']
    credentials = command['credentials']
    options = command.get('options', {})
    webhook = command.get('webhook', {})

    return (name, files, target, credentials, options, webhook)


def partitionize(items, n):
    if items == []:
        return

    yield items[:n]
    yield from partitionize(items[n:], n)