import os
DATABASE = os.environ.get('DATABASE', 'sqlite:///./data/db.sqlite')
