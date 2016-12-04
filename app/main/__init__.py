# coding: utf-8
# app/main/__init__.py

from flask import Blueprint
from ..models import Permission

main = Blueprint('main', __name__)

from . import views, errors

@main.app_template_filter()
def format_datetime(value):
    return value.strftime('%Y-%m-%d %H:%M:%S')
    
@main.app_template_filter()
def summary(html_text):
    start = html_text.find('<p>')
    end = html_text.find('</p>')
    if start > -1 and end > 3:
        txt = html_text[start+3: end]
    else:
        txt = html_text
    
    return txt[: 20].strip()

@main.app_context_processor 
def inject_permissions(): 
    return dict(Permission=Permission)