# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import datetime
import ElasticEmail
from ElasticEmail.api import emails_api
from ElasticEmail.model.email_content import EmailContent
from ElasticEmail.model.body_part import BodyPart
from ElasticEmail.model.body_content_type import BodyContentType
from ElasticEmail.model.transactional_recipient import TransactionalRecipient
from ElasticEmail.model.email_transactional_message_data import EmailTransactionalMessageData
from pprint import pprint
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

class SendMail:
    """class for sending email using sendgrid client"""
    def __init__(self, sender, receiver, subject):
        self.template = open("server/instance/email_template.txt", "r")
        self.recipient_email = receiver
        self.title = "Pikanto Test Email"
        self.subject = subject
        self.date = datetime.datetime.now().strftime("%d, %A %Y")
        self.sender = sender

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

    def send_elastic_email(self):
        """send email using elastic email api service"""
        configuration = ElasticEmail.Configuration()
        configuration.api_key['apikey'] = os.environ.get('ELASTIC_EMAIL_API_KEY')

        with ElasticEmail.ApiClient(configuration) as api_client:
            api_instance = emails_api.EmailsApi(api_client)

            email_transactional_message_data = EmailTransactionalMessageData(
                recipients=TransactionalRecipient(
                    to=self.recipient_email,
                ),
                content=EmailContent(
                    body=[
                        BodyPart(
                            content_type=BodyContentType("HTML"),
                            content="<strong>Mail content.<strong>",
                            charset="utf-8",
                        ),
                        BodyPart(
                            content_type=BodyContentType("PlainText"),
                            content="Mail content.",
                            charset="utf-8",
                        ),
                    ],
                    _from=self.sender,
                    reply_to=self.sender,
                    subject=self.title,
                ),
            )

            try:
                api_response = api_instance.emails_transactional_post(email_transactional_message_data)
                pprint(api_response)
            except ElasticEmail.ApiException as e:
                print("Exception when calling EmailsApi->emails_transactional_post: %s\n" % e)

    def elastic_email_by_smtp(self, email_body, file_paths=None):
        """send email via elastic email smtp server"""
        # Elastic Email SMTP server credentials
        if file_paths is None:
            file_paths = []
        smtp_server = 'smtp.elasticemail.com'
        port = 2525  # Use port 2525 for Elastic Email
        username = os.environ.get('ELASTIC_USERNAME')  # Replace with your Elastic Email username
        password = os.environ.get('ELASTIC_PASSWORD')  # Replace with your Elastic Email password

        sender_email = self.sender
        recipient_email = self.recipient_email

        subject = self.subject
        body = email_body

        # Create a MIMEText object for the email content
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html'))

        # attach files here
        if file_paths:
            if len(file_paths) > 0:
                for file_path in file_paths:
                    with open(file_path, 'rb') as attachment:
                        part = MIMEApplication(attachment.read())
                        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
                        message.attach(part)

        server = smtplib.SMTP(smtp_server, port)

        try:
            # Establish a connection to Elastic Email's SMTP server
            server.starttls()  # Enable encryption
            print('started tls')
            server.login(username, password)  # Login to the SMTP server
            print('logged in successfully')

            # Send the email
            server.sendmail(sender_email, recipient_email, message.as_string())
            print("Email sent successfully!")

        except Exception as e:
            print(f"Failed to send email. Error: {e}")

        finally:
            server.quit()  # Close the connection

        return
