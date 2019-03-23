from app import app
from flask import render_template,redirect,request,url_for,session,flash,escape
from flask_login import LoginManager,login_required,current_user,login_user,logout_user
from instagram_web.blueprints.users.views import users_blueprint
from flask_assets import Environment, Bundle
from .util.assets import bundles
from werkzeug.security import generate_password_hash,check_password_hash
import re
# we have to specify which file and which data
from models.user import User
from models.image import Image
from helpers import s3
from config import S3_BUCKET


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





@app.route("/")
@login_required
def home():
    users = User.select()
    users_list = list(users)
    return render_template('home.html',users_list=users_list)


# SIGN UP
@app.route("/sign_up")
def sign_up():
    return render_template('sign_up.html')

@app.route("/sign_up_form", methods=["POST"])
def sign_up_form():
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
            return redirect(url_for('sign_up'))
        else:
            return render_template('sign_up.html',username=request.form['username'],email=request.form['email'],password=request.form['password'],errors=u.errors)    

    elif not result and result_email:
        flash("password must be longer than 6")
        return render_template('sign_up.html',username=request.form['username'],email=request.form['email'],password=request.form['password']) 

    elif not result_email and result:
        flash("invalid email")
        return render_template('sign_up.html',username=request.form['username'],email=request.form['email'],password=request.form['password']) 
    
    else:
        flash("password must be longer than 6")
        flash("invalid email")
        return render_template('sign_up.html',username=request.form['username'],email=request.form['email'],password=request.form['password']) 


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
            return redirect(url_for('home'))

        else:
            flash('login failed')
            return render_template('sign_in.html')
    
    else:
        flash('login failed')
        return render_template('sign_in.html')


@app.route("/profile_edit")
def profile_edit():
    # objects= s3.list_objects(Bucket=S3_BUCKET)
    # fi = objects('Key').get()
    # import boto3
    # s3 = boto3.resource('s3')
    # s3.Bucket('mybucket').download_file('hello.txt', '/tmp/hello.txt')
    return render_template('profile_edit.html',img=current_user.profile_image_url)



@app.route("/profile_edit_form", methods=["POST"])
def profile_edit_form():
    # breakpoint()
    u = (User.update({User.username: request.form['username']})).where(User.username==current_user.username)

    if not User.get_or_none(User.username==request.form['username']):
        if u.execute():
            flash("successfully updated")
            return redirect(url_for("profile_edit"))
        else:
            return render_template("profile_edit.html", username=request.form["username"])
    else:
        return render_template("profile_edit.html", username=request.form["username"])

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
        return redirect(url_for("profile_edit"))
    except:
        flash("Something went wrong!!")
        return render_template("profile_edit.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('logged out')
    return redirect(url_for('sign_in'))


# USER PROFILE PAGE
@app.route('/user_profile')
@login_required
def user_profile():
    # breakpoint()
    images = Image.select().where(Image.user_id == current_user.id)
    path = list(images)
    return render_template('user_profile.html',img=current_user.profile_image_url,images_path=path)

@app.route("/upload_img", methods=["POST"])
def upload_img():
    # breakpoint()
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
        return redirect(url_for("user_profile"))
    except:
        flash("Something went wrong!!")
        return render_template("user_profile.html")




#  error handler
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# @app.errorhandler(500)
# def server_error(e):
#     # note that we set the 404 status explicitly
#     return render_template('500.html'), 500