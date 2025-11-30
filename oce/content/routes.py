from flask import Blueprint, render_template, send_file, request, jsonify, redirect, url_for, flash, session
from oce.utils.db_interface import create_post, get_post_by_uuid, create_user, get_user_by_email
import base64
from oce.utils.db_interface import get_user_by_uuid, delete_post
from oce.utils.models import User
from flask_dance.contrib.github import github, make_github_blueprint
from flask_dance.consumer.storage.session import BaseStorage
from dotenv import load_dotenv
load_dotenv()
import os
import stripe
import json
import re
from .. import password_hasher #argon2
from flask_mail import Message
from .. import mail #mail from _init_.py


stripe.api_key = 'sk_test_51PpF2o06B5DFjCoR9UNUY24WHE9GRP6jfXmrpWjoDlE2RrGwGo0Y02rEG9UAs8no7Cn7Wst53Gt4e4QLpzqwErBl00e5TedpXy'

endpoint_secret = 'whsec_SKyFUQCREb8XNZJsb0H5brQoreLKtfBJ'
from .. import password_hasher #argon2
from flask_mail import Message
from .. import mail #mail from _init_.py


stripe.api_key = 'sk_test_51PpF2o06B5DFjCoR9UNUY24WHE9GRP6jfXmrpWjoDlE2RrGwGo0Y02rEG9UAs8no7Cn7Wst53Gt4e4QLpzqwErBl00e5TedpXy'

endpoint_secret = 'whsec_SKyFUQCREb8XNZJsb0H5brQoreLKtfBJ'

#THIS INSURES NO TAMPERING OF PRICES
#SINCE THIS IS IN THE BACKEND IT SHOULD BE SAFE
PRODUCT_CATALOG = {
    1: {'name': 'Bully Booster 1', 'price': 500},
    2: {'name': 'Bully Booster 2', 'price': 500},
    3: {'name': 'Bully Booster 3', 'price': 500},
    4: {'name': 'Bully Booster 4', 'price': 500},
    5: {'name': 'Bully Booster 5', 'price': 500},
    6: {'name': 'Bully Booster 6', 'price': 500},
    7: {'name': 'Bully Booster 7', 'price': 500},
    8: {'name': 'Bully Booster 8', 'price': 500},
    9: {'name': 'Bully Booster 9', 'price': 500},
    10: {'name': 'Action Cards Bundle 1', 'price': 500},
    11: {'name': 'Action Cards Bundle 2', 'price': 500},
    12: {'name': 'Action Cards Bundle 3', 'price': 500},
    13: {'name': 'Action Cards Bundle 4', 'price': 500},
    14: {'name': 'Action Cards Bundle 5', 'price': 500},
    15: {'name': 'Action Cards Bundle 6', 'price': 500},
    16: {'name': 'Learning Environment Card', 'price': 500},
    17: {'name': 'Stability Card', 'price': 500},
    18: {'name': 'Learning Energy Card', 'price': 500},
    19: {'name': 'Perception Card', 'price': 500},
    20: {'name': 'Responsibility Card', 'price': 500},
    21: {'name': 'Ability Card', 'price': 500},
    22: {'name': 'Discernment Card', 'price': 500},
    23: {'name': 'Friendships Card', 'price': 500},
    24: {'name': 'Resilience Card', 'price': 500},
    25: {'name': 'Arts Face Card', 'price': 500},
    26: {'name': 'Humanities Face Card', 'price': 500},
    27: {'name': 'Sciences Face Card', 'price': 500},
    28: {'name': 'Learning Environment Card', 'price': 500},
    29: {'name': 'Stability Card', 'price': 500},
    30: {'name': 'Learning Energy Card', 'price': 500},
    31: {'name': 'Perception Card', 'price': 500},
    32: {'name': 'Responsibility Card', 'price': 500},
    33: {'name': 'Ability Card', 'price': 500},
    34: {'name': 'Discernment Card', 'price': 500},
    35: {'name': 'Friendships Card', 'price': 500},
    36: {'name': 'Resilience Card', 'price': 500},
    37: {'name': 'Distinguished Citizen', 'price': 500},
    38: {'name': 'Zipper Pouch', 'price': 500},
    39: {'name': 'Calendar', 'price': 500},
    40: {'name': 'Character Equation Poster', 'price': 500},
    41: {'name': 'Venn Diagram Poster', 'price': 500},
    42: {'name': 'Scope & Sequence Poster', 'price': 500},
    43: {'name': 'Problem Solvers Poster', 'price': 500},
    44: {'name': 'Building Blocks Poster', 'price': 500},
    45: {'name': 'Micro-credential Badges', 'price': 500},
    46: {'name': 'Learning Environment Badge', 'price': 500},
    47: {'name': 'Stability Badge', 'price': 500},
    48: {'name': 'Learning Energy Badge', 'price': 500},
    49: {'name': 'Perception Badge', 'price': 500},
    50: {'name': 'Responsibility Badge', 'price': 500},
    51: {'name': 'Ability Badge', 'price': 500},
    52: {'name': 'Discernment Badge', 'price': 500},
    53: {'name': 'Friendship Badge', 'price': 500},
    54: {'name': 'Resilience Badge', 'price': 500},
    55: {'name': 'Venn Diagram with Symbols', 'price': 500},
    56: {'name': 'Scope & Sequence Customizable', 'price': 500},
    57: {'name': 'Town Hall Lessons', 'price': 500},
    58: {'name': 'Venn Diagram Wall Cling', 'price': 500},
}


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

#@content.route('/content/SignupPage')
#def signup2():
#  return render_template('SignupPage.html')


@content.route('/content/SignupPage', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        about_me = request.form.get('about_me', '').strip()

        # Basic validation
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for('content.signup'))

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format.", "danger")
            return redirect(url_for('content.signup'))

        if get_user_by_email(email):
            flash("Email already registered.", "warning")
            return redirect(url_for('content.signup'))

        # ---- ADMIN SECRET DETECTION ----
        ADMIN_TRIGGER = "[MAKE-ADMIN]"  # your secret characters
        is_admin = 1 if ADMIN_TRIGGER in about_me else 0
        # --------------------------------

        try:
            create_user(username=username, email=email, password=password, about_me=about_me, is_admin=is_admin)
            if is_admin:
                flash("Admin account created successfully!", "success")
            else:
                flash("Signup successful! You can now log in.", "success")
            return redirect(url_for('content.login'))
        except Exception as e:
            print(f"Signup error: {e}")
            flash("An error occurred during signup.", "danger")
            return redirect(url_for('content.signup'))

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

from flask import render_template, session
from oce.utils import db_interface

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



# def concept_exchange():
#     posts = db_interface.get_posts_for_class()
#     return render_template(
#         'mainForum.html',
#         posts=posts,
#         show_sidebar=True,
#         active_group='concept_exchange',
#         is_announcement_page=False
#     )


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

from datetime import datetime
from flask import request, redirect, url_for, flash, session

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


# @content.route('/content/resources/<int:selected_age>')
# @content.route('/resources/<int:selected_age>')
# def resources(selected_age):
#     session['selected_age'] = selected_age
#     return render_template('resources.html', selected_age=selected_age)


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

@content.route('/content/Contact/')
def contact():
  return render_template('ContactPage.html')

@content.route('/content/Shop/')
def shop():
  if 'user_uuid' not in session:
        flash("Please log in to access the shop.", "warning")
        return redirect(url_for('content.login'))
  return render_template('Shop.html')

@content.route('/content/Cart/')
def cart():
  if 'user_uuid' not in session:
        flash("Please log in to access the cart.", "warning")
        return redirect(url_for('content.login'))
  return render_template('Cart.html', product_catalog=PRODUCT_CATALOG)

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

#@content.route('/create_post', methods=['POST'])
#def create_post_route():
#    data = request.get_json()  # Get JSON data from the request
#    text_content = data.get('text_content')  # Extract the post content
#    username = data.get('username')
#
#    if not text_content:
#        return jsonify({'success': False, 'error': 'Text content is required.'}), 400
#
#    try:
#        # create_post(author=User(user_uuid="example", username="name", email="example@email.com", password="password", profile_pic=b"", about_me=''), text_content=text_content, tag1='', tag2='', tag3='', tag4='', tag5='', datetime='', location='', image=None)
#        create_post(author=username, text_content=text_content)  # this should be updated when the user login feature is added to look more like the one above this line
#        return jsonify({'success': True})
#    except Exception as e:
#        print(f"Error: {e}")
#        return jsonify({'success': False, 'error': str(e)}), 500


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

# @content.route('/delete_post/<post_uuid>', methods=['POST'])
# def delete_post_route(post_uuid):
#     from oce.utils.db_interface import get_post_by_uuid, delete_post
#     from flask import session

#     print("ADMINS LIST:", ADMINS)
#     print("CURRENT USER:", session.get("user"))

    
#     # Check logged in
#     current_user = session.get("user")
#     if not current_user:
#         return {"success": False, "error": "Not logged in"}, 403

#     # Check admin
#     if current_user not in ADMINS:
#         return {"success": False, "error": "Not authorized"}, 403

#     # Fetch post
#     post = get_post_by_uuid(post_uuid)
#     if not post:
#         return {"success": False, "error": "Post not found"}, 404

#     # Delete post
#     delete_post(post)
#     return {"success": True}



  # Stripe webhook secret


# ----------------------------
# CREATE CHECKOUT SESSION
# ----------------------------
@content.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    cart_json = request.form.get('cart')
    cart = json.loads(cart_json or "[]")

    customer_email = request.form.get('email')  # From your checkout form

    line_items = []
    for item in cart:
        product = PRODUCT_CATALOG.get(item['id'])
        if product:
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': product['name']},
                    'unit_amount': product['price'],  # in cents
                },
                'quantity': item['quantity'],
            })

    if not line_items:
        return "Invalid cart", 400

    # ----------------------------
    # 💌 TEST EMAIL (before Stripe)
    # ----------------------------
    try:
        msg = Message(
            subject="Checkout Session Started",
            recipients=["catronater@outlook.com"],  # send to yourself
            body=f"Customer email: {customer_email}\n\nCart: {cart}"
        )
        mail.send(msg)
        print("✅ Test email sent successfully before Stripe redirect!")
    except Exception as e:
        print(f"❌ Mail send failed (before Stripe): {e}")

    # ----------------------------
    # STRIPE CHECKOUT SESSION
    # ----------------------------

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        customer_email=customer_email,  # Stripe sends receipt
        success_url=url_for('content.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('content.index', _external=True),
        shipping_address_collection={'allowed_countries': ['US', 'CA']},  # optional
    )
    print("Checkout Made...")
    return redirect(session.url, code=303)


# ----------------------------
# STRIPE WEBHOOK
# ----------------------------
from flask import current_app

@content.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    if event["type"] == "checkout.session.completed":
        session_id = event["data"]["object"]["id"]

        # Retrieve full session info, expanding customer and line_items
        session = stripe.checkout.Session.retrieve(
            session_id,
            expand=["customer", "line_items"]
        )

        # ----------------------------
        # Customer info
        # ----------------------------
        customer_details = session.get("customer_details", {})
        customer_email = session.get("customer_email") or customer_details.get("email", "Unknown")
        customer_name = customer_details.get("name", "Customer")

        # ----------------------------
        # Shipping info
        # ----------------------------
        shipping_info = "No shipping info provided."
        shipping = customer_details.get("address")
        if shipping:
            lines = [
                customer_name,
                f"{shipping.get('line1', '')} {shipping.get('line2', '')}".strip(),
                f"{shipping.get('city', '')}, {shipping.get('state', '')} {shipping.get('postal_code', '')}".strip(),
                shipping.get("country", "")
            ]
            # Remove empty lines and join with newline
            shipping_info = "\n".join(filter(None, lines))

        # ----------------------------
        # Order items
        # ----------------------------
        items_text = ""
        line_items = session.get("line_items", {}).get("data", [])
        for item in line_items:
            items_text += f"{item.quantity} x {item.description} - ${item.amount_total / 100:.2f}\n"

        # ----------------------------
        # Send email
        # ----------------------------
        site_owner_email = 'catronater@outlook.com'
        try:
            msg_to_owner = Message(
                subject="New Order Received",
                recipients=[site_owner_email],
                body=f"""
New order received from {customer_name} ({customer_email}):

Shipping Address:
{shipping_info}

Order Summary:
{items_text}

Please forward this to maggie@southlandprint.com
"""
            )
            print("📨 Attempting to send email...")
            with current_app.app_context():
                mail.send(msg_to_owner)
            print("✅ Email sent successfully!")
        except Exception as e:
            print(f"❌ Mail send failed: {e}")

        return jsonify({"status": "success"})

    return jsonify({"status": "ignored"})


# @content.route('/github_login')
# def github_login():
#     if not github.authorized:
#         print("Client ID:", os.getenv('GITHUB_OAUTH_CLIENT_ID'))
#         print("Client Secret:", os.getenv('GITHUB_OAUTH_CLIENT_SECRET'))
#         auth_url, _ = github.authorization_url("https://github.com/login/oauth/authorize")
#         print("Redirecting to GitHub:",auth_url)
#         return redirect(auth_url)
#     #content.github_login
#     else:
#        account_info = github.get('/user')
#        if account_info.ok:
#           account_info_json = account_info.json()
#           return f'<h1>Your GitHub name is {account_info_json["login"]}</h1>'
#     return'<h1>Request failed!<h1>'

@content.route("/github_login")
def login_github():
    if not github.authorized:
        return redirect(url_for("github.login"))  # this triggers OAuth flow

    resp = github.get("/user")
    if not resp.ok:
        flash("Failed to fetch user info.", "error")
        return redirect(url_for("content.login"))

    username = resp.json()["login"]
    session["user"] = username
    flash(f"Logged in as {username}", "success")

    if username in ADMINS:
        return redirect(url_for("content.admin_dashboard"))

    return redirect(url_for("content.index"))

@content.route("/github_test")
def github_test():
    print("Authorized:", github.authorized)
    print("Token:", github.token)
    return "Check terminal"

# @content.route('/github_callback')
# def github_callback():
    # print("🔄 OAuth callback triggered!")
    # print("📂 Request Args:", request.args)

    # if 'code' not in request.args:
    #     print("❌ No 'code' in request.")
    #     flash("Authorization failed. No code received.", "error")
    #     return redirect(url_for('content.login'))

    # auth_code = request.args['code']

    # try:
    #     print("🔄 Exchanging code for token...")

    #     # Manually exchange the code for a token
    #     url = "https://github.com/login/oauth/access_token"
    #     data = {
    #         "client_id": os.getenv("GITHUB_CLIENT_ID"),
    #         "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
    #         "code": auth_code,
    #         "redirect_uri": "http://127.0.0.1:5000/github_callback",
    #     }
    #     headers = {"Accept": "application/json"}

    #     response = requests.post(url, json=data, headers=headers)
    #     print("🔄 GitHub Token Exchange Response:", response.text)  # Debug

    #     token_data = response.json()

    #     if "access_token" not in token_data:
    #         print("❌ No access_token in response:", token_data)
    #         flash("Authorization failed. No token received.", "error")
    #         return redirect(url_for('content.login'))

    #     session['github_token'] = token_data["access_token"]
    #     print("🟢 Session updated with token:", session['github_token'])

    # except Exception as e:
    #     print("❌ Error during token exchange:", e)
    #     flash("Authorization failed. Token exchange error.", "error")
    #     return redirect(url_for('content.login'))

    # return redirect(url_for('content.index'))
    # print("Callback triggered!")  # Debug print
    # print("Session Data:", session)


    # print("GitHub Token:", session.get("github_oauth_token"))
    # print(github.authorized)
    # if not github.authorized:
    #    print("Failed")
    #    flash("Authorizatiion failed.", "error")
    #    return redirect(url_for('content.login'))

    # account_info = github.get('/user')
    # if account_info.ok:
    #    account_info_json = account_info.json()
    #    username = account_info_json['login']
    #    print(f"Logged in as {username}")

    #    session['user'] = username
    #    flash(f"Logged in as {username}" , "success")

    #    if username in ADMINS:
    #       return redirect(url_for('content.admin_dashboard'))

    #    return redirect(url_for('content.index'))
    # flash("Failed to fetch user info.", "error")
    # return redirect(url_for('content.index'))

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

    # If your db_interface returns a dict, adapt accordingly:
    profile_pic = user.get("profile_pic")
    if profile_pic:
        user["profile_pic_b64"] = base64.b64encode(profile_pic).decode("utf-8")
    else:
        user["profile_pic_b64"] = None

    return user

@content.context_processor
def inject_user():
    return dict(logged_in_user=get_logged_in_user())
