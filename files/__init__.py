from flask import Blueprint, request, send_from_directory, g
from flask import current_app as app
from sqlalchemy import select
from werkzeug.routing import BaseConverter

from shutil import copyfile
import json, os
from uuid import UUID

from .models import UploadedFile
from ..db import get_session

bp = Blueprint('file', __name__, template_folder='templates')

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename: str) -> bool:
    """Helper function to validate file extension"""

    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/file/upload', methods=['POST'])
def upload():
    """Uploads a file
    
    Saves a file locally and adds it to the database, returning file name 
    and id or an error message.
    """

    if 'file' in request.files:
        f = request.files['file']
    elif 'file' in request.form:
        f = request.form['file']
    else:
        return json.dumps({'error': 'no file uploaded'}), 400 

    try:
        user = g.user
    except:
        user = request.form['userId']

    if f.filename == '':
        return json.dumps({'error': 'no selected file'}), 400

    if not allowed_file(f.filename):
        return json.dumps({'error': 'file type not allowed'}), 415

    #TODO: sanitize the description
    description = \
      request.form['description'].strip() \
        if 'description' in request.form \
        else None
    
    with get_session() as db_session:
        file = UploadedFile(f.filename, description, user)
        try:
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], str(file.id)))
        except:
            return json.dumps({'error': 'upload failed'}), 500
        else:
            db_session.add(file)
            db_session.commit()

        return json.dumps({
            'id': f'{file.id}',
            'name': f'{file.original_name}'
        }), 200


def get_extension(id):
    with get_session() as db_session:
        file = db_session.get(UploadedFile, id)
        return file.extension


@bp.route("/file/get/<uuid:id>")
# https://tedboy.github.io/flask/generated/flask.send_from_directory.html
def get(id):
    """Sends a file from the upload directory"""

    upload_folder = app.config['UPLOAD_FOLDER']

    # TODO: update the verification to include direction
    with get_session() as db_session:
      file = db_session.get(UploadedFile, id)
      if file.public:
        return send_from_directory(upload_folder, id)
      else:
        if g.IXIPC_user is None or (not g.IXIPC_user.organizer):
          return 'access unauthorized', 401
        else:
          return send_from_directory(upload_folder, id)

@bp.route("/file/get/<uuid:id>/<string:name>")
# https://tedboy.github.io/flask/generated/flask.send_from_directory.html
def get_with_name(id, name=None):
    """Sends a file from the upload directory"""

    upload_folder = app.config['UPLOAD_FOLDER']
    temp_folder = app.config['TEMP_FOLDER']

    # TODO: update the verification to include direction
    with get_session() as db_session:
        file = db_session.get(UploadedFile, id)

        if file.public:
            # TODO: authorize for public files after proper escaping
            return send_from_directory(upload_folder, id)
        else:
            if g.IXIPC_user is None or (not g.IXIPC_user.organizer):
                return 'access unauthorized', 401
            else:
                filename = f'{name}.{get_extension(id)}'

                orig_file = os.path.join(upload_folder, str(id))
                dest_file = os.path.join(temp_folder, filename)

                copyfile(orig_file, dest_file)
                return send_from_directory(temp_folder, filename)


@bp.route("/file/remove", methods=['POST'])
def remove():
    """Removes a file from the uploaded files
    
    Mark a file as removed in the database and move it to the deleted files
    folder.
    """

    # Temporarily disable file removal until proper checks are in place
    # TODO: implement proper checks
    return '', 401

    if 'id' in request.form:
        id = request.form['id']
    else:
        # TODO: Correct this error
        return json.dumps({'error': 'no file uploaded'}), 400

    with get_session() as db_session:
        file = db_session.execute(
            select(UploadedFile).filter_by(id=UUID(id))
        ).scalar_one()

        if not file.deleted:
            try:
                file.delete()
            except:
                db_session.rollback()
                return 'unable to remove file', 500
            else:
                db_session.commit()

    return json.dumps({}), 204


def register(app) -> None:
    """Registers the files blueprint with the Flask app"""

    app.register_blueprint(bp)
