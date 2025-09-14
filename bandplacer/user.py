import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from bandplacer.db import get_db

bp = Blueprint('user', __name__, url_prefix="/user")

@bp.route('/user', methods=('GET', 'POST'))
def user():
    if request.method == 'GET':

        if error is None:
            try:
                db.execute(
                    "insert into user (username, email, password) values (?, ?, ?)",
                    (username, email, generate_password_hash(password)))
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("user/user.html")

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "select * from user where id = ?", (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view
