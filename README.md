# LOFAR download adaptor

## Functions
This adaptor exposes three functions: download, status and cancel. 

Reachable on `/download`, `/status`, and `/cancel` via HTTP, or `functions.lofar-download.download`, `functions.lofar-download.status`, `functions.lofar-download.cancel` via AMQP.

### `download`
Use the following request payload, with `paths` containing SURLs:

```json
{
    "cmd": {
        "src": {
            "paths": [
                "...", 
                "..."
            ]
        },
        "dest": {
            "host": "...",
            "path": "..."
        },
        "credentials": {
            "username": "...",
            "password": "...",
            "certificate": "..."
        },
        "options": {
            "partitions": 5,
            "parallelism": 8
        }
    }
}
```

The response will contain the identifier of the download:
```json
{
    "identifier": "..."
}
```

### `status`
Embed the download identifier in the URL to retrieve the status:

```shell
http get http://lobcder.process-project.eu:<port>/status/<identifier>
```

### `cancel`
Use the following request payload:

```json
{
    "identifier": "..."
}
```

## AMQP
In case of AMQP, wrap the payload in the following JSON:

```json
{
    "id": "...",
    "replyTo": "...",
    "body": "<payload>"
}
```
