import sys
import os
import base64
 
INTERP = os.path.expanduser("/home/gsbq8115mkly/Human-Family-Team/venv/bin/python3")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
 
sys.path.insert(0, os.path.dirname(__file__))
 
from oce import create_app
from flask import render_template, session
from oce.utils.db_interface import close_db, get_user_by_uuid
 
app = create_app()
 
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
 
application = app