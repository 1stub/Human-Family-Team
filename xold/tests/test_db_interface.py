import sqlite3
from pathlib import Path

import pytest
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from oce import create_app
from oce.utils.db_interface import *
from oce.utils.db_interface import _dict_factory


@pytest.fixture(scope='module')
def app():
    app = create_app()
    app.config.update({'TESTING': True, 'DB_NAME': 'test.db'})

    yield app


@pytest.fixture(scope='module')
def setup_database():
    db_path = Path('oce') / 'static' / 'test.db'
    con = sqlite3.connect(db_path)
    con.row_factory = _dict_factory
    cur = con.cursor()
    cur.execute(
        'CREATE TABLE USERS(user_uuid TEXT PRIMARY KEY, username TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, profile_pic BLOB NOT NULL, about_me TEXT NOT NULL);'
    )
    cur.execute(
        'CREATE TABLE POSTS(post_uuid TEXT PRIMARY KEY, author_uuid TEXT NOT NULL, text_content TEXT NOT NULL, tag1 TEXT, tag2 TEXT, tag3 TEXT, tag4 TEXT, tag5 TEXT, image BLOB, datetime TEXT NOT NULL, location TEXT);'
    )
    cur.execute(
        'CREATE TABLE COMMENTS(comment_uuid TEXT PRIMARY KEY, parent_post_uuid TEXT NOT NULL, author_uuid TEXT NOT NULL, text_content TEXT NOT NULL, datetime TEXT NOT NULL);'
    )
    con.commit()
    yield cur
    con.close()
    db_path.unlink()


@pytest.fixture
def setup_password_hasher():
    ph = PasswordHasher()
    yield ph


# region
def test_create_user(app, setup_database, setup_password_hasher):
    with app.app_context():
        create_user('TestUser', 'test.user@email.com', 'testpassword')


def test_get_user_by_uuid(app, setup_database):
    with app.app_context():
        ...

def test_get_user_by_email(app, setup_database):
    with app.app_context():
        assert 'test.user@email.com' in get_user_by_email('test.user@email.com').values()

def test_update_user_username(app, setup_database):
    with app.app_context():
        u = User(**get_user_by_email('test.user@email.com'))
        update_user_username(u, 'NewUsername')
        assert 'NewUsername' in get_user_by_email('test.user@email.com').values()

def test_update_user_email(app, setup_database):
    with app.app_context():
        u = User(**get_user_by_email('test.user@email.com'))
        update_user_email(u, 'new.email@tsest.com')
        assert 'new.email@tsest.com' in get_user_by_email('new.email@tsest.com').values()

def test_update_user_password(app, setup_database, setup_password_hasher):
    with app.app_context():
        u = User(**get_user_by_email('new.email@tsest.com'))
        update_user_password(u, 'pass2')
        assert setup_password_hasher.verify(get_user_by_email('new.email@tsest.com')['password'], 'pass2')

def test_update_user_profile_pic(app, setup_database):
    with app.app_context():
        u = User(**get_user_by_email('new.email@tsest.com'))
        update_user_profile_pic(u, b'\x89PNG')
        assert b'\x89PNG' in get_user_by_email('new.email@tsest.com').values()

def test_update_user_about_me(app, setup_database):
    with app.app_context():
        u = User(**get_user_by_email('new.email@tsest.com'))
        update_user_about_me(u, 'ABOUT ME')
        assert 'ABOUT ME' in get_user_by_email('new.email@tsest.com').values()

def test_delete_user(app, setup_database):
    with app.app_context():
        ...

def test_create_post(app, setup_database):
    with app.app_context():
        ...

def test_get_post_by_uuid(app, setup_database):
    with app.app_context():
        ...

def test_get_posts_by_author(app, setup_database):
    with app.app_context():
        ...

def test_get_posts_by_tag(app, setup_database):
    with app.app_context():
        ...

def test_get_posts_by_datetime(app, setup_database):
    with app.app_context():
        ...

def test_get_posts_by_location(app, setup_database):
    with app.app_context():
        ...

def test_update_post_text_content(app, setup_database):
    with app.app_context():
        ...

def test_update_post_tags(app, setup_database):
    with app.app_context():
        ...

def test_update_post_image(app, setup_database):
    with app.app_context():
        ...

def test_update_post_datetime(app, setup_database):
    with app.app_context():
        ...

def test_update_post_location(app, setup_database):
    with app.app_context():
        ...

def test_delete_post(app, setup_database):
    with app.app_context():
        ...

def test_create_comment(app, setup_database):
    with app.app_context():
        ...

def test_get_comment_by_uuid(app, setup_database):
    with app.app_context():
        ...

def test_get_comments_by_parent_post(app, setup_database):
    with app.app_context():
        ...

def test_get_comments_by_author(app, setup_database):
    with app.app_context():
        ...

def test_get_comments_by_datetime(app, setup_database):
    with app.app_context():
        ...

def test_update_comment_text_content(app, setup_database):
    with app.app_context():
        ...

def test_update_comment_datetime(app, setup_database):
    with app.app_context():
        ...

def test_delete_comment(app, setup_database):
    with app.app_context():
        ...

# endregion
