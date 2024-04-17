from flask import Blueprint, render_template

from .db import get_session
from .auth import login_required
from .models import Member

from sqlalchemy import select

bp = Blueprint('associado', __name__, url_prefix='/associado')

@bp.route('/lista/')
# @login_required
def list_members():
    with get_session() as db_session:
        members = db_session.execute(select(Member.id, Member.number, Member.given_name, Member.family_name)).fetchall()

    return render_template(
        'members/list.html',
        members=members,
        lang='pt'
    )

@bp.route('/<int:id>')
# @login_required
def show_member(id: int):
    with get_session() as db_session:
        member = db_session.execute(select(Member).where(Member.id == id)).fetchone()

    return render_template(
        'members/show.html',
        member=member[0],
        lang='pt'
    )


def register(app):
    app.register_blueprint(bp)