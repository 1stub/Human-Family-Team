import sys
import os
import base64

# Make sure the app folder is on the Python path
sys.path.insert(0, os.path.dirname(__file__))

from oce import create_app
from flask import render_template, session
from oce.utils.db_interface import close_db, get_user_by_uuid
from werkzeug.middleware.proxy_fix import ProxyFix

app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

@app.route('/')
def home():
    return render_template('index.html')

@app.context_processor
def inject_user():
    user = None
    if 'user_uuid' in session:
        user = get_user_by_uuid(session['user_uuid'])
    return dict(logged_in_user=user)

@app.template_filter('b64encode')
def b64encode_filter(data):
    if isinstance(data, bytes):
        return base64.b64encode(data).decode('utf-8')
    return ''

app.teardown_appcontext(close_db)

# WSGI entry point for Passenger
application = app