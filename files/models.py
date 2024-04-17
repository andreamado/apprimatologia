from sqlalchemy import Column, Uuid, ForeignKey, String, Text, Boolean
from werkzeug.utils import secure_filename

import os, shutil, uuid

from ..db import Base

class UploadedFile(Base):
    __tablename__ = 'uploaded_files'
    id = Column(Uuid(), primary_key=True)
    user = Column(ForeignKey('users.id'))
    original_name = Column(String(256))
    extension = Column(String(6))
    description = Column(Text)
    deleted = Column(Boolean, nullable=False)

    def __init__(self, original_name, description=None, user=None, file_path=None):
        self.id = uuid.uuid4()
        self.user = user
        self.original_name = secure_filename(original_name)
        self.extension = self.original_name.split('.')[-1]
        self.description = description
        self.deleted = False

        if file_path:
            shutil.copy(file_path, os.path.join(app.root_path, 'uploaded_files', str(self.id)))

    def __repr__(self):
        return f'<File {self.original_name} ({self.id})>'

    def delete(self):
        self.deleted = True
        os.rename(
            os.path.join('uploaded_files', str(self.id)), 
            os.path.join('deleted_files', str(self.id))
        )
