import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate, MigrateCommand
from flask_msearch import Search
from flask_mail import Mail

app = Flask(__name__)
##################DataBase Setup#####################

basedir = os.path.abspath(os.path.dirname(__file__))

# Settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
""" app.config['MSEARCH_INDEX_NAME '] = 'msearch'
app.config['MSEARCH_ENABLE'] = True
app.config['MSEARCH_BACKEND'] = 'whoosh' """
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')

app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

# Variables
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
search = Search(app)
search.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category= 'info'
migrate = Migrate(app, db)
mail = Mail(app)

#######################################################


from nstublog import routes