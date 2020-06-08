from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, TextField, HiddenField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0,max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class StreamingForm(FlaskForm):
    title = TextField('Title', validators=[
        DataRequired(), Length(min=1, max=140)])
    origin = TextField('Origin', validators=[
        DataRequired(), Length(min=1, max=1024)])
    server = TextField('Server', validators=[
        DataRequired(), Length(min=1, max=140)])
    stream_key = TextField('Stream Key', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit_start = SubmitField('Launch 🚀')

    def validate_origin(self, field):
        if 'youtu' not in field.data and 'm3u8' not in field.data and 'rtmp' not in field.data:
            raise ValidationError('Not a valid input')

    def validate_server(self, field):
        if 'rtmp' not in field.data and 'rtmps' not in field.data:
            raise ValidationError('Not a valid server')

class StopForm(FlaskForm):
    submit_stop = SubmitField('Stop')
    fld1 = HiddenField('Field 1')