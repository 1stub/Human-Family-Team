"""
Database helper functions for the OCE forum app.
"""

from pathlib import Path
from typing import Any, Sequence, TypeAlias
from uuid import uuid4 as create_uuid
from datetime import datetime

import sqlite3 as sql
import pytz
from flask import current_app, g, session

from .. import password_hasher
from .models import Comment, Post, User  # keep for typing

DatabaseRow: TypeAlias = dict[str, Any]


def _dict_factory(cursor: sql.Cursor, row: Sequence) -> DatabaseRow:
    d: DatabaseRow = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_db() -> sql.Connection:
    """Retrieve the database connection from the app.

    Attempts to open a new connection if database has not been opened yet.
    Raises FileNotFoundError if the database file cannot be located.
    """
    db: sql.Connection | None = getattr(g, "_database", None)
    if db is None:
        if not isinstance(current_app.static_folder, str):
            raise FileNotFoundError(
                "App static folder not registered properly. Unable to locate database."
            )
        db_path = Path(current_app.static_folder) / current_app.config["DB_NAME"]
        con = sql.connect(db_path)
        print(f"[DEBUG] Database connected at: {db_path}")
        con.row_factory = _dict_factory
        db = g._database = con
    return db


def close_db(e=None) -> None:
    db = g.pop("_database", None)
    if db is not None:
        db.close()


# ----------------------
# Users
# ----------------------
def create_user(
    username: str,
    email: str,
    password: str,
    profile_pic: bytes | None = None,
    about_me: str = "",
    is_admin: int = 0,
) -> None:
    """Create a new user in the database."""
    con = get_db()
    cur = con.cursor()

    if profile_pic is None:
        default_path = Path(current_app.static_folder) / "images" / "__DEFAULT.jpg"
        with open(default_path, "rb") as fp:
            profile_pic = fp.read()

    eastern = pytz.timezone("US/Eastern")
    now_est = datetime.now(eastern).isoformat()

    new_user_data = (
        str(create_uuid()),  # user_uuid
        username,
        email,
        password_hasher.hash(password),
        profile_pic,
        about_me,
        now_est,
        is_admin,
    )

    cur.execute(
        "INSERT INTO USERS (user_uuid, username, email, password, profile_pic, about_me, datetime_created, is_admin) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
        new_user_data,
    )
    con.commit()


def get_user_by_uuid(user_uuid: str) -> DatabaseRow | None:
    con = get_db()
    cur = con.cursor()
    return cur.execute("SELECT * FROM USERS WHERE user_uuid = ?;", (user_uuid,)).fetchone()


def get_user_by_email(email: str) -> DatabaseRow | None:
    con = get_db()
    cur = con.cursor()
    return cur.execute("SELECT * FROM USERS WHERE email = ?;", (email,)).fetchone()


def get_user_by_username(username: str) -> DatabaseRow | None:
    con = get_db()
    cur = con.cursor()
    return cur.execute("SELECT * FROM USERS WHERE username = ?;", (username,)).fetchone()


def update_user_username(user: User, username: str) -> None:
    con = get_db()
    cur = con.cursor()
    cur.execute("UPDATE USERS SET username = ? WHERE user_uuid = ?;", (username, user.user_uuid))
    con.commit()


def update_user_email(user: User, email: str) -> None:
    con = get_db()
    cur = con.cursor()
    cur.execute("UPDATE USERS SET email = ? WHERE user_uuid = ?;", (email, user.user_uuid))
    con.commit()


def update_user_password(user: User, password: str) -> None:
    con = get_db()
    cur = con.cursor()
    cur.execute(
        "UPDATE USERS SET password = ? WHERE user_uuid = ?;",
        (password_hasher.hash(password), user.user_uuid),
    )
    con.commit()


def update_user_profile_pic(user: User, profile_pic: bytes) -> None:
    con = get_db()
    cur = con.cursor()
    cur.execute("UPDATE USERS SET profile_pic = ? WHERE user_uuid = ?;", (profile_pic, user.user_uuid))
    con.commit()


def update_user_about_me(user: User, about_me: str) -> None:
    con = get_db()
    cur = con.cursor()
    cur.execute("UPDATE USERS SET about_me = ? WHERE user_uuid = ?;", (about_me, user.user_uuid))
    con.commit()


def delete_user(user: User) -> None:
    con = get_db()
    cur = con.cursor()
    cur.execute("DELETE FROM USERS WHERE user_uuid = ?;", (user.user_uuid,))
    con.commit()


# ----------------------
# Posts
# ----------------------
def create_post(author: str, text_content: str, is_announcement: bool = False) -> None:
    """
    Create a new post (temporary version without full user accounts).
    Stores class_year from the current session selection if not an announcement.
    """
    class_year = session.get("selected_class_year") if not is_announcement else None
    con = get_db()
    cur = con.cursor()

    # Provide default tag placeholders and image=None, location=None
    new_post_data = (
        str(create_uuid()),  # post_uuid
        author,  # author_uuid or placeholder
        text_content,
        None,  # tag1
        None,  # tag2
        None,  # tag3
        None,  # tag4
        None,  # tag5
        None,  # image
        datetime.now().isoformat(),  # datetime
        None,  # location
        class_year,
        int(is_announcement),
    )

    cur.execute(
        """
        INSERT INTO POSTS (
            post_uuid, author_uuid, text_content, tag1, tag2, tag3, tag4, tag5,
            image, datetime, location, class_year, is_announcement
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        new_post_data,
    )
    con.commit()


def get_posts_for_class(class_year=None):
    con = get_db()
    cur = con.cursor()
    if class_year is None:
        class_year = session.get("selected_class_year")
    if not class_year:
        return []
    cur.execute(
        """
        SELECT * FROM POSTS
        WHERE class_year = ?
          AND (is_announcement IS NULL OR is_announcement = 0)
        ORDER BY datetime DESC;
        """,
        (class_year,),
    )
    return cur.fetchall()


def get_announcements():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM POSTS WHERE is_announcement = 1 ORDER BY datetime DESC;")
    return cur.fetchall()


def get_all_posts():
    con = get_db()
    cur = con.cursor()
    class_year = session.get("selected_class_year")
    if class_year:
        cur.execute(
            "SELECT * FROM POSTS WHERE class_year = ? OR is_announcement = 1 ORDER BY datetime DESC;",
            (class_year,),
        )
    else:
        cur.execute("SELECT * FROM POSTS WHERE is_announcement = 1 ORDER BY datetime DESC;")
    return cur.fetchall()


def get_post_by_uuid(post_uuid: str) -> DatabaseRow | None:
    con = get_db()
    cur = con.cursor()
    return cur.execute("SELECT * FROM POSTS WHERE post_uuid = ?;", (post_uuid,)).fetchone()


def get_posts_by_author(author: User) -> list[DatabaseRow]:
    con = get_db()
    cur = con.cursor()
    return cur.execute("SELECT * FROM POSTS WHERE author_uuid = ?;", (author.user_uuid,)).fetchall()


def get_posts_by_tag(tag: str) -> list[DatabaseRow]:
    if not tag:
        raise ValueError("Cannot query for posts based on empty tag.")
    con = get_db()
    cur = con.cursor()
    return cur.execute(
        "SELECT * FROM POSTS WHERE tag1 = ? OR tag2 = ? OR tag3 = ? OR tag4 = ? OR tag5 = ?;",
        (tag, tag, tag, tag, tag),
    ).fetchall()


def get_posts_by_datetime(dt: str) -> list[DatabaseRow]:
    con = get_db()
    cur = con.cursor()
    return cur.execute("SELECT * FROM POSTS WHERE datetime = ?;", (dt,)).fetchall()


def get_posts_by_location(location: str) -> list[DatabaseRow]:
    con = get_db()
    cur = con.cursor()
    return cur.execute("SELECT * FROM POSTS WHERE location = ?;", (location,)).fetchall()


def update_post_text_content(post: Post, text_content: str) -> None:
    con = get_db()
    cur = con.cursor()
    cur.execute("UPDATE POSTS SET text_content = ? WHERE post_uuid = ?;", (text_content, post.post_uuid))
    con.commit()


def update_post_tags(post: Post, tags: tuple[str, str, str, str, str]) -> None:
    con = get_db()
    cur = con.cursor()
    tag1, tag2, tag3, tag4, tag5 = tags
    cur.execute(
        """
        UPDATE POSTS SET tag1 = ?, tag2 = ?, tag3 = ?, tag4 = ?, tag5 = ?
        WHERE post_uuid = ?;
        """,
        (tag1, tag2, tag3, tag4, tag5, post.post_uuid),
    )
    con.commit()


def update_post_image(post: Post, image: bytes) -> None:
    con = get_db()
    cur = con.cursor()
    cur.execute("UPDATE POSTS SET image = ? WHERE post_uuid = ?;", (image, post.post_uuid))
    con.commit()


def update_post_datetime(post: Post, dt: str) -> None:
    con = get_db()
    cur = con.cursor()
    cur.execute("UPDATE POSTS SET datetime = ? WHERE post_uuid = ?;", (dt, post.post_uuid))
    con.commit()


def update_post_location(post: Post, location: str) -> None:
    con = get_db()
    cur = con.cursor()
    cur.execute("UPDATE POSTS SET location = ? WHERE post_uuid = ?;", (location, post.post_uuid))
    con.commit()


def delete_post_by_uuid(post_uuid: str) -> None:
    con = get_db()
    cur = con.cursor()
    cur.execute("DELETE FROM POSTS WHERE post_uuid = ?;", (post_uuid,))
    con.commit()


# ----------------------
# Comments
# ----------------------
def create_comment(parent_post: Post, author: User, text_content: str, dt: str) -> None:
    """Create a new comment for a post."""
    con = get_db()
    cur = con.cursor()
    new_comment_data = (
        str(create_uuid()),  # comment_uuid
        parent_post.post_uuid,
        author.user_uuid,
        text_content,
        dt,
    )
    cur.execute(
        "INSERT INTO COMMENTS (comment_uuid, parent_post_uuid, author_uuid, text_content, datetime) VALUES (?, ?, ?, ?, ?);",
        new_comment_data,
    )
    con.commit()


def get_comment_by_uuid(comment_uuid: str) -> DatabaseRow | None:
    con = get_db()
    cur = con.cursor()
    return cur.execute("SELECT * FROM COMMENTS WHERE comment_uuid = ?;", (comment_uuid,)).fetchone()


def get_comments_by_parent_post(parent_post: Post) -> list[DatabaseRow]:
    con = get_db()
    cur = con.cursor()
    return cur.execute("SELECT * FROM COMMENTS WHERE parent_post_uuid = ?;", (parent_post.post_uuid,)).fetchall()


def get_comments_by_author(author: User) -> list[DatabaseRow]:
    con = get_db()
    cur = con.cursor()
    return cur.execute("SELECT * FROM COMMENTS WHERE author_uuid = ?;", (author.user_uuid,)).fetchall()


def get_comments_by_datetime(dt: str) -> list[DatabaseRow]:
    con = get_db()
    cur = con.cursor()
    return cur.execute("SELECT * FROM COMMENTS WHERE datetime = ?;", (dt,)).fetchall()


def update_comment_text_content(comment: Comment, text_content: str) -> None:
    con = get_db()
    cur = con.cursor()
    cur.execute("UPDATE COMMENTS SET text_content = ? WHERE comment_uuid = ?;", (text_content, comment.comment_uuid))
    con.commit()


def update_comment_datetime(comment: Comment, dt: str) -> None:
    con = get_db()
    cur = con.cursor()
    cur.execute("UPDATE COMMENTS SET datetime = ? WHERE comment_uuid = ?;", (dt, comment.comment_uuid))
    con.commit()


def delete_comment(comment: Comment) -> None:
    con = get_db()
    cur = con.cursor()
    cur.execute("DELETE FROM COMMENTS WHERE comment_uuid = ?;", (comment.comment_uuid,))
    con.commit()


# ----------------------
# Groups helper
# ----------------------
def get_all_groups(selected_age=None):
    """Return available groups based on selected age."""
    current_year = datetime.now().year
    base_groups = [
        {"id": 1, "name": f"Class Year {current_year}"},
        {"id": 2, "name": f"Class Year {current_year + 1}"},
        {"id": 3, "name": f"Class Year {current_year + 2}"},
        {"id": 4, "name": "Announcements"},
    ]

    if selected_age is None:
        return base_groups

    class_index = min(selected_age, 3)
    # class_index maps 1->index0, 2->index1, etc.
    idx = max(0, class_index - 1)
    filtered_groups = [base_groups[idx], base_groups[-1]]
    return filtered_groups
