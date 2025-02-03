from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms import TextAreaField

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ChallengeForm(FlaskForm):
    challenge_type = StringField('Challenge Type', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    tags = StringField('Tags (comma separated)')
    image = FileField('Challenge Image (optional)')
    badges = SelectMultipleField('Select Badge(s)', choices=[], coerce=str)
    goals = TextAreaField('Goals (one per line)', validators=[DataRequired()])
    submit = SubmitField('Create Challenge')

class ChatForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired()])
    chat_image = FileField('Upload Image (optional)')
    submit = SubmitField('Send')
