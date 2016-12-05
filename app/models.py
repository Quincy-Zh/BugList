# coding: utf-8
# app/models.py

import os

from flask import current_app
from . import db
from . import login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class SystemSettings(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    value = db.Column(db.String(64))
    
    def __repr__(self):
        return '<Settings [%r]: [%r]>' % (self.title, self.value)
    
class Bug(db.Model):
    __tablename__ = 'bugs'
    id = db.Column(db.Integer, primary_key=True, autoincrement='ignore_fk')
    
    # 所属产品
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    # 问题来源
    source_id = db.Column(db.Integer, db.ForeignKey('source.id'))
    # 版本
    version = db.Column(db.String(64))
    
    # 报告人
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # 问题处理人
    handler_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 描述
    text = db.Column(db.String(1024))
    # 原因分析
    ca = db.Column(db.String(1024))
    # 对策
    cm = db.Column(db.String(1024))
    # 处理进展
    progress_id = db.Column(db.Integer, db.ForeignKey('progress.id'))
    
    date_submit = db.Column(db.DateTime, default=datetime.now)
    date_update = db.Column(db.DateTime, default=datetime.now)
    
    remark = db.Column(db.String(128))
    deleted = db.Column(db.Boolean, default=False)
    
    records = db.relationship('Record', backref='bug')
    comments = db.relationship('Comment', backref='bug')
    
    def __repr__(self):
        return '<Bug %d[%r]>' % (self.id, self.text[:16])

class Permission:
    REPORT = 0x01  ## 报告（提交）问题
    HANDLE = 0x02  ## 处理问题，提出对策
    ADMINISTER = 0x04 ## 管理员
    
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.Integer)
    
    users = db.relationship('User', backref='role') 
    
    def __repr__(self):
        return '<Role %r>' % self.name
    
    @staticmethod 
    def insert_roles():
        roles = {
            u'报告员': (Permission.REPORT, True),
            u'工程师': (Permission.REPORT | Permission.HANDLE, False),
            u'管理员': (0xff, False)
        }
        
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            
            db.session.add(role)
        db.session.commit()
        
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64))
    
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    
    reported = db.relationship('Bug',
        foreign_keys=[Bug.reporter_id],
        backref=db.backref('reporter', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan')
        
    handled = db.relationship('Bug',
        foreign_keys=[Bug.handler_id],
        backref=db.backref('handler', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan')
    
    disable = db.Column(db.Boolean, default=False)
    records = db.relationship('Record', backref='user')
    comments = db.relationship('Comment', backref='user')
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        
        if self.role is None:
            if self.email == current_app.config['ADMINISTER']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
                
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.name

    def can(self, permissions): 
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions 
 
    def is_administrator(self): 
        return self.can(Permission.ADMINISTER)
        
class AnonymousUser(AnonymousUserMixin): 
    def can(self, permissions): 
        return False 
 
    def is_administrator(self): 
        return False 
 
login_manager.anonymous_user = AnonymousUser

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    spec = db.Column(db.String(64))
    bugs = db.relationship('Bug', backref='product', uselist=False)
    
    def __repr__(self):
        return '<Product %r[%r]>' % (self.title, self.spec)
        
class Progress(db.Model):
    __tablename__ = 'progress'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(64))
    bugs = db.relationship('Bug', backref='progress')
    
    def __repr__(self):
        return '<Progress %r>' % (self.text)
    
    @staticmethod 
    def insert_data():
        progress = (
            u'未处理',
            u'处理中',
            u'验证中',
            u'不处理',
            u'已完成',
            u'以挂起',
        )
        
        for text in progress:
            p = Progress.query.filter_by(text=text).first()
            if p is None:
                p = Progress(text=text)
                db.session.add(p)
        db.session.commit()
        
class Source(db.Model):
    __tablename__ = 'source'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(64))
    bugs = db.relationship('Bug', backref='source')
    
    def __repr__(self):
        return '<Source %r>' % (self.text)
        
    @staticmethod 
    def insert_data():
        progress = (
            u'设计开发',
            u'样机试装',
            u'生产组装',
            u'工程反馈',
            u'用户反馈',
        )
        
        for text in progress:
            p = Source.query.filter_by(text=text).first()
            if p is None:
                p = Source(text=text)
                db.session.add(p)
        db.session.commit()

class Record(db.Model):
    __tablename__ = 'records'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(64))
    bug_id = db.Column(db.Integer, db.ForeignKey('bugs.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    date_submit = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return '<Source %r>' % (self.text)

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(512))
    
    bug_id = db.Column(db.Integer, db.ForeignKey('bugs.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    date_submit = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return '<Source %r>' % (self.text)

