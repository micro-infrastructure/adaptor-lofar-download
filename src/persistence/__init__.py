from databases import Database
from sqlalchemy import create_engine, MetaData

database = Database("sqlite:///db.sqlite")
metadata = MetaData()

from persistence.models import Download

engine = create_engine(str(database.url))
metadata.create_all(engine)