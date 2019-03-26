from flask import Blueprint, render_template
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
from models.donation import Donation
from helpers import s3
from config import S3_BUCKET
# for google oauth
import os
from instagram_web.helpers.google_oauth import oauth
import config

import braintree


def generate_client_token():
    return gateway.client_token.generate()

def transact(options):
    return gateway.transaction.sale(options)

def find_transaction(id):
    return gateway.transaction.find(id)


gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=os.environ.get('use_your_merchant_id'),
        public_key=os.environ.get('use_your_public_key'),
        private_key=os.environ.get('use_your_private_key')
    )
)

donation_blueprint = Blueprint('donation',
                            __name__,
                            template_folder='templates')

@donation_blueprint.route('/new/<img_id>', methods=['GET'])
def new_checkout(img_id):
    client_token = generate_client_token()
    return render_template('donation/new.html', client_token=client_token,img_id=img_id)


@donation_blueprint.route('/', methods=['POST'])
def create():
    pass


@donation_blueprint.route('/<username>', methods=["GET"])
def show(username):
    pass


@donation_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"


@donation_blueprint.route('/<id>/edit', methods=['GET'])
def edit(id):
    pass


@donation_blueprint.route('/<id>', methods=['POST'])
def update(id):
    pass



@app.route('/checkouts/<img_id>', methods=['POST'])
def create_checkout(img_id):
    result = transact({
        'amount': request.form['amount'],
        'payment_method_nonce': request.form['payment_method_nonce'],
        'options': {
            "submit_for_settlement": True
        }
    })

    if result.is_success or result.transaction:
        d = Donation(value=request.form['amount'],img_id=img_id)
        d.save()
        return redirect(url_for('users_api.send_email' ,img_id=img_id))
    else:
        return 'failed'
        # for x in result.errors.deep_errors: flash('Error: %s: %s' % (x.code, x.message))
        # return redirect(url_for('new_checkout'))

