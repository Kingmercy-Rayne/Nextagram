from flask import Blueprint, request,jsonify
from flask import render_template,redirect,request,url_for,session,flash,escape
import sendgrid
import os
from flask_login import LoginManager,login_required,current_user,login_user,logout_user
from models.user import User
from models.image import Image
from rqueue import q
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

images_api_blueprint = Blueprint('images_api',
                             __name__,
                             template_folder='templates')


@images_api_blueprint.route("/",methods=['GET'])
def index():
    # breakpoint()
    id = request.args.get("userId")
    imgs = []
    if id:
        imgs = Image.select().where(Image.user_id == request.args["userId"])
    else:
        imgs = Image.select()
    return jsonify([img.image_path for img in imgs])





@images_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def protected():
    username = get_jwt_identity()
    user = User.get_or_none(User.username == username)
    images = Image.select().where(user.id == Image.user_id)
    return jsonify([img.image_path for img in images]), 200
