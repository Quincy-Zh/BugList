# coding: utf-8
# app/main/views.py

from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.widgets import TextArea
#from wtforms.validators import Required, Length, Regexp, EqualTo
#from wtforms import ValidationError
from ..models import Bug, Product, User, Progress, Source

class BugForm(FlaskForm):
    #product = SelectField(u'归属产品', coerce=int)
    source = SelectField(u'问题来源', coerce=int)
    product = StringField(u'归属产品')
    #source = StringField(u'问题来源')
    
    version = StringField(u'版本')
    handler = SelectField(u'处理工程师', coerce=int)
    progress = SelectField(u'进展', coerce=int)
    
    text = StringField(u'问题描述', widget=TextArea())
    ca = StringField(u'原因分析', widget=TextArea())
    cm = StringField(u'问题对策', widget=TextArea())
    
    remark = StringField(u'备注')
    submit = SubmitField(u'提交')
    
    def __init__(self, *args, **kwargs):
        super(BugForm, self).__init__(*args, **kwargs)
        self.handler.choices = [(user.id, '%s' % user.name if user.name is not None else user.name) for user in User.query.filter_by(disable=False).order_by(User.name).all()]
        self.progress.choices = [(p.id, p.text) for p in Progress.query.all()]
        
        #self.product.choices = [(product.id, '%s / %s' % (product.title, product.spec)) for product in Product.query.order_by(Product.title.desc()).all()]
        self.source.choices = [(s.id, s.text) for s in Source.query.all()]

class BatchForm(FlaskForm):
    #product = SelectField(u'归属产品', coerce=int)
    product = StringField(u'归属产品')
    source = SelectField(u'问题来源', coerce=int)
    version = StringField(u'版本')
    reporter = SelectField(u'报告人', coerce=int)
    handler = SelectField(u'处理工程师', coerce=int)
    progress = SelectField(u'进展', coerce=int)
    
    text = StringField(u'粘贴区域', widget=TextArea())
    
    submit = SubmitField(u'提交')
    
    def __init__(self, *args, **kwargs):
        super(BatchForm, self).__init__(*args, **kwargs)
        #self.product.choices = [(product.id, '%s / %s' % (product.title, product.spec)) for product in Product.query.order_by(Product.title.desc()).all()]
        self.handler.choices = [(user.id, '%s' % user.name if user.name is not None else user.name) for user in User.query.order_by(User.name).all()]
        self.reporter.choices = [(user.id, '%s' % user.name if user.name is not None else user.name) for user in User.query.order_by(User.name).all()]
        self.progress.choices = [(p.id, p.text) for p in Progress.query.all()]
        self.source.choices = [(s.id, s.text) for s in Source.query.all()]

class FilterForm(FlaskForm):
    product = SelectField(u'归属产品', coerce=int)
    progress = SelectField(u'进展', coerce=int)
    
    submit = SubmitField(u'过滤')
    
    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.product.choices = [(product.id, product.title) for product in Product.query.group_by(Product.title).all()]
        self.progress.choices = [(p.id, p.text) for p in Progress.query.all()]
        
class CommentForm(FlaskForm):
    text = StringField(u'发表评论', widget=TextArea())
    submit = SubmitField(u'提交')