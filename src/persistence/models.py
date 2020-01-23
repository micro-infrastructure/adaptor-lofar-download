from datetime import datetime

from orm import DateTime, ForeignKey, Integer, Model, String
from persistence import database, metadata

class Download(Model):
    __tablename__ = "download"
    __database__ = database
    __metadata__ = metadata

    identifier = Integer(primary_key=True)

    # Fields
    certificate = String(max_length=None)
    parallelism = Integer()
    status = String(max_length=100, default='created')
    target_directory = String(max_length=100)
    target_hostname = String(max_length=100)
    target_password = String(max_length=100)
    target_username = String(max_length=100)

    # Timestamps
    created = DateTime(default=datetime.now)
    started = DateTime(allow_null=True)
    stopped = DateTime(allow_null=True)


class Partition(Model):
    __tablename__ = "partition"
    __database__ = database
    __metadata__ = metadata

    identifier = Integer(primary_key=True)

    # Fields
    download = ForeignKey(Download)
    status = String(max_length=100, default='created')

    # Timestamps
    started = DateTime(allow_null=True)
    stopped = DateTime(allow_null=True)


class Transfer(Model):
    __tablename__ = "transfer"
    __database__ = database
    __metadata__ = metadata

    identifier = Integer(primary_key=True)

    # Fields
    checksum = String(max_length=100, allow_null=True)
    filename = String(max_length=None)
    partition = ForeignKey(Partition)
    size = Integer(allow_null=True)


class Job(Model):
    __tablename__ = "job"
    __database__ = database
    __metadata__ = metadata  

    identifier = Integer(primary_key=True)

    # Fields
    download = ForeignKey(Download)
    status = String(max_length=100, default='created')
    xenon_id = String(max_length=100, allow_null=True)

    # Timestamps
    created = DateTime(default=datetime.now)
    started = DateTime(allow_null=True)
    stopped = DateTime(allow_null=True)


class Attempt(Model):
    __tablename__ = "attempt"
    __database__ = database
    __metadata__ = metadata

    identifier = Integer(primary_key=True)

    # Fields
    job = ForeignKey(Job)
    partition = ForeignKey(Partition)
    status = String(max_length=100, default='started')

    # Timestamps
    started = DateTime(default=datetime.now)
    stopped = DateTime(allow_null=True)
