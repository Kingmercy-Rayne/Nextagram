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

# what does it mean??????????????????????????????????????????
# app.register_blueprint(users_blueprint, url_prefix="/users")


# main page
@app.route("/users/")
@login_required
def home():
    users = User.select()
    image = Image.select()
    users_list = list(users)
    return render_template('home.html',users_list=users_list,image=image)

# individual page
@app.route('/users/<name>/')
def users(name):
    images = list(Image.select().join(User).where(User.username == name))
    user = User.get_or_none(User.username == name)
    return render_template('indivisual_user.html', images=images,user=user)




# SIGN UP
@app.route("/user/new")
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
            return redirect(url_for('/user/new'))
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


@app.route("/user/<id>/edit")
def profile_edit(id):
    return render_template('profile_edit.html',img=current_user.profile_image_url)

@app.route("/profile_edit_name", methods=["POST"])
def profile_edit_name():
    # breakpoint()
    u = (User.update({User.username: request.form['username']})).where(User.username==current_user.username)

    if not User.get_or_none(User.username==request.form['username']):
        if u.execute():
            flash("successfully updated")
            return redirect(url_for("/user/current_user.id/edit"))
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
        return redirect(url_for("/user/<id>/edit"))
    except:
        flash("Something went wrong!!")
        return render_template("profile_edit.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('logged out')
    return redirect(url_for('sign_in'))


# myprofile upload
@app.route("/upload_img", methods=["POST"])
def upload_img():
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
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
