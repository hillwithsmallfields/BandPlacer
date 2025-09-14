import os

from flask import Flask, render_template

# based on https://flask.palletsprojects.com/en/stable/tutorial/factory/

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'bandplacer.sqlite'),
    )

    if test_config:
        app.config.from_mapping(test_config)
    else:
        app.config.from_pyfile('config.py', silent=True)

    os.makedirs(app.instance_path, exist_ok=True)

    @app.route('/')
    def home():
        return render_template('home.html')

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import user
    app.register_blueprint(user.bp)

    return app
