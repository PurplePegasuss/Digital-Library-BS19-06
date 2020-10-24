from flask import Blueprint, render_template

index_router = Blueprint('index', __name__, template_folder='templates')


@index_router.route('/')
def index():
    return render_template('index.html')
