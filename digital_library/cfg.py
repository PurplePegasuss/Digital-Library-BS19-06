import os
DATABASE = os.environ.get('DATABASE', 'sqlite:///./data/db.sqlite')
SECRET_KEY = bytes(os.environ.get('SECRET_KEY', 'очень сложный ключ'))
