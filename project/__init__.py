from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from project.config import Config
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
import os

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

db = SQLAlchemy()
login_manager = LoginManager()

mail = Mail()
migrate = Migrate()


#########################################
#register blueprints

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.__init__(app)
    login_manager.__init__(app)
    login_manager.login_view = 'users.login'
    login_manager.login_message_category = 'info'
    mail.__init__(app)
    migrate.__init__(app, db)

    from project.users.views import users, google_blueprint
    from project.events.views import events
    from project.main.views import main
    from project.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(events)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(google_blueprint, url_prefix='/google_login')



    return app





