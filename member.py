from flask import Blueprint, render_template

from .db import db_session
from .auth import login_required
from .models import Member

from sqlalchemy import select

bp = Blueprint('associado', __name__, url_prefix='/associado')

@bp.route('/lista/')
# @login_required
def list_members():
    try:
        members = db_session.execute(select(Member.id, Member.number, Member.given_name, Member.family_name)).fetchall()
    finally:
        db_session.close()


    return render_template(
        'members/list.html',
        members=members,
        lang='pt'
    )

@bp.route('/<int:id>')
# @login_required
def show_member(id: int):
    try:
        member = db_session.execute(select(Member).where(Member.id == id)).fetchone()
    finally:
        db_session.close()

    return render_template(
        'members/show.html',
        member=member[0],
        lang='pt'
    )

