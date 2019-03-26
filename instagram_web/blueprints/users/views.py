from flask import Blueprint, render_template
from app import app
from flask import render_template,redirect,request,url_for,session,flash,escape
from flask_login import LoginManager,login_required,current_user,login_user,logout_user
from flask_assets import Environment, Bundle
# from .util.assets import bundles
from werkzeug.security import generate_password_hash,check_password_hash
import re
# we have to specify which file and which data
from models.user import User, Following
from models.image import Image
from helpers import s3
from config import S3_BUCKET
# for google oauth
import os
from instagram_web.helpers.google_oauth import oauth
import config
import braintree

# donation things
gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id="use_your_merchant_id",
        public_key="use_your_public_key",
        private_key="use_your_private_key"
    )
)

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')


@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')


@users_blueprint.route('/create', methods=['POST'])
def create():
    user_password = request.form['password']
    hashed_password = generate_password_hash(user_password)

    pattern_password = '\w{6,}'
    result = re.search(pattern_password, user_password)
    pattern_email = '[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]'
    result_email = re.search(pattern_email,request.form['email'])
    
    if (result and result_email):
        u = User(username=request.form['username'],email=request.form['email'],password=hashed_password)

        if u.save():
            flash("Successfully saved")
            return redirect(url_for('/new'))
        else:
            return render_template('new.html',username=request.form['username'],email=request.form['email'],password=request.form['password'],errors=u.errors)    

    elif not result and result_email:
        flash("password must be longer than 6")
        return render_template('new.html',username=request.form['username'],email=request.form['email'],password=request.form['password']) 

    elif not result_email and result:
        flash("invalid email")
        return render_template('new.html',username=request.form['username'],email=request.form['email'],password=request.form['password']) 
    
    else:
        flash("password must be longer than 6")
        flash("invalid email")
        return render_template('new.html',username=request.form['username'],email=request.form['email'],password=request.form['password'])     


@users_blueprint.route('/<username>/', methods=["GET"])
def show(username):
    # client_token = gateway.client_token.generate()
    images = list(Image.select().join(User).where(User.username == username))
    user = User.get_or_none(User.username == username)
    follow = Following.get_or_none(Following.fan_id == current_user.id and Following.idol_id == user.id)
    return render_template('users/show.html', images=images,user=user,username=username,follow=follow)


@users_blueprint.route('/<username>/follow', methods=["POST"])
def follow(username):
    images = list(Image.select().join(User).where(User.username == username))
    user = User.get_or_none(User.username == username)
    idol_id = user.id
    if user.private:
        f = Following(fan_id=current_user.id, idol_id=idol_id)
        f.save()
    else:
        f = Following(fan_id=current_user.id, idol_id=idol_id,approval=True)
        f.save()
    follow = Following.get_or_none(Following.fan_id == current_user.id and Following.idol_id == user.id)
    return render_template('users/show.html', images=images,user=user,username=username,follow=follow)


@users_blueprint.route('/<username>/unfollow', methods=["POST"])
def unfollow(username):
    images = list(Image.select().join(User).where(User.username == username))
    user = User.get_or_none(User.username == username)
    idol_id = user.id
    uf = Following.delete().where(Following.fan_id==current_user.id and Following.idol_id==idol_id)
    uf.execute()
    follow = Following.get_or_none(Following.fan_id == current_user.id and Following.idol_id == user.id)
    return render_template('users/show.html', images=images,user=user,username=username,follow=follow)




@users_blueprint.route('/<username>/feed', methods=["GET"])
@login_required
def show_feed(username):
    users = User.select().join(Following, on=(User.id == Following.idol_id)).where(Following.fan_id == current_user.id and Following.approval==True)
    image = Image.select()
    # approval = Following.select()
    return render_template('users/show_feed.html',users_list=users,image=image)



@users_blueprint.route('/<id>/edit', methods=['GET'])
def edit(id):
    return render_template('users/edit.html',img=current_user.profile_image_url)
    

@app.route("/profile_edit_name", methods=["POST"])
def profile_edit_name():
    # breakpoint()
    u = (User.update({User.username: request.form['username']})).where(User.username==current_user.username)

    if not User.get_or_none(User.username==request.form['username']):
        if u.execute():
            flash("successfully updated")
            return redirect(url_for("users.edit", id=current_user.id))
            
        else:
            flash("failed")
            return render_template("users/edit.html", username=request.form["username"])
    else:
        flash("failed")
        return render_template("users/edit.html", username=request.form["username"])

@app.route("/upload", methods=["POST"])
def upload():
    # breakpoint()
    try:
        file = request.files.get("user_file")
        s3.upload_fileobj(
            file,
            S3_BUCKET,
            file.filename
        )
        flash("successfully updated")
        file = request.files.get("user_file")
        u = (User.update({User.picture: file.filename})).where(User.username == current_user.username)
        # userp = current_user.picture = request.files.get("user_file").filename
        # userp.save()
        u.execute()
        return redirect(url_for("/<id>/edit"))
    except:
        flash("Something went wrong!!")
        return render_template("edit.html")


# myprofile upload
@app.route("/upload_img", methods=["POST"])
def upload_img():
    images = list(Image.select().join(User).where(User.username == current_user.username))
    user = User.get_or_none(User.username == current_user.username)
    try:
        file = request.files.get("user_file")
        s3.upload_fileobj(
            file,
            S3_BUCKET,
            file.filename
        )
        flash("successfully updated") 

        p = Image(description=request.form['description'],user_id=current_user.id,img_path=file.filename)
        p.save()
        return render_template("users/show.html", images=images,user=user)
    except:
        flash("Something went wrong!!")
        return render_template("users/show.html", images=images,user=user)



@users_blueprint.route('/', methods=['GET'])
@login_required
def index():
    users = User.select()
    image = Image.select()
    users_list = list(users)
    return render_template('users/index.html',users_list=users_list,image=image)




@users_blueprint.route('/<id>', methods=['POST'])
def update(id):
    pass

