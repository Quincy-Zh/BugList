# coding: utf-8
# app/main/views.py

import os
from datetime import datetime
import random

from flask import current_app, render_template, request, redirect, url_for, flash, send_from_directory, make_response, jsonify
from . import main
from .. import db
from ..models import User, Bug, Record, \
    Product, Comment, Source, Progress, \
    Permission, SystemSettings, Role
from ..decorators import admin_required, permission_required 
from .forms import BugForm, BatchForm, FilterForm, CommentForm

from flask_login import login_required, current_user

def safe_filename(filename):
    a='qwertyuiopasdfghjklmnbvcxz1234567890'
    
    return 'U{0}{1}.{2}'.format(
        datetime.now().strftime('%Y%m%d%H%M%S'),
        ''.join(random.choice(a) for i in range(6)),
        filename.rsplit('.', 1)[1])

@main.before_app_first_request
def _before_first_request():
    initialized = SystemSettings.query.filter_by(title='initialized').first()
    
    if not initialized:
        Role.insert_roles()
        Progress.insert_data()
        Source.insert_data()
        
        initialized = SystemSettings(title='initialized', value='1')
        db.session.add(initialized)
        db.session.commit()
    
@main.route('/')
def index():
    
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
        query = Bug.query.filter(Bug.product_id==product_id)
    else:
        query = Bug.query
    
    if progress_id != -1:
        query = query.filter(Bug.progress_id == progress_id)
        
    pagination = query.paginate(page, 
        per_page=current_app.config['MATERIAL_COUNT_PER_PAGE'],
        error_out=False)
    bugs = pagination.items
    
    return render_template('main/index.html', 
        products=Product.query.all(),
        product_id=product_id,
        progs=Progress.query.all(), 
        progress_id=progress_id,
        bugs=bugs, 
        pagination=pagination)

@main.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = BugForm()
    
    if request.method == 'GET': 
        try:
            # 从cookies载入上一次提交时的某些设置
            form.source.data = int(request.cookies.get('source_last_submit'))
            form.product.data = request.cookies.get('product_last_submit')
            form.version.data = request.cookies.get('version_last_submit')
            form.handler.data = int(request.cookies.get('handler_last_submit'))
            form.progress.data = int(request.cookies.get('progress_last_submit'))
        except:
            pass
            
        # 默认负责人为自己
        if not form.handler.data:
            form.handler.data = current_user.id
        
    if form.validate_on_submit():
        product = Product.query.filter_by(title=form.product.data).first()
        if not product:
            product = Product(title=form.product.data)
            db.session.add(product)
            db.session.commit()
            
        bug = Bug(product_id=product.id, 
            reporter_id=current_user.id,
            handler_id=form.handler.data,
            text=form.text.data,
            ca=form.ca.data,
            cm=form.cm.data,
            progress_id=form.progress.data,
            source_id=form.source.data,
            version=form.version.data)
        
        db.session.add(bug)
        db.session.commit()
        
        rec = Record(text=u'创建', bug=bug, user=current_user)
        db.session.add(rec)
        db.session.commit()
        
        flash(u'内容已经保存')
        
        # 保存最近的输入项
        resp = make_response(redirect(url_for('.create')))
        resp.set_cookie('username', 'the username')
        
        resp.set_cookie('source_last_submit', str(form.source.data))
        resp.set_cookie('product_last_submit', form.product.data)
        resp.set_cookie('version_last_submit', form.version.data)
        resp.set_cookie('handler_last_submit', str(form.handler.data))
        resp.set_cookie('progress_last_submit', str(form.progress.data))
        
        return resp
        
    return render_template('main/create.html', form=form)

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    bug = Bug.query.get_or_404(id)
    form = BugForm()
    
    if request.method == 'GET':
        form.product.data = bug.product.title	
        form.handler.data = bug.handler_id	
        form.text.data = bug.text	    
        form.ca.data = bug.ca	        
        form.cm.data = bug.cm	        
        form.progress.data = bug.progress_id	
        form.source.data = bug.source_id	
        form.version.data = bug.version	    
    
    else:
        if form.validate_on_submit():
            product = Product.query.filter_by(title=form.product.data).first()
            if not product:
                product = Product(title=form.product.data)
                db.session.add(product)
                db.session.commit()
            
            bug.product_id = product.id
            bug.handler_id = form.handler.data
            bug.text = form.text.data
            bug.ca = form.ca.data
            bug.cm = form.cm.data
            bug.progress_id = form.progress.data
            bug.source_id = form.source.data
            bug.version = form.version.data
            bug.date_update = datetime.now()
        
            rec = Record(text=u'更新', bug=bug, user=current_user)
            
            db.session.add(bug)
            db.session.commit()
        
            flash(u'内容已经保存')
            
            return redirect(url_for('.details', id=bug.id))
            
    return render_template('main/edit.html', form=form)
    
@main.route('/details/<int:id>', methods=['GET', 'POST'])
def details(id):
    form = CommentForm()
    bug = Bug.query.get_or_404(id)
    
    if form.validate_on_submit():
        c = Comment(text=form.text.data,
            bug_id=bug.id,
            user_id=current_user.id)
        db.session.add(c)
        db.session.commit()
        
        return redirect(url_for('.details', id=bug.id))
        
    next_bug = Bug.query.filter(Bug.id>id).first()
    
    return render_template('main/details.html', 
        bug=bug, form=form, 
        next_id=next_bug.id if next_bug else None)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']
           
@main.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'myFileName' not in request.files:
            return u"error|服务器端错误1"
            
        file = request.files['myFileName']
        if file.filename == '':
            return u"error|服务器端错误2"
            
        if file and allowed_file(file.filename):
            filename = safe_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            return url_for('.attch', path=filename) #, _external=True)
            
    return u'''<!doctype html>
<title>Upload new File</title>
<h1>上传文件</h1>
<form action="" method="post" enctype="multipart/form-data">
  <input type="file" name="myFileName">
  <input type="submit" value="Upload">
</form>'''
           
@main.route('/attch/<path>')
def attch(path):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], path)

@main.route('/batch', methods=['GET', 'POST'])
@login_required
def batch():
    form = BatchForm()
        
    if form.validate_on_submit():
        lines = form.text.data.split('\n')
        count = 0
        bugs = []
        for line in lines:
            line = line.strip()
            
            if len(line) == 0:
                continue
                
            items = line.split('\t')
            if len(items) != 3:
                flash(u'格式错误 %d' % len(items))
                
                return render_template('main/batch.html', form=form)
                
            bug = Bug(product_id=form.product.data, 
                reporter_id=form.reporter.data,
                handler_id=form.handler.data,
                text=items[0],
                ca=items[1],
                cm=items[2],
                progress_id=form.progress.data,
                source_id=form.source.data,
                version=form.version.data)
                
            bugs.append(bug)
            count += 1
            
        for bug in bugs:
            db.session.add(bug)
            db.session.commit()
        
            rec = Record(text=u'批量导入', bug=bug, user=current_user)
            
            db.session.add(rec)
            db.session.commit()
        
        flash(u'已经导入 %d 条记录' % count)
        
        return redirect(url_for('.index'))
        
    return render_template('main/batch.html', form=form)
    
@main.route('/settings', methods=['GET', 'POST'])
@login_required
#@admin_required
def settings():
    if not current_user.can(Permission.ADMINISTER):
        flash(u'权限受限，不能修改系统设置')
        return redirect(url_for('.index'))
        
    if request.method == 'POST':
        value = request.form.get('value', '') #] if request.form.has_key('value') else ''
        action = request.form.get('action', '') # if request.form.has_key('action') else ''
        cmd = request.form['cmd']
        
        if action == 'add':
            if cmd == 'source':
                item = Source.query.filter_by(text=value).first()
                if not item:
                    item = Source(text=value)
                    db.session.add(item)
                    db.session.commit()
                    
                    response = make_response(jsonify({'result': 'ok'}))
                else:
                    response = make_response(jsonify({'err_msg': u'内容已存在'}))
            elif cmd == 'progress':
                item = Progress.query.filter_by(text=value).first()
                if not item:
                    item = Progress(text=value)
                    db.session.add(item)
                    db.session.commit()
                    
                    response = make_response(jsonify({'result': 'ok'}))
                else:
                    response = make_response(jsonify({'err_msg': u'内容已存在'}))
        elif action == 'del':
            if cmd == 'source':
                item = Source.query.filter_by(text=value).first()
            elif cmd == 'progress':
                item = Progress.query.filter_by(text=value).first()
                
            if item:
                db.session.delete(item)
                db.session.commit()
                
                response = make_response(jsonify({'result': 'ok'}))
            else:
                response = make_response(jsonify({'err_msg': u'内容不存在'}))
        
        else:
            if cmd == 'source':
                items = Source.query.all()
            elif cmd == 'progress':
                items = Progress.query.all()
                
            if items:
                response = make_response(jsonify({'result': 'ok', 'items': [(item.id, item.text) for item in items]}))
            else:
                response = make_response(jsonify({'err_msg': u'内容不存在'}))
                
        return response
        
    return render_template('main/settings.html')
    
@main.route('/product_list')
def product_list():
    keyword = request.args.get('term', '')
    products = Product.query.filter(Product.title.like('%{0}%'.format(keyword))).all()
    response = make_response(jsonify(['{0}'.format(p.title) for p in products]))
    
    # 跨域访问
    # response.headers['Access-Control-Allow-Origin'] = '*'
    # response.headers['Access-Control-Allow-Methods'] = 'POST'
    # response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type' 

    return response
    