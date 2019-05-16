from flask import Blueprint, request,jsonify
from flask import render_template,redirect,request,url_for,session,flash,escape
import sendgrid
import os
from flask_login import LoginManager,login_required,current_user,login_user,logout_user
from models.user import User
from models.image import Image
from rqueue import q
from flask_jwt import jwt_required, current_identity as current_user
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity
)
from werkzeug.security import check_password_hash
from app import csrf

login_api_blueprint = Blueprint('login_api',
                             __name__,
                             template_folder='templates')


# @login_api_blueprint.route("/",methods=['post'])
# def new(username, password):
    
#     return 'sdfsdfsdfsdf'
    
@login_api_blueprint.route('/login', methods=['POST'])
@csrf.exempt
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    user = User.get(User.username == username)
    if user and check_password_hash(user.password, password):
        # Identity can be any data that is json serializable
        access_token = create_access_token(identity=username)
        return jsonify({
            "access_token": access_token,
            "message": "Successfully signed in.",
            "status": "success",
            "user": {
                "id": user.id,
                "profile_picture": user.profile_image_url,
                "username": user.username
            }
        }), 200
    else:
        return jsonify({"msg": "Bad login"}), 404

