# coding: utf-8
# app/__init__.py

from flask import Flask
from flask_bootstrap import Bootstrap, WebCDN
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    
    app.config.from_object(config[config_name])
    
    config[config_name].init_app(app)
    
    bootstrap.init_app(app)
    
    if app.config.has_key('USER_DEF_CDN_BOOTSTRAP'):
        cdn_bootstrap = WebCDN(app.config['USER_DEF_CDN_BOOTSTRAP'])
        app.extensions['bootstrap']['cdns']['bootstrap'] = cdn_bootstrap
        
        
    if app.config.has_key('USER_DEF_CDN_JQUERY'):
        cdn_jquery = WebCDN(app.config['USER_DEF_CDN_JQUERY'])
        app.extensions['bootstrap']['cdns']['jquery'] = cdn_jquery
    
    db.init_app(app)
    login_manager.init_app(app)
    
    # 附加路由和自定义的错误页面
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    return app