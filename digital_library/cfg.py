import os
from pathlib import Path

DATABASE = os.environ.get('DATABASE', 'sqlite:///./data/db.sqlite')
SECRET_KEY = os.environ.get('SECRET_KEY', 'очень сложный ключ').encode('utf-8')

MATERIALS_PER_PAGE = int(os.environ.get('MATERIALS_PER_PAGE', 4))  # TODO: is 4 for the moment, make it 20 after!
COMMENTS_PER_PAGE = int(os.environ.get('COMMENTS_PER_PAGE', 3))  # TODO: is 3 for the moment, make it 20 after!
REVIEWS_PER_PAGE = int(os.environ.get('REVIEWS_PER_PAGE', 2))  # TODO: is 2 for the moment, make it 10 after!

# flask-login
SESSION_PROTECTION = "strong"

UPLOAD_PATH = Path(os.environ.get('UPLOADS_PATH', Path(__file__).parent / 'static' / 'uploads'))
assert UPLOAD_PATH.exists()
assert str(UPLOAD_PATH).startswith(str((Path(__file__).parent / 'static')))
