from flask import Blueprint, render_template
from app import app
from flask import render_template,redirect,request,url_for,session,flash,escape
from flask_login import LoginManager,login_required,current_user,login_user,logout_user
from flask_assets import Environment, Bundle
# from .util.assets import bundles
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


sessions_blueprint = Blueprint('sessions',
                            __name__,
                            template_folder='templates')


@sessions_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('sessions/new.html')


@sessions_blueprint.route('/', methods=['POST'])
def create():
    pass


@sessions_blueprint.route('/<username>', methods=["GET"])
def show(username):
    pass


@sessions_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"


@sessions_blueprint.route('/<id>/edit', methods=['GET'])
def edit(id):
    pass


@sessions_blueprint.route('/<id>', methods=['POST'])
def update(id):
    pass



# SIGN IN
@app.route("/sign_in")
def sign_in():
    return render_template('sign_in.html')

@app.route("/sign_in_form" , methods=["POST"])
def sign_in_form():
    password_to_check = request.form['password'] 

    # breakpoint()
    user = User.get_or_none(User.username == request.form.get("username"))

    if user:
        hashed_password = user.password
        result = check_password_hash(hashed_password, password_to_check) 

        if result:
            flash('Successfully login')
            login_user(user)
            # session['username'] = request.form['username'] 
            return redirect(url_for('users.index'))

        else:
            flash('login failed')
            return render_template('sessions.new.html')
    
    else:
        flash('login failed')
        return render_template('sessions.new.html')


@app.route("/google_sign_in", methods=["GET","POST"])
def google_sign_in():
    redirect_url = url_for('authorize', _external= True)
    return oauth.google.authorize_redirect(redirect_url)


@app.route("/authorize", methods=["GET","POST"])
def authorize():
    token = oauth.google.authorize_access_token()
    email = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()['email']

    user = User.get_or_none(User.email == email)
    # user = User.query.filter_by(email=email).first()

    if user:
        login_user(user)
        return redirect(url_for('users.index'))
    else:
        return render_template('sessions.new.html')
    
    







@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('logged out')
    return redirect(url_for('sessions.new'))