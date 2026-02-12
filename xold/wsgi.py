from oce import create_app
from flask import render_template
from flask import session
#from flask_limiter import Limiter
#from flask_limiter.util import get_remote_address
from oce.utils.db_interface import close_db

app = create_app()
#limiter = Limiter(get_remote_address, app=app)

if __name__ == '__main__':
    app.run()

@app.route('/')
#@limiter.limit("5/minute")
def home():
  return render_template('index.html')

from oce.utils.db_interface import get_user_by_uuid

@app.context_processor
def inject_user():
    user = None
    if 'user_uuid' in session:
        user = get_user_by_uuid(session['user_uuid'])
    return dict(logged_in_user=user)

import base64

@app.template_filter('b64encode')
def b64encode_filter(data):
    if isinstance(data, bytes):
        return base64.b64encode(data).decode('utf-8')
    return ''

app.teardown_appcontext(close_db)