from playhouse.migrate import SqliteMigrator

from .. import database

migrator = SqliteMigrator(database)
