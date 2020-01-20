from orm import DateTime, ForeignKey, Integer, Model, String
from persistence import database, metadata

class Download(Model):
    __tablename__ = "download"
    __database__ = database
    __metadata__ = metadata

    identifier = Integer(primary_key=True)

    # Fields
    status = String(max_length=100)

    # Timestamps
    created = DateTime()
    started = DateTime(allow_null=True)
    stopped = DateTime(allow_null=True)


class Partition(Model):
    __tablename__ = "partition"
    __database__ = database
    __metadata__ = metadata

    identifier = Integer(primary_key=True)

    # Fields
    download = ForeignKey(Download)
    status = String(max_length=100)

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
    filename = String(max_length=100)
    partition = ForeignKey(Partition)
    size = Integer(allow_null=True)


class Job(Model):
    __tablename__ = "job"
    __database__ = database
    __metadata__ = metadata  

    identifier = Integer(primary_key=True)

    # Fields
    download = ForeignKey(Download)
    status = String(max_length=100)
    xenon_id = String(max_length=100)

    # Timestamps
    created = DateTime()
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

    # Timestamps
    started = DateTime()
    stopped = DateTime(allow_null=True)
