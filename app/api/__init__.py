# coding: utf-8
# app/api/__init__.py

from flask import Blueprint

api = Blueprint('api', __name__)

from . import views
