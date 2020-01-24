#!/usr/bin/env python3
from base64 import b64decode
from json import dumps, loads
from multiprocessing import Pool
from os import path, remove, environ
from subprocess import run, PIPE
from sys import argv, exc_info
from urllib.request import Request, urlopen
from uuid import uuid4


def prepare_callback(url, job):
    def callback(identifier, status, subject):
        payload = {
            'identifier': identifier,
            'job': job,
            'status': status,
            'subject': subject,
        }

        data = dumps(payload).encode('UTF-8')
        headers = { 'Content-Type': 'application/json' }

        try:
            urlopen(Request(url, data, headers))
        except:
            print(f'Failed to post JSON to: {url}')

    return callback


def download(partition, callback_url, job, proxy_file, working_dir):
    callback = prepare_callback(callback_url, job)

    identifier = partition['identifier']
    transfers = partition['transfers']

    copyjob = '\n'.join([path.join(f'{t} file:////local/', path.basename(t)) for t in transfers])
    random = str(uuid4().hex[0:4])
    copyjob_file = path.join(working_dir, f'copyjob_{random}')

    # Write copyjob to file
    with open(copyjob_file, 'w') as f:
        f.write(copyjob)

    command = [
        'srmcp',
        '-debug',
        '-use_urlcopy_script=true',
        '-urlcopy=/var/local/lta-url-copy.sh',
        '-server_mode=passive',
        f'-x509_user_proxy={proxy_file}',
        f'-copyjobfile={copyjob_file}'
    ]

    try:
        callback(identifier, 'started', 'partition')
        run(command, stdout=PIPE, check=True)
        callback(identifier, 'complete', 'partition')
    except:
        callback(identifier, 'failed', 'partition')

    # Cleanup
    remove(copyjob_file)


if __name__ == '__main__':
    arguments = loads(b64decode(argv[1]).decode('UTF-8'))
    working_dir = argv[2]

    callback_url = arguments['callback_url']
    partitions = arguments['partitions']
    identifier = arguments['identifier']
    parallelism = arguments['parallelism']
    proxy_file = arguments['proxy_file']

    # Prepare callback and download functions
    callback = prepare_callback(callback_url, identifier)

    # Start downloading
    callback(identifier, 'started', 'job')

    partitions_with_arguments = [[
        partition,
        callback_url,
        identifier,
        proxy_file,
        working_dir
    ] for partition in partitions]

    with Pool(processes=parallelism) as pool:
        pool.starmap(download, partitions_with_arguments)

    callback(identifier, 'stopped', 'job')
