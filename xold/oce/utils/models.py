"""
    Various models and abstractions around users, posts, and comments.
"""

from dataclasses import dataclass

from argon2.exceptions import VerifyMismatchError
from flask_login import UserMixin

from .. import login_manager, password_hasher


class User(UserMixin):
    def __init__(
        self,
        user_uuid: str,
        username: str,
        email: str,
        password: str,
        profile_pic: bytes,
        about_me: str,
        datetime_created: str
    ):
        self.id = user_uuid
        self.user_uuid = user_uuid
        self.username = username
        self.email = email
        self.password = password
        self.profile_pic = profile_pic
        self.about_me = about_me
        self.datetime_created = datetime_created


@login_manager.user_loader
def user_loader(uuid: str) -> User | None:
    from ..utils.db_interface import get_user_by_uuid

    if user_data := get_user_by_uuid(uuid):
        user = User(**user_data)
        return user
    return None

def validate_user_login(email: str, password: str) -> tuple[bool, str]:
    """Validate a login attempt given a email and password.

    Args:
        email: Email to log in with.
        password: Password to log in with.

    Returns:
        A tuple of login status and message.
        The status is True if the login was a success.
        The status is False if the login was a fail, and the status message is set accordingly.
    """
    from ..utils.db_interface import get_user_data_by_email

    if (user_data := get_user_data_by_email(email)) is not None:
        try:
            password_hasher.verify(user_data['password'], password)
        except VerifyMismatchError:
            return (False, 'Incorrect Password')
        else:
            return (True, '')
    return (False, 'Unrecognized Email')


@dataclass
class Post:
    post_uuid: str
    author_uuid: str
    text_content: str
    tag1: str
    tag2: str
    tag3: str
    tag4: str
    tag5: str
    image: bytes
    datetime: str
    location: str


@dataclass
class Comment:
    comment_uuid: str
    parent_post_uuid: str
    author_uuid: str
    text_content: str
    datetime: str
