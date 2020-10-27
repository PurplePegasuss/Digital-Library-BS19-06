import os

DATABASE = os.environ.get('DATABASE', 'sqlite:///./data/db.sqlite')
SECRET_KEY = os.environ.get('SECRET_KEY', 'очень сложный ключ').encode('utf-8')

MATERIALS_PER_PAGE = int(os.environ.get('MATERIALS_PER_PAGE', 4))  # TODO: is 4 for the moment, make it 20 after!
COMMENTS_PER_PAGE = int(os.environ.get('COMMENTS_PER_PAGE', 3))     # TODO: is 3 for the moment, make it 20 after!
