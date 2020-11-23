from playhouse.migrate import migrate

from digital_library.db import MATERIAL
from . import migrator

migrate(
    migrator.add_column(MATERIAL._meta.table.__name__, 'Title', MATERIAL.Title)
)
