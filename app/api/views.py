# coding: utf-8
# app/main/views.py

import os
from datetime import datetime
import random

from flask import current_app, request, redirect, url_for, make_response, jsonify
from . import api
#from .. import db
from ..models import User, Bug, Record, \
    Product, Comment, Source, Progress, \
    Permission, SystemSettings, Role
from ..decorators import admin_required, permission_required 
#from .forms import BugForm, BatchForm, FilterForm, CommentForm

from flask_login import login_required, current_user

    
@api.route('/list/<title>')
def list(title):
    items = None
    
    if title.lower() == 'product':
        keyword = request.args.get('term', '')
        products = Product.query.filter(Product.title.like(u'%{0}%'.format(keyword))).all()
        items = [{'id': p.id, 'title': p.title} for p in products]
        result = {'items': items, 'title': title}
    elif title.lower() == 'source':
        items = [{'id': s.id, 'title': s.text} for s in Source.query.all()]
        result = {'items': items, 'title': title}
    elif title.lower() == 'progress':
        items = [{'id': s.id, 'title': s.text} for s in Progress.query.all()]
        result = {'items': items, 'title': title}
    elif title.lower() == 'bugs':
        try:
            product_id = int(request.args.get('product'))
        except:
            product_id = -1
            
        try:
            progress_id = int(request.args.get('progress'))
        except:
            progress_id = -1
            
        try:
            page = int(request.args.get('page'))
        except:
            page = 1
            
        if product_id != -1:
            query = Bug.query.filter(Bug.product_id==product_id).order_by(Bug.id.desc())
        else:
            query = Bug.query.order_by(Bug.id.desc())
        
        if progress_id != -1:
            query = query.filter(Bug.progress_id == progress_id)
            
        pagination = query.paginate(page, 
            per_page=current_app.config['MATERIAL_COUNT_PER_PAGE'],
            error_out=False)
            
        items = [{'id': b.id, 'text': b.text, 'product': b.product.title, 'progress': b.progress.text} for b in pagination.items]
        
        result = {'items': items, 
            'count': len(items),
            'page_size': current_app.config['MATERIAL_COUNT_PER_PAGE'],
            'page': page
            }
    else:
        current_app.logger.debug(u'"{0}" Not Found.'.format(title))
        
        result = {'errormsg': 'title not found.'}
        
    response = make_response(jsonify(result))
    
    # 跨域访问
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type' 

    return response
    