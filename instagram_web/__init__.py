from app import app
from flask import render_template,redirect,request,url_for,session,flash,escape
from flask_login import LoginManager,login_required,current_user,login_user,logout_user
from instagram_web.blueprints.users.views import users_blueprint
from instagram_web.blueprints.sessions.views import sessions_blueprint
from instagram_web.blueprints.donation.views import donation_blueprint
from flask_assets import Environment, Bundle
from .util.assets import bundles
from werkzeug.security import generate_password_hash,check_password_hash
import re
# we have to specify which file and which data
from models.user import User
from models.image import Image
from helpers import s3
from config import S3_BUCKET
# for google oauth
import os
from instagram_web.helpers.google_oauth import oauth
import config

oauth.init_app(app)


app.config.from_object("config")

assets = Environment(app)
assets.register(bundles)

# CHECK FOR LOGIN 
login_manager = LoginManager()
login_manager.init_app(app)
# login_manager.login_view = 'sign_in_form'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

app.register_blueprint(users_blueprint, url_prefix="/users")
app.register_blueprint(sessions_blueprint, url_prefix="/sessions")
app.register_blueprint(donation_blueprint, url_prefix="/donation")


@app.route("/")
def home():
    return render_template('home.html')


#  error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

