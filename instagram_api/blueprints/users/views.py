from flask import Blueprint, request,jsonify
from flask import render_template,redirect,request,url_for,session,flash,escape
import sendgrid
import os
from flask_login import LoginManager,login_required,current_user,login_user,logout_user
from models.user import User
from models.image import Image
from rqueue import q
from werkzeug.security import generate_password_hash,check_password_hash
import re
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity
)

from app import csrf

users_api_blueprint = Blueprint('users_api',
                             __name__,
                             template_folder='templates')


                                
#? sendiung email API
@users_api_blueprint.route('<img_id>/send_email', methods=['GET','POST'])
def send_email(img_id):
    # breakpoint()
    img = Image.get_or_none(Image.id == img_id)
    user = User.get_or_none(User.id == img.user_id)
    q.enqueue(send, user.email)
    return redirect(url_for('donation.new_checkout',img_id=img_id))

def send(email):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    data = {
    "personalizations": [
        {
        "to": [
            {
            "email": email
            }
        ],
        "subject": "Sending with SendGrid is Fun"
        }
    ],
    "from": {
        "email": "chu22f@gmail.com"
    },
    "content": [
        {
        "type": "text/plain",
        "value": "and easy to do anywhere, even with Python"
        }
    ]
    }
    response = sg.client.mail.send.post(request_body=data)
    print(response.status_code)
    print(response.body)
    print(response.headers)

#? till here is for sending email



@users_api_blueprint.route("/users",methods=['GET'])
def show():
    users = User.select()

    return jsonify([
        {"id": user.id,
        "username": user.username,
        "profileImage": user.profile_image_url} for user in users])


@users_api_blueprint.route('/new', methods=['POST'])
@csrf.exempt
def create():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    email = request.json.get('email',None)

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400

    # actual sign up users 
    user_password = password
    hashed_password = generate_password_hash(user_password)

    pattern_password = '\w{6,}'
    result = re.search(pattern_password, user_password)
    pattern_email = '[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]'
    result_email = re.search(pattern_email,email)

    username_check = User.get_or_none(User.username == username)
    email_check = User.get_or_none(User.email == email)
    
    if (result and result_email):
        u = User(username=username,email=email,password=hashed_password)

    if not username_check and not email_check:
        u.save()
        user = User.get(User.username == username)
        access_token = create_access_token(identity=username)
        return jsonify({
        "access_tokhttp://localhost:5000/api/v1/auth/loginen": access_token,
        "message": "Successfully created a user and signed in.",
        "status": "success",
        "user": {
            "id": user.id,
            "profile_picture": user.profile_image_url,
            "username": user.username
        }
    }), 200
    else:
        return jsonify({"msg": "username or email already used"}), 400
  

    
