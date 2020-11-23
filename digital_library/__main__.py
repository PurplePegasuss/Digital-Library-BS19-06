import digital_library.db
from digital_library.app import app, admin
from digital_library.views import create_views
create_views(app, admin)

if __name__ == '__main__':
    app.run('0.0.0.0', '8080', debug=False)
