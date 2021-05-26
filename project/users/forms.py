from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from project.models import User
from flask_login import current_user
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Email,DataRequired,EqualTo,Length,ValidationError

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),Length(min=3,max=15)])
    email = StringField('Email',validators=[
        DataRequired(),Email()])
    password = PasswordField('Password',validators=[
        DataRequired(),Length(min=8),EqualTo('confirm_password',
            message='Password must be match')])
    confirm_password = PasswordField('Confirm Passowrd',validators=[
        DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        if len(username.data) > 19:
            raise ValidationError('character limit exceeded')

        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Username already exist')

    def validate_email(self,email):
        if len(email.data) > 49:
            raise ValidationError('character limit exceeded')

        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Email already exist')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),Email()])
    password = PasswordField('Password',validators=[
        DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),Length(min=3,max=15)])
    email = StringField('Email',validators=[
        DataRequired(),Email()])
    picture = FileField('Update Profile Picture',validators=[
        FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_username(self,username):
        if current_user.username != username.data: 
            if User.query.filter_by(username=username.data).first():
                raise ValidationError('Username already exist')

        if len(username.data) > 19:
            raise ValidationError('character limit exceeded')

    def validate_email(self,email):
        if current_user.email != email.data: 
            if User.query.filter_by(email=email.data).first():
                raise ValidationError('Email already exist')

        if len(email.data) > 49:
            raise ValidationError('character limit exceeded')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')
    
    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is None:
            raise ValidationError('There is no account with this email')

        if len(field.data) > 49:
            raise ValidationError('character limit exceeded')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('confirm_password')])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired()])
    submit = SubmitField('Reset Password')
