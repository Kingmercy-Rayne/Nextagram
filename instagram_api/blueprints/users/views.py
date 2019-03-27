from flask import Blueprint
from flask import render_template,redirect,request,url_for,session,flash,escape
import sendgrid
import os
from flask_login import LoginManager,login_required,current_user,login_user,logout_user
from models.user import User
from models.image import Image
from app import q

users_api_blueprint = Blueprint('users_api',
                             __name__,
                             template_folder='templates')

@users_api_blueprint.route('/', methods=['GET'])
def index():
    return "USERS API"


# sendiung email API
@users_api_blueprint.route('<img_id>/send_email', methods=['GET','POST'])
def send_email(img_id):
    # breakpoint()
    img = Image.get_or_none(Image.id == img_id)
    user = User.get_or_none(User.id == img.user_id)
    q.enqueue(send, user)
    return redirect(url_for('donation.new_checkout',img_id=img_id))

def send(user):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    data = {
    "personalizations": [
        {
        "to": [
            {
            "email": user.email
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