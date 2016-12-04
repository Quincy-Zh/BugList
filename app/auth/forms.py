# coding: utf-8
# app/auth/views.py

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, EqualTo, ValidationError
from ..models import User

class LoginForm(Form):
    email = StringField(u'E-mail', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField(u'保持登录')
    
    submit = SubmitField(u'登录')

class RegistrationForm(Form):
    name = StringField(u'姓名', validators=[Required(), Length(1, 64)])
    email = StringField(u'E-mail', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[Required(), Length(6, 64), EqualTo('password2', message=u'两次输入的密码不一致')])
    password2 = PasswordField(u'再次确认密码', validators=[Required()]) 
    
    submit = SubmitField(u'注册')
 
    def validate_email(self, field): 
        if User.query.filter_by(email=field.data).first(): 
            raise ValidationError(u'Email 已经注册') 
 
    def validate_name(self, field): 
        if User.query.filter_by(name=field.data).first(): 
            raise ValidationError(u'用户名已经注册')