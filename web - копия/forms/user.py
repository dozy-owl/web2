from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField
from wtforms import SubmitField, EmailField
from wtforms.validators import DataRequired
from flask import Flask
from flask import render_template


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль',
                                   validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')
