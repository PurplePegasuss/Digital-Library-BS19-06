from flask import Flask
from flask_admin import Admin

app = Flask(__name__)
app.config.from_object('digital_library.cfg')
admin = Admin(app, name='DigitalLibrary', template_mode='bootstrap3')

