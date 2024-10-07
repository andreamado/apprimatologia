from flask_mail import Mail, Message
import threading, json, os, uuid, mimetypes
from imap_tools import MailBox, AND

from flask import g, request 

INBOX = 'INBOX'
SENT = "[Gmail]/Sent Mail"
TRASH = "[Gmail]/Trash"
SPAM = "[Gmail]/Spam"
ALL = "[Gmail]/All Mail"

def register(app):
    # register the email methods
    app.mail = Mail(app)

    def send_email(subject: str, body: str, recipients: list[str], attachment: None|str=None) -> None:
        def _send_email():
            with app.app_context():
                for recipient in recipients:
                    msg = Message(subject, recipients=[recipient], body=body)

                    if attachment:
                        attachment_filename, id = attachment.split('|')
                        filetype = mimetypes.guess_type(attachment_filename)[0]
                        try:
                            with open(os.path.join(app.config['TEMP_FOLDER'], 'email', id), 'rb') as f:
                                msg.attach(filename=attachment_filename, content_type=filetype, data=f.read())
                        except:
                            print(f'error including attachment {attachment} in email to {recipient}')
                    
                    app.mail.send(msg)
                
                # TODO: log the emails
                print(f'Email sent to {recipients}.')
        t1 = threading.Thread(target=_send_email, name="email")
        t1.start()
    
    app.send_email = send_email

    @app.route('/email/attachmentupload', methods=['POST'])
    def attachmentupload():
        """Uploads an attachment file
        
        Saves a file locally to the temp folder and assigns it an id.
        """

        try:
            if g.IXIPC_user is None or (not g.IXIPC_user.organizer):
                return json.dumps({'error': 'unauthorized'}), 401
        except:
            return json.dumps({'error': 'unauthorized'}), 401

        if 'file' in request.files:
            f = request.files['file']
        elif 'file' in request.form:
            f = request.form['file']
        else:
            return json.dumps({'error': 'no file uploaded'}), 400

        if f.filename == '':
            return json.dumps({'error': 'no selected file'}), 400
        
        filename = f.filename.replace(' ', '_')

        id = str(uuid.uuid4())
        try:
            f.save(os.path.join(app.config['TEMP_FOLDER'], 'email', id))
        except:
            print(f'failed to save file {filename} with id {id}')
            return json.dumps({'error': 'upload failed'}), 500

        return json.dumps({
            'id': id,
            'name': f'{filename}',
            'attachment': f'{filename}|{id}'
        }), 200


    def fetch_user_emails(address):
        with MailBox(app.config['IMAP_URL']).login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']) as mailbox:
            emails = {
                'sent': [],
                'received': []
            }

            mailbox.folder.set(ALL)
            for msg in mailbox.fetch(AND(from_=address)):
                emails['received'].append(msg)
    
            mailbox.folder.set(SENT)
            for msg in mailbox.fetch(AND(to=address)):
                emails['sent'].append(msg)
                # print(msg.date, msg.subject, len(msg.text or msg.html))

            return emails

    app.fetch_user_emails = fetch_user_emails
