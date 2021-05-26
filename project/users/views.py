from flask import (render_template, redirect,flash,
        url_for,Blueprint, request,current_app, abort,session)
from project.users.forms import (RegisterForm, LoginForm, UpdateForm,
        RequestResetForm, ResetPasswordForm)
from project.models import User, Event, generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from project import db, mail
from project.users.pic_handler import pic_saver
import os
from flask_mail import Message
from flask_dance.contrib.google import make_google_blueprint, google
import secrets
import requests


users = Blueprint('users',__name__)

google_blueprint = make_google_blueprint(client_id=os.environ.get('CLIENT_ID'),
        client_secret=os.environ.get('CLIENT_SECRET'), offline=True,
        scope=['openid', 'email', 'profile'],
        redirect_to='users.google_login')

@users.route('/register', methods=['POST','GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegisterForm()

    if form.validate_on_submit():
        user = User(
                username = form.username.data,
                email = form.email.data,
                password = form.password.data
                )
        db.session.add(user)
        db.session.commit()
        flash(f'Account Successfully Created for {form.username.data}','success')
        return redirect(url_for('users.login')) 
    return render_template('register.html',title='Register',form=form)

@users.route('/login',methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.email_varified:
                send_email(user,'Varify Account',link='users.verify_email')
                session['username'] = user.username
                return redirect(url_for('users.verify'))
            login_user(user,remember=form.remember.data)
            next = request.args.get('next')
            if not next or next[0] != '/':
                next = url_for('main.home')
            return redirect(next)
        else:
            flash('Username or Password is incorrect','danger')
    return render_template('login.html',title='Login',form=form)

@users.route('/google')
def google_login():
    next = request.args.get('next')
    print(f'\n {next} \n')
    if current_user.is_authenticated:
        logout(current_user)
    if not google.authorized:
        return redirect(url_for('google.login'))

    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        response = resp.json()
        user = User.query.filter_by(email=response['email']).first()
        if not user:
            r = requests.get(response['picture'])
            filename = f'{response["id"]}.jpg'
            loc = os.path.join(current_app.root_path,'static/profile_pics',filename)
            with open(loc, 'wb') as f:
                f.write(r.content)
            user = User(
                username = response['name'],
                email = response['email'],
                password = secrets.token_hex(12),
                image_file = filename
                )
            db.session.add(user)
            db.session.commit()
        login_user(user)
        return redirect(url_for('main.home'))

    else:
        flash('Something went Wrong','danger')
        return redirect(url_for('users.login'))



@users.route('/verification')
def verify():
    if session.get('username'):
        return render_template('verify.html', username=session['username'])
    else:
        abort(403)

@users.route('/verification/<token>', methods=['POST', 'GET'])
def verify_email(token):
    if current_user.is_authenticated:
        logout(current_user)
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.login'))
    user.email_varified = True
    db.session.commit()
    login_user(user)
    return redirect(url_for('main.home'))



@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route('/account',methods = ['POST','GET'])
@login_required
def account():
    image_file = url_for('static',filename='profile_pics/'+current_user.image_file)
    form = UpdateForm()
    if form.validate_on_submit():
        if form.picture.data:
            old_image = current_app.root_path+image_file
            image_file = pic_saver(form.picture.data,current_user.username)
            current_user.image_file = image_file
            if 'default.jpg' not in old_image: 
                os.remove(old_image)
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account is updated','success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html',title='Account',image_file=image_file,form=form)

def send_email(user,message,link):
    token = user.get_reset_token()
    msg = Message(f'{message}',
            sender='noreply@flasklogin.com',
            recipients=[user.email])
    url = url_for(link, token=token, _external=True)   
    msg.html=render_template('reset.html', message=message, url=url)
    mail.send(msg)

@users.route('/reset_password', methods=['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_email(user,'reset password',link='users.reset_token')
        flash('An email as been send with reset password link to your mail', 'info')
        return redirect(url_for('users.login'))

    return render_template('reset_request.html', title='Reset Password',form=form)

@users.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password = generate_password_hash(form.password.data)
        user.password_hash = password
        user.email_varified = True
        db.session.commit()
        flash('Your Password successfully updated','success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
        
