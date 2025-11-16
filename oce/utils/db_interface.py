"""
Functions to interface to the database.
"""

import sqlite3 as sql
from collections.abc import Sequence
from pathlib import Path
from typing import Any, TypeAlias
from uuid import uuid4 as create_uuid

from flask import current_app, g

from .. import password_hasher
from .models import Comment, Post, User
from datetime import datetime
import pytz

DatabaseRow: TypeAlias = dict[str, Any]


def _dict_factory(cursor: sql.Cursor, row: Sequence) -> DatabaseRow:
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_db() -> sql.Connection:
    """Retrieve the database connection from the app.

    Attempts to open a new connection if database has not been open yet.

    Raises:
        FileNotFoundError: Database file was not able to be located.

    Returns:
        Connection to the database for querying.
    """
    db: sql.Connection | None = getattr(g, '_database', None)
    if db is None:
        if not isinstance(current_app.static_folder, str):
            raise FileNotFoundError(
                'App static folder not registered properly. Unable to locate database.'
            )
        con = sql.connect(Path(current_app.static_folder) / current_app.config['DB_NAME'] )
        print(f"[DEBUG] Database connected at: {Path(current_app.static_folder) / current_app.config['DB_NAME']}")
        con.row_factory = _dict_factory
        db = g._database = con
    return db


# Methods for Users


def create_user(
    username: str,
    email: str,
    password: str,
    profile_pic: bytes | None = None,
    about_me: str = '',
) -> None:
    """Creates a new user in the database.

    Args:
        username: User's user/display name.
        email: User's email.
        password: User's password. Will be hashed.
        profile_pic: User's profile picture as raw bytes. Defaults to None.
        about_me: User's about me description. Defaults to ''.
    """
    con = get_db()
    cur = con.cursor()

    if profile_pic is None:
        with open(Path(current_app.static_folder) / 'images' / '__DEFAULT.jpg', 'rb') as fp:
            profile_pic = fp.read()

    eastern = pytz.timezone('US/Eastern')
    now_est = datetime.now(eastern).isoformat()
    new_user_data = (
        str(create_uuid()),
        username,
        email,
        password_hasher.hash(password),
        profile_pic,
        about_me,
        now_est  # UTC timestamp
    )

    cur.execute(
        'INSERT INTO USERS VALUES(?, ?, ?, ?, ?, ?, ?);',
        new_user_data,
    )
    con.commit()


def get_user_by_uuid(user_uuid: str) -> DatabaseRow | None:
    """Retrieve user data given a UUID.

    Args:
        user_uuid: UUID of user.

    Returns:
        Database query if the UUID exists, None otherwise.
    """
    con = get_db()
    cur = con.cursor()

    datum: DatabaseRow = cur.execute(
        'SELECT * FROM USERS WHERE user_uuid = ?;',
        (user_uuid,),
    ).fetchone()
    return datum


def get_user_by_email(email: str) -> DatabaseRow | None:
    """Retrieve user data given an email.

    Args:
        email: Email of user.

    Returns:
        Database query if the email exists, None otherwise.
    """
    con = get_db()
    cur = con.cursor()

    datum: DatabaseRow = cur.execute(
        'SELECT * FROM USERS WHERE email = ?;',
        (email,),
    ).fetchone()
    return datum

def get_user_by_username(username: str) -> DatabaseRow | None:
    con = get_db()
    cur = con.cursor()
    datum: DatabaseRow = cur.execute(
        'SELECT * FROM USERS WHERE username = ?;',
        (username,)
    ).fetchone()
    return datum


def update_user_username(user: User, username: str) -> None:
    """Update a user's username.

    Args:
        user: User to be edited.
        username: New username.
    """
    con = get_db()
    cur = con.cursor()

    cur.execute(
        'UPDATE USERS SET username = ? WHERE user_uuid = ?;',
        (username, user.user_uuid),
    )
    con.commit()


def update_user_email(user: User, email: str) -> None:
    """Update a user's email.

    Args:
        user: User to be edited.
        email: New email.
    """
    con = get_db()
    cur = con.cursor()

    cur.execute(
        'UPDATE USERS SET email = ? WHERE user_uuid = ?;',
        (email, user.user_uuid),
    )
    con.commit()


def update_user_password(user: User, password: str) -> None:
    """Update a user's password.

    Args:
        user: User to be edited.
        password: New password. Will be hashed.
    """
    con = get_db()
    cur = con.cursor()

    cur.execute(
        'UPDATE USERS SET password = ? WHERE user_uuid = ?;',
        (password_hasher.hash(password), user.user_uuid),
    )
    con.commit()


def update_user_profile_pic(user: User, profile_pic: bytes) -> None:
    """Update a user's password.

    Args:
        user: User to be edited.
        profile_pic: New profile pic.
    """
    con = get_db()
    cur = con.cursor()

    cur.execute(
        'UPDATE USERS SET profile_pic = ? WHERE user_uuid = ?;',
        (profile_pic, user.user_uuid),
    )
    con.commit()


def update_user_about_me(user: User, about_me: str) -> None:
    """Update user's about me.

    Args:
        user: User to be edited.
        about_me: New about me.
    """
    con = get_db()
    cur = con.cursor()

    cur.execute(
        'UPDATE USERS SET about_me = ? WHERE user_uuid = ?;',
        (about_me, user.user_uuid),
    )
    con.commit()


def delete_user(user: User) -> None:
    """Delete a user.

    Arguments:
        user: User to delete.

    """
    con = get_db()
    cur = con.cursor()

    cur.execute(
        'DELETE FROM USERS WHERE user_uuid = ?;',
        (user.user_uuid,),
    )
    con.commit()


# Methods for Posts.


# def create_post(
#     author: User,
#     text_content: str,
#     tag1: str,
#     tag2: str,
#     tag3: str,
#     tag4: str,
#     tag5: str,
#     datetime: str,
#     location: str,
#     image: bytes | None = None,
# ) -> None:
#     """Create a new post for a user with tags and content.

#     Args:
#         author: Author of the post.
#         text_content: Content of the post.
#         tag1: Tag for the post.
#         tag2: Tag for the post.
#         tag3: Tag for the post.
#         tag4: Tag for the post.
#         tag5: Tag for the post.
#         datetime: Date- and timestamp of the post.
#         location: Location associated with the post.
#         image: Optional image to associate with the post. Defaults to None.
#     """
#     con = get_db()
#     cur = con.cursor()

#     new_post_data = (
#         str(create_uuid()),
#         author.user_uuid,
#         text_content,
#         tag1,
#         tag2,
#         tag3,
#         tag4,
#         tag5,
#         location,
#         datetime,
#         image,
#     )

#     cur.execute(
#         'INSERT INTO POSTS VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
#         new_post_data,
#     )
#     con.commit()


#this is temorary, should be relpaced by the function above when the user acounts feature is added
from flask import session
from datetime import datetime
# from oce.utils import create_uuid  # adjust import as needed
# from oce.db import get_db          # adjust import as needed

def create_post(author: str, text_content: str, is_announcement: bool = False) -> None:
    """
    Create a new post (temporary version without user accounts).
    Stores class_year from the current session selection.

    Args:
        author: Author name or placeholder (e.g., "Anonymous")
        text_content: The message content
        is_announcement: If True, post is visible to all class years
    """

    # Get class_year (None if announcement or not selected)
    class_year = session.get('selected_class_year') if not is_announcement else None

    # Create database connection
    con = get_db()
    cur = con.cursor()

    # Define new post tuple
    new_post_data = (
        str(create_uuid()),         # post_uuid
        author,                     # author_uuid
        text_content,               # text_content
        'None', 'None', 'None', 'None', 'None',  # tags
        None,                       # image (BLOB)
        datetime.now().isoformat(), # datetime
        None,                       # location
        class_year,                 # class_year
        int(is_announcement)        # is_announcement
    )

    # Adjusted INSERT statement — now includes 13 fields
    cur.execute(
        """
        INSERT INTO POSTS (
            post_uuid, author_uuid, text_content, tag1, tag2, tag3, tag4, tag5,
            image, datetime, location, class_year, is_announcement
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        new_post_data
    )

    con.commit()

def get_posts_for_class(class_year=None):
    """Fetch posts only for the user's class (no announcements)."""
    con = get_db()
    cur = con.cursor()

    # Prefer explicit argument; fallback to session
    if class_year is None:
        class_year = session.get('selected_class_year')
    print(f"[DEBUG][get_posts_for_class] Using class_year: {class_year}")
    print(f"[DEBUG][get_posts_for_class] Full session: {dict(session)}")

    if not class_year:
        print("[DEBUG][get_posts_for_class] No class year in session — returning []")
        return []

    # Fetch posts for this class (not announcements)
    cur.execute("""
        SELECT *
        FROM POSTS
        WHERE class_year = ?
          AND (is_announcement IS NULL OR is_announcement = 0)
        ORDER BY datetime DESC;
    """, (class_year,))

    rows = cur.fetchall()
    print(f"[DEBUG][get_posts_for_class] Rows fetched: {len(rows)}")
    return rows



def get_announcements():
    """Fetch only announcements."""
    con = get_db()
    cur = con.cursor()

    cur.execute("""
        SELECT * FROM POSTS
        WHERE is_announcement = 1
        ORDER BY datetime DESC;
    """)
    rows = cur.fetchall()
    print(f"[DEBUG][get_announcements] Announcement count: {len(rows)}")

    return cur.fetchall()


def get_all_posts():
    """Fetch posts filtered by selected class year and announcements."""
    con = get_db()
    cur = con.cursor()

    class_year = session.get('selected_class_year')

    if class_year:
        cur.execute("""
            SELECT * FROM POSTS
            WHERE class_year = ? OR is_announcement = 1
            ORDER BY datetime DESC;
        """, (class_year,))
    else:
        # fallback — show only announcements
        cur.execute("""
            SELECT * FROM POSTS
            WHERE is_announcement = 1
            ORDER BY datetime DESC;
        """)

    return cur.fetchall()


def get_post_by_uuid(post_uuid: str) -> DatabaseRow | None:
    """Retrieve a post by UUID.

    Args:
        post_uuid: UUID of the post.

    Returns:
        Database query if the post exists, None otherwise.
    """
    con = get_db()
    cur = con.cursor()

    datum: DatabaseRow = cur.execute(
        'SELECT * FROM POSTS WHERE post_uuid = ?;',
        (post_uuid,),
    ).fetchone()
    return datum


def get_posts_by_author(author: User) -> list[DatabaseRow]:
    """Retrieve all posts by a certain author.

    Args:
        author: Author of the posts.

    Returns:
        All posts by specified author.
    """
    con = get_db()
    cur = con.cursor()

    datum: DatabaseRow = cur.execute(
        'SELECT * FROM POSTS WHERE author_uuid = ?;',
        (author.user_uuid,),
    ).fetchall()
    return datum


def get_posts_by_tag(tag: str) -> list[DatabaseRow]:
    """Retrieve posts by tag.

    Args:
        tag: Tag of the posts.

    Raises:
        ValueError: Supplied tag was empty.

    Returns:
        All posts with specified tag.
    """
    if not tag:
        raise ValueError('Cannot query for posts based on empty tag.')

    con = get_db()
    cur = con.cursor()

    datum: DatabaseRow = cur.execute(
        'SELECT * FROM POSTS WHERE tag1 = ? OR tag2 = ? OR tag3 = ? OR tag4 = ? OR tag5 = ?;',
        (tag, tag, tag, tag, tag),
    ).fetchall()
    return datum


def get_posts_by_datetime(datetime: str) -> list[DatabaseRow]:
    """Retrieve posts by date- and timestamp.

    Args:
        datetime: Date- and timestamp of the posts.

    Returns:
        All posts with specified date- and timestamp.
    """
    con = get_db()
    cur = con.cursor()

    datum: DatabaseRow = cur.execute(
        'SELECT * FROM POSTS WHERE datetime = ?;',
        (datetime,),
    ).fetchall()
    return datum


def get_posts_by_location(location: str) -> list[DatabaseRow]:
    """Retrieve posts by location.

    Args:
        location: Location of the posts.

    Returns:
        All posts with specified location.
    """
    con = get_db()
    cur = con.cursor()

    datum: DatabaseRow = cur.execute(
        'SELECT * FROM POSTS WHERE location = ?;',
        (location,),
    ).fetchall()
    return datum


def update_post_text_content(post: Post, text_content: str) -> None:
    """Update a post's content.

    Args:
        post: Post to be edited.
        text_content: New content for the post.
    """
    con = get_db()
    cur = con.cursor()

    cur.execute(
        'UPDATE POSTS SET text_content = ? WHERE post_uuid = ?;',
        (text_content, post.post_uuid),
    )
    con.commit()


def update_post_tags(post: Post, tags: tuple[str, str, str, str, str]) -> None:
    """Update a post's tags.

    Args:
        post: Post to be edited.
        tags: New tags for the post.
    """
    con = get_db()
    cur = con.cursor()

    tag1, tag2, tag3, tag4, tag5 = tags

    cur.execute(
        'UPDATE POSTS SET tag1 = ? WHERE post_uuid = ?;',
        (tag1, post.post_uuid),
    )
    cur.execute(
        'UPDATE POSTS SET tag2 = ? WHERE post_uuid = ?;',
        (tag2, post.post_uuid),
    )
    cur.execute(
        'UPDATE POSTS SET tag3 = ? WHERE post_uuid = ?;',
        (tag3, post.post_uuid),
    )
    cur.execute(
        'UPDATE POSTS SET tag4 = ? WHERE post_uuid = ?;',
        (tag4, post.post_uuid),
    )
    cur.execute(
        'UPDATE POSTS SET tag5 = ? WHERE post_uuid = ?;',
        (tag5, post.post_uuid),
    )
    con.commit()


def update_post_image(post: Post, image: bytes) -> None:
    """Update a post's image.

    Args:
        post: Post to be edited.
        image: New image for the post.
    """
    con = get_db()
    cur = con.cursor()

    cur.execute(
        'UPDATE POSTS SET image = ? WHERE post_uuid = ?;',
        (image, post.post_uuid),
    )
    con.commit()


def update_post_datetime(post: Post, datetime: str) -> None:
    """Update a post's date- and timestamp.

    Args:
        post: Post to be edited.
        datetime: New date- and timestamp for the post.
    """
    con = get_db()
    cur = con.cursor()

    cur.execute(
        'UPDATE POSTS SET datetime = ? WHERE post_uuid = ?;',
        (datetime, post.post_uuid),
    )
    con.commit()


def update_post_location(post: Post, location: str) -> None:
    """Update a post's location.

    Args:
        post: Post to be edited.
        location: New location for the post.
    """
    con = get_db()
    cur = con.cursor()

    cur.execute(
        'UPDATE POSTS SET location = ? WHERE post_uuid = ?;',
        (location, post.post_uuid),
    )
    con.commit()


def delete_post(post: Post) -> None:
    """Delete a post.

    Args:
        post: Post to delete.
    """
    con = get_db()
    cur = con.cursor()

    cur.execute(
        'DELETE FROM POSTS WHERE post_uuid = ?;',
        (post.post_uuid,),
    )
    con.commit()


# Methods for Comments.


def create_comment(
    parent_post: Post,
    author: User,
    text_content: str,
    datetime: str,
) -> None:
    """Create a new comment for a post with content.

    Args:
        parent_post: Post the comment will be under.
        author: Author of the comment.
        text_content: Content of the comment.
        datetime: Date- and timestamp of the comment.
    """
    con = get_db()
    cur = con.cursor()

    new_comment_data = (
        str(create_uuid()),
        parent_post.post_uuid,
        author.uuid,
        text_content,
        datetime,
    )

    cur.execute(
        'INSERT INTO COMMENTS VALUES(?, ?, ?, ?, ?);',
        new_comment_data,
    )
    con.commit()


def get_comment_by_uuid(comment_uuid: str) -> DatabaseRow | None:
    """Retrieve a comment by UUID.

    Args:
        comment_uuid: UUID of the comment.

    Returns:
        Database query if the comment exists, None otherwise.
    """
    con = get_db()
    cur = con.cursor()

    datum: DatabaseRow = cur.execute(
        'SELECT * FROM COMMENTS WHERE comment_uuid = ?;',
        (comment_uuid,),
    ).fetchone()
    return datum


def get_comments_by_parent_post(parent_post: Post) -> list[DatabaseRow]:
    """Retrieve all comments under a certain post.

    Args:
        parent_post: Parent post of the comments.

    Returns:
        All comments under specified parent post.
    """
    con = get_db()
    cur = con.cursor()

    datum: DatabaseRow = cur.execute(
        'SELECT * FROM COMMENTS WHERE parent_post_uuid = ?;',
        (parent_post.user_uuid,),
    ).fetchall()
    return datum


def get_comments_by_author(author: User) -> list[DatabaseRow]:
    """Retrieve all comments by a certain author.

    Args:
        author: Author of the comments.

    Returns:
        All comments by specified author.
    """
    con = get_db()
    cur = con.cursor()

    datum: DatabaseRow = cur.execute(
        'SELECT * FROM COMMENTS WHERE author_uuid = ?;',
        (author.user_uuid,),
    ).fetchall()
    return datum


def get_comments_by_datetime(datetime: str) -> list[DatabaseRow]:
    """Retrieve comments by date- and timestamp.

    Args:
        datetime: Date- and timestamp of the comments.

    Returns:
        All comments with specified date- and timestamp.
    """
    con = get_db()
    cur = con.cursor()

    datum: DatabaseRow = cur.execute(
        'SELECT * FROM COMMENTS WHERE datetime = ?;',
        (datetime,),
    ).fetchall()
    return datum


def update_comment_text_content(comment: Comment, text_content: str) -> None:
    """Update a comment's content.

    Args:
        comment: Post to be edited.
        text_content: New content for the comment.
    """
    con = get_db()
    cur = con.cursor()

    cur.execute(
        'UPDATE COMMENTS SET text_content = ? WHERE comment_uuid = ?;',
        (text_content, comment.comment_uuid),
    )
    con.commit()


def update_comment_datetime(comment: Comment, datetime: str) -> None:
    """Update a comment's date- and timestamp.

    Args:
        comment: Post to be edited.
        datetime: New date- and timestamp for the comment.
    """
    con = get_db()
    cur = con.cursor()

    cur.execute(
        'UPDATE COMMENTS SET datetime = ? WHERE comment_uuid = ?;',
        (datetime, comment.comment_uuid),
    )
    con.commit()


def delete_comment(comment: Comment) -> None:
    """Delete a comment.

    Args:
        comment: Comment to delete.
    """
    con = get_db()
    cur = con.cursor()

    cur.execute(
        'DELETE FROM COMMENTS WHERE comment_uuid = ?;',
        (comment.comment_uuid,),
    )
    con.commit()


from datetime import datetime

def get_all_groups(selected_age=None):
    """Return available groups based on selected age."""
    current_year = datetime.now().year
    base_groups = [
        {'id': 1, 'name': f'Class Year {current_year}'},
        {'id': 2, 'name': f'Class Year {current_year + 1}'},
        {'id': 3, 'name': f'Class Year {current_year + 2}'},
        {'id': 4, 'name': 'Announcements'},
    ]

    if selected_age is None:
        return base_groups

    # Map ages to class indices (adjust mapping to your app logic)
    class_index = min(selected_age, 3)
    filtered_groups = [
        base_groups[class_index - 1],  # Class Year X
        base_groups[-1],               # Announcements
    ]
    return filtered_groups


# def get_all_groups():
#     current_year = datetime.now().year
#     return [
#         {'id': 1, 'name': f'Class Year {current_year}'},
#         {'id': 2, 'name': f'Class Year {current_year + 1}'},
#         {'id': 3, 'name': f'Class Year {current_year + 2}'},
#         {'id': 4, 'name': 'Announcements'},
#     ]