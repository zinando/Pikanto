# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import datetime

class SendMail:
    """class for sending email using sendgrid client"""
    def __init__(self):
        self.template = open("server/instance/email_template.txt", "r")
        self.recipient_email = None
        self.title = ""
        self.date = datetime.datetime.now().strftime("%d, %A %Y")
        self.sender = 'zinando2000@gmail.com'  #  ('Pikanto', 'zinando2000@gmail.com')

    def sendmail(self):
        message = Mail(
            from_email='apps@wullinp.com',
            to_emails='belovedsamex@yahoo.com',
            subject='Sending with Twilio SendGrid is Fun',
            html_content='<strong>and easy to do anywhere, even with Python</strong>')

        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(str(e))

