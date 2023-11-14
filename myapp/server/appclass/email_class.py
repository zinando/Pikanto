from flask_mail import Message
import datetime


class EmailService:
    """class for sending email"""

    def __init__(self):
        self.template = open("server/instance/email_template.txt", "r")
        self.recipient_email = None
        self.title = ""
        self.date = datetime.datetime.now().strftime("%d, %A %Y")
        self.sender = 'zinando2000@gmail.com'  #  ('Pikanto', 'zinando2000@gmail.com')

    def prepare_email(self, body):

        email_body = self.template.read()
        mdate = self.date
        # emailBody=emailBody.replace('#title#',subject)
        email_body = email_body.replace('#title#', '')
        email_body = email_body.replace('#date#', mdate)
        email_body = email_body.replace('#body#', body)

        return email_body

    def sendmail(self, body):
        from server.extensions import mail
        try:
            msg = Message(self.title, sender=self.sender, recipients=[self.recipient_email])
            msg.html = body
            mail.send(msg)
        except Exception as e:
            return {"status": 2, "message": str(e)}

        return {"status": 1, "message": "message sent!"}
