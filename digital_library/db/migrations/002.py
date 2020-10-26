from playhouse.migrate import migrate

from digital_library.db import ATTACHMENT, USER
from . import migrator

migrate(migrator.add_column(USER._meta.table.__name__, 'PasswordHash', USER.PasswordHash))
migrate(migrator.rename_column(ATTACHMENT._meta.table.__name__, 'URLS', 'Url'))
