#!/usr/bin/env python3
from base64 import b64decode
from json import loads
from multiprocessing import Pool
from os import path, remove, environ
from subprocess import run, PIPE
from sys import argv, exc_info
from uuid import uuid4
from loguru import logger
from requests import post
from os.path import isfile


def prepare_callback(url, job):
    def callback(identifier, status, subject):
        payload = {
            'identifier': identifier,
            'job': job,
            'status': status,
            'subject': subject,
        }

        try:
            post(url, json=payload)
        except Exception:
            logger.exception(f'Failed to post JSON to {url}')

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

    proxy_file_found = isfile(proxy_file)
    logger.info(f'Proxy file: {proxy_file} (found: {proxy_file_found}')
    logger.info(f'Copyjob file: {copyjob_file}')

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
    except Exception:
        logger.exception(f'Failed to download partition')
        callback(identifier, 'failed', 'partition')
    finally:
        try:
            remove(copyjob_file)
        except Exception:
            logger.exception(f'Failed to perform cleanup')


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
