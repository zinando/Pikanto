# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import webbrowser
import urllib.parse

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

    def send_email_with_application(self, body, attachments=None):
        """Opens the default email client app on your device prefilled with email content to send"""

        # Encode HTML content for the mailto link
        formatted_body = urllib.parse.quote(body)

        mailto_link = f"mailto:{self.recipient_email}?subject={self.subject}&body={formatted_body}&content-type=text/html"

        if attachments:
            attachment_str = "&".join([f"attachment={urllib.parse.quote(file)}" for file in attachments])
            mailto_link += f"&{attachment_str}"

        webbrowser.open(mailto_link)

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
