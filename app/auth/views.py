# coding: utf-8
# app/auth/views.py

import os
from flask import current_app, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
    
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash(u'已登录')            
            return redirect(request.args.get('next') or url_for('main.index'))
            
        flash(u'用户名和密码不匹配')
    return render_template('auth/login.html', form=form)
    
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'已经登出')
    
    return redirect(url_for('.login'))
    
@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.filter_by(id=current_user.id).first()
    form = RegistrationForm()
    
    if request.method == 'POST':
        if not user.verify_password(form.password.data):
            flash(u'密码不正确，信息未修改')
        else:
            user.name = form.name.data
            user.email = form.email.data
            if form.password2.data != '':
                user.password = form.password2.data
                
            db.session.commit()
        
            flash(u'信息已更新')
    else:
        form.name.data = user.name
        form.email.data = user.email
        
    return render_template('auth/profile.html', form=form)
    
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data,
                    password = form.password.data, 
                    email = form.email.data)
        db.session.add(user)
        db.session.commit()
        
        flash(u'注册成功')
        
        login_user(user, False)
        
        return redirect(request.args.get('next') or url_for('main.index'))
        
    return render_template('auth/register.html', form=form)
    