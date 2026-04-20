from flask import Blueprint, render_template, send_file, request, jsonify, redirect, url_for, flash, session, current_app
from oce.utils.db_interface import create_post, get_post_by_uuid, create_user, get_user_by_email
import base64
from oce.utils.db_interface import get_user_by_uuid, delete_post
from oce.utils.models import User
from flask_dance.contrib.github import github, make_github_blueprint
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.session import BaseStorage
from flask_dance.contrib.google import google as google_oauth, make_google_blueprint
from dotenv import load_dotenv
load_dotenv()
import os
import stripe
import json
import re
from .. import password_hasher #argon2
from flask_mail import Message
from .. import mail #mail from _init_.py
from oce.utils import db_interface
from datetime import datetime

class SessionStorage(BaseStorage):
    def __init__(self, session_key="flask_dance_token"):
        super().__init__()
        self.session_key = session_key

    def get(self, blueprint):
        print("Getting token from session:", session.get(self.session_key))
        return session.get(self.session_key)

    def set(self, blueprint, token):
        print("Setting token in session:", token)
        if isinstance(token, str):  # Handle legacy string just in case
            token = {"access_token": token}
        session[self.session_key] = token

    def delete(self, blueprint):
        print("Deleting token from session")
        session.pop(self.session_key, None)

content = Blueprint('content', __name__)

#ADMINS = os.getenv('ADMINS', '').split(',')
ADMINS = [a for a in os.getenv('ADMINS', '').split(',') if a] + ['admin']

github_blueprint = make_github_blueprint(
    client_id=os.getenv('GITHUB_OAUTH_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_OAUTH_CLIENT_SECRET'),
    scope='user',
    # redirect_to='content.github_callback',
    redirect_url="/github_callback",
    storage=SessionStorage()
)
content.register_blueprint(github_blueprint, url_prefix='/github_login')

@content.route('/debug_oauth')
def debug_oauth():
    from flask import request
    return f"Base URL: {request.base_url}<br>Host URL: {request.host_url}"

google_blueprint = make_google_blueprint(
    client_id=os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
    storage=SessionStorage()
)
content.register_blueprint(google_blueprint, url_prefix='/google_login')

@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flash("Google authentication failed.", "danger")
        return False

    try:
        resp = google_oauth.get("/oauth2/v2/userinfo")
        if not resp.ok:
            flash("Could not fetch Google account info.", "danger")
            return False

        info = resp.json()
        google_id = info["id"]
        email     = info.get("email", "")
        name      = info.get("name", email.split("@")[0])

        user = db_interface.get_user_by_google_id(google_id)
        if not user:
            user = get_user_by_email(email)

        if user:
            if not user.get("google_id"):
                db_interface.update_user_google_id(user["user_uuid"], google_id)
        else:
            db_interface.create_user(
                username=name,
                email=email,
                password="",
                about_me="Role: student",
                google_id=google_id
            )
            user = get_user_by_email(email)

        session['user']      = user['username']
        session['user_uuid'] = user['user_uuid']
        flash(f"Welcome, {user['username']}!", "success")

    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Google login error: {e}", "danger")

    return False 

@content.route('/content/SignupPage', methods=['GET', 'POST'])
def signup():  # ← Function name MUST be 'signup' to match url_for('content.signup')
    if request.method == 'POST':
        try:
            # Get form data - match the new HTML field names
            username = request.form.get('name', '').strip()  # 'name' not 'username'
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            role = request.form.get('role', '').strip()  # 'role' not 'about_me'

            # Basic validation
            if not username or not email or not password or not role:
                flash("All fields are required.", "danger")
                return redirect(url_for('content.signup'))

            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash("Invalid email format.", "danger")
                return redirect(url_for('content.signup'))

            # Validate role
            if role not in ['student', 'family', 'teacher']:
                flash("Invalid role selected.", "danger")
                return redirect(url_for('content.signup'))

            # Check duplicate email
            if get_user_by_email(email):
                flash("Email already registered.", "warning")
                return redirect(url_for('content.signup'))

            # Create user - store role in about_me
            create_user(
                username=username,
                email=email,
                password=password,
                about_me=f"Role: {role}"
            )

            flash("Signup successful! You can now log in.", "success")
            return redirect(url_for('content.login'))

        except Exception as e:
            import traceback
            traceback.print_exc()
            flash(f"An error occurred during signup: {e}", "danger")
            return redirect(url_for('content.signup'))

    # GET request - render the signup page
    return render_template('SignupPage.html')

@content.route('/content/success')
def success():
  return render_template('success.html')

@content.route('/content/block1')
def block1():
  return render_template('block1.html')

@content.route('/content/block2')
def block2():
  return render_template('block2.html')

@content.route('/content/block3')
def block3():
  return render_template('block3.html')

@content.route('/content/block4')
def block4():
  return render_template('block4.html')

@content.route('/content/block5')
def block5():
  return render_template('block5.html')

@content.route('/content/block6')
def block6():
  return render_template('block6.html')

@content.route('/content/block7')
def block7():
  return render_template('block7.html')

@content.route('/content/block8')
def block8():
  return render_template('block8.html')

@content.route('/content/block9')
def block9():
  return render_template('block9.html')

@content.route('/content/archingblock1')
def archingblock1():
    return render_template('archingblock1.html')

@content.route('/content/archingblock2')
def archingblock2():
    return render_template('archingblock2.html')

@content.route('/content/archingblock3')
def archingblock3():
    return render_template('archingblock3.html')

@content.route('/content/archingblock4')
def archingblock4():
    return render_template('archingblock4.html')

@content.route('/content/archingblock5')
def archingblock5():
    return render_template('archingblock5.html')

@content.route('/content/archingblock6')
def archingblock6():
    return render_template('archingblock6.html')

@content.route('/content/archingblock7')
def archingblock7():
    return render_template('archingblock7.html')

@content.route('/content/archingblock8')
def archingblock8():
    return render_template('archingblock8.html')

@content.route('/content/archingblock9')
def archingblock9():
    return render_template('archingblock9.html')

@content.route('/content/keystoneblock')
def keystoneblock():
    return render_template('keystoneblock.html')

@content.route('/content/tiles/')
def tiles():
    return send_file('static/docs/Human-Domino-Effect-Footprint-Tiles.pdf', download_name='Human-Domino-Effect-Footprint-Tiles.pdf')


@content.route('/content/ConceptExchange/')
@content.route('/content/ConceptExchange/<group_id>')
def concept_exchange(group_id=None):
    con = db_interface.get_db()
    cur = con.cursor()

    # --- Determine active group ---
    if group_id == "announcement":
        posts = db_interface.get_announcements()
        active_group = "announcement"
        selected_group_name = "Announcements"
    else:
        class_year = None
        if group_id and str(group_id).isdigit():
            class_year = int(group_id)
        elif session.get("selected_class_year"):
            class_year = session["selected_class_year"]

        posts = db_interface.get_posts_for_class(class_year)
        active_group = class_year
        selected_group_name = f"Class of {class_year}" if class_year else "Concept Exchange Chat"

    # --- Sidebar groups ---
    selected_class_year = session.get("selected_class_year")
    groups = [
        {"id": "announcement", "name": "Announcements"}
    ]
    if selected_class_year:
        groups.append({
            "id": selected_class_year,
            "name": f"Class of {selected_class_year}"
        })

    print(f"[DEBUG] Showing {selected_group_name}, active_group={active_group}, posts={len(posts)}")

    return render_template(
        "mainForum.html",
        posts=posts,
        groups=groups,
        show_sidebar=True,
        active_group=active_group,
        selected_group_name=selected_group_name,
    )

@content.route('/announcements')
def announcements():
    posts = db_interface.get_announcements()
    return render_template(
        'mainForum.html',
        posts=posts,
        show_sidebar=True,
        active_group='announcements',
        is_announcement_page=True
    )


@content.route('/select_age', methods=['POST'])
def select_age():
    """Handle age selection and redirect to the appropriate Concept Exchange forum."""
    try:
        age = int(request.form.get('age', 0))
        print(f"[DEBUG] Received age from form: {age}")

        # Validate the age
        if age < 0:
            flash("Please select a valid age.", "warning")
            print("[DEBUG] Invalid age submitted — redirecting to resources.")
            return redirect(url_for('content.resources'))

        # Compute "Class of XXXX"
        current_year = datetime.now().year
        class_year = current_year + (18 - age)
        print(f"[DEBUG] Current year: {current_year}, Computed class year: {class_year}")

        # Store both in the Flask session
        session['selected_age'] = age
        session['selected_class_year'] = class_year
        session.modified = True
        print(f"[DEBUG] Session updated: {dict(session)}")

        # Redirect directly to that class group page
        return redirect(url_for('content.concept_exchange', group_id=class_year))

    except Exception as e:
        print(f"[ERROR] Exception in select_age: {e}")
        flash("An error occurred while processing your selection.", "danger")
        return redirect(url_for('content.resources'))


@content.route('/content/resources/', defaults={'selected_age': None})
@content.route('/content/resources/<int:selected_age>')
@content.route('/resources/', defaults={'selected_age': None})
@content.route('/resources/<int:selected_age>')
def resources(selected_age=None):
    # If selected_age is provided (including 0), keep it; otherwise fallback to session or None
    if selected_age is None:
        selected_age = session.get('selected_age')
    # store if not None so templates can use it
    if selected_age is not None:
        session['selected_age'] = selected_age
    return render_template('resources.html', selected_age=selected_age)

@content.route('/content/Login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return redirect(url_for('content.login'))

        user = get_user_by_email(email)
        if not user:
            flash("No account found with that email.", "danger")
            return redirect(url_for('content.login'))

        try:
            password_hasher.verify(user['password'], password)
        except Exception:
            flash("Incorrect password.", "danger")
            return redirect(url_for('content.login'))

        session['user'] = user['username']
        session['user_uuid'] = user['user_uuid']
        flash(f"Welcome back, {user['username']}!", "success")
        return redirect(url_for('content.index'))

    return render_template('LoginPage.html')

@content.route('/content/calendar/')
def calendar():
  return render_template('calendar.html')

@content.route('/content/Contact/', methods=['GET', 'POST'])
def contact():
  if request.method == 'POST':
    subject = request.form.get('inputSubject')
    name = request.form.get('inputName')
    email = request.form.get('inputEmail')
    phone = request.form.get('inputPhoneNumber')
    message = request.form.get('inputMessage')
    msg = Message(f"The Human Domino Effect Contact Page: {subject}", recipients=[email])
    msg.bcc = ["stephaniefairchildfister@gmail.com"]
    msg.body = f"This is an automatic response, but I have recieved your message. Please keep an eye out for a response from me, I will get back in touch soon!\n\n"\
    + f"Name: {name}\nEmail: {email}\nPhone Number: {phone}\n\nMessage: {message}"
    mail.send(msg)
  return render_template('ContactPage.html')

# TODO: Update shope page to instead redirect to shopify content!
@content.route('/content/Shop/')
def shop():
#   if 'user_uuid' not in session:
#         flash("Please log in to access the shop.", "warning")
#         return redirect(url_for('content.login'))
  return render_template('Shop.html')

@content.route('/create_post', methods=['POST'])
def create_post_route():
    """
    Handle AJAX post creation.
    Forces username to be the logged-in user.
    Allows announcements only for DB admins.
    """
    try:
        # Require login
        user_uuid = session.get('user_uuid')
        if not user_uuid:
            return jsonify({'success': False, 'error': 'Not logged in'}), 401

        # Fetch full user record from DB
        user = get_user_by_uuid(user_uuid)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 401

        username = user["username"]
        is_admin = user.get("is_admin", 0)

        data = request.get_json() or {}
        text_content = data.get('text_content', '').strip()
        is_announcement = bool(data.get('is_announcement', False))

        if not text_content:
            return jsonify({'success': False, 'error': 'Empty post'}), 400

        # ---- SECURE ADMIN CHECK ----
        if is_announcement and not is_admin:
            print(f"[SECURITY] Non-admin '{username}' tried posting an announcement.")
            return jsonify({'success': False, 'error': 'Forbidden - admin only'}), 403
        # -----------------------------

        # CREATE THE POST — using secure username
        post_uuid = db_interface.create_post(
            username,
            text_content,
            is_announcement=is_announcement
        )

        return jsonify({'success': True, 'post_uuid': post_uuid}), 200


    except Exception as e:
        print(f"[ERROR] Failed to create post: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@content.route('/delete_post/<post_uuid>', methods=['POST'])
def delete_post_route(post_uuid):

    user_uuid = session.get("user_uuid")
    if not user_uuid:
        return {"success": False, "error": "Not logged in"}, 403

    user = get_user_by_uuid(user_uuid)
    if not user or user['is_admin'] != 1:
        return {"success": False, "error": "Not authorized"}, 403

    post = get_post_by_uuid(post_uuid)
    if not post:
        return {"success": False, "error": "Post not found"}, 404

    # FIX: db_interface.delete_post() expects a post_uuid, not a dict
    delete_post(post['post_uuid'])

    return {"success": True}

@content.route('/admin')
def admin_dashboard():
    if 'user' not in session or session['user'] not in ADMINS:
       return "Unauthorized", 403
    return render_template('admin_dashboard.html')

from oce.utils.db_interface import (
    get_user_by_uuid,
    update_user_username,
    update_user_email,
    update_user_about_me,
)

@content.route('/account_settings', methods=['GET', 'POST'])
def account_settings():
    # Require login and valid UUID in session
    user_uuid = session.get('user_uuid')
    if not user_uuid:
        flash("You must be logged in to access account settings.", "danger")
        return redirect(url_for('content.login'))

    # Fetch the current user record
    user = get_user_by_uuid(user_uuid)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('content.login'))

    if request.method == 'POST':
        new_username = request.form.get('username', '').strip()
        new_email = request.form.get('email', '').strip()
        new_about_me = request.form.get('about_me', '').strip()

        if new_username:
            update_user_username(user, new_username)
            session['user'] = new_username  # keep navbar/display in sync

        if new_email:
            update_user_email(user, new_email)

        if new_about_me:
            update_user_about_me(user, new_about_me)

        flash("Account settings updated successfully!", "success")
        return redirect(url_for('content.account_settings'))

    return render_template('account_settings.html', user=user)

@content.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    session.pop('user_uuid', None)
    #github.logout()
    flash("You have been logged out.", "success")
    return render_template('logout.html')

@content.route('/')
def index():
    return render_template('index.html')

def get_logged_in_user():
    """Return the current logged-in user object, or None if not logged in."""
    user_uuid = session.get("user_uuid")
    if not user_uuid:
        return None

    user = get_user_by_uuid(user_uuid)
    if not user:
        return None

    return user

@content.context_processor
def inject_user():
    return dict(logged_in_user=get_logged_in_user())
