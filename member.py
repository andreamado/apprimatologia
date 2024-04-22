from flask import Blueprint, render_template

from .db import get_session
from .auth import login_required
from .models import Member, Profile

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


@bp.route('/<language:language>/<int:id>')
# @login_required
def profile(id: int, language):
    with get_session() as db_session:
        member = db_session.execute(select(Profile).where(Profile.id == id)).scalar_one()

        # TODO: display a member not found page if member is not found

        description = member.description_pt if language == 'pt' else member.description_en

        return render_template(
            'members/profile.html',
            member=member,
            description=description,
            lang=language
        )


def register(app):
    app.register_blueprint(bp)