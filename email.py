from flask_mail import Mail, Message
import threading
from imap_tools import MailBox, AND

INBOX = 'INBOX'
SENT = "[Gmail]/Sent Mail"
TRASH = "[Gmail]/Trash"
SPAM = "[Gmail]/Spam"
ALL = "[Gmail]/All Mail"

def register(app):
    # register the email methods
    app.mail = Mail(app)

    def send_email(subject: str, body: str, recipients: list[str]) -> None:
        def _send_email():
            with app.app_context():
                for recipient in recipients:
                    msg = Message(subject, recipients=[recipient], body=body)
                    app.mail.send(msg)
                
                # TODO: log the emails
                print(f'Email sent to {recipients}.')
        t1 = threading.Thread(target=_send_email, name="email")
        t1.start()
    
    app.send_email = send_email

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
