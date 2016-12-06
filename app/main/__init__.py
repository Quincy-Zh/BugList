# coding: utf-8
# app/main/__init__.py

from flask import Blueprint
from ..models import Permission

MAX_LINE_LENGTH = 30
main = Blueprint('main', __name__)

from . import views, errors

@main.app_template_filter()
def format_datetime(value):
    return value.strftime('%Y-%m-%d %H:%M')
    
@main.app_template_filter()
def summary(html_text):
    start = html_text.find('<p>')
    end = html_text.find('</p>')
    if start >= 0 and end > 3:
        if end > MAX_LINE_LENGTH:
            end  = MAX_LINE_LENGTH
        pos1 = html_text.find(u'。')
        if pos1 > -1 and pos1 < end:
            end = pos1
            
        txt = html_text[start+3: end] + ' ...'
    else:
        txt = html_text[: MAX_LINE_LENGTH].strip() + ' ...'
    
    return txt

@main.app_context_processor 
def inject_permissions(): 
    return dict(Permission=Permission)