from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Optional
from flask_login import current_user
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                          validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                            validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                    validators=[DataRequired(), EqualTo('password')])
    location = StringField('Location (Optional)',
                           validators=[Optional(), Length(max=100)])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                            validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                          validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    location = StringField('Location',
                          validators=[Optional(), Length(max=100)])
    profile_pic = FileField('Update Profile Picture')
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class SkillForm(FlaskForm):
    skill_type = SelectField('Skill Type', 
                           choices=[('offer', 'Skill Offered'), ('wanted', 'Skill Wanted')],
                           validators=[DataRequired()])
    name = StringField('Skill Name',
                      validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description',
                               validators=[Optional(), Length(max=500)])
    proficiency = SelectField('Proficiency Level',
                            choices=[('beginner', 'Beginner'),
                                     ('intermediate', 'Intermediate'),
                                     ('advanced', 'Advanced')],
                            validators=[Optional()])
    submit = SubmitField('Add Skill')

class AvailabilityForm(FlaskForm):
    day = SelectField('Day',
                     choices=[('Monday', 'Monday'),
                              ('Tuesday', 'Tuesday'),
                              ('Wednesday', 'Wednesday'),
                              ('Thursday', 'Thursday'),
                              ('Friday', 'Friday'),
                              ('Saturday', 'Saturday'),
                              ('Sunday', 'Sunday')],
                     validators=[DataRequired()])
    time_range = SelectField('Time Range',
                           choices=[('Morning', 'Morning (8AM-12PM)'),
                                   ('Afternoon', 'Afternoon (12PM-5PM)'),
                                   ('Evening', 'Evening (5PM-9PM)'),
                                   ('Weekend', 'Weekend')],
                           validators=[DataRequired()])
    submit = SubmitField('Add Availability')

class SwapRequestForm(FlaskForm):
    message = TextAreaField('Message (Optional)',
                           validators=[Optional(), Length(max=500)])
    submit = SubmitField('Send Request')

class RatingForm(FlaskForm):
    rating = IntegerField('Rating',
                         validators=[DataRequired(),
                                    NumberRange(min=1, max=5, message='Rating must be between 1 and 5')])
    comment = TextAreaField('Comment (Optional)',
                           validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Rating')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
                            validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')