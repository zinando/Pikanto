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


email_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Waybill Information</title>
    </head>
    <body>
        <!-- Logo -->
            <iframe src="https://silchemicalsltd-my.sharepoint.com/personal/samuel_n_ugeechemicals_com/_layouts/15/embed.aspx?UniqueId=c29cb4e6-7082-46c3-bb9c-3458fa2a0777" width="640" height="360" frameborder="0" scrolling="no" allowfullscreen title="ugee-edited.png"></iframe>
            <!--<img src="https://your-logo-url.com" alt="Company Logo" style="width: 100%; max-width: 600px; display: block; margin: 0 auto;">-->

            <p>You have been requested to review the following information and to append your approval of the waybill
            by clicking providing your Pikanto app password using the below form.</p>
            
            
        {% block content %}
            <!-- Table 1 -->
            <h2>WEIGHBRIDGE SLIP</h2>
            <table>                
                {{table1_data | safe}}
            </table>

            <!-- Table 2 -->
            <hr style="height: 3px; color: blue">
            <h2>WAYBILL DATA</h2>
            <table >                
                {{table2_data | safe}}
            </table>
            <hr style="height: 3px; color: blue">
            <!-- Table 3 -->
            <h2>Products</h2>
            <table border="1">
                <thead>
                    <tr>
                        <th>Product Description</th>
                        <th>Product Code</th>
                        <th>No of Packages (Bags/Boxes)</th>
                        <th>Quantity (MT/NOs)</th>
                        <th>Accepted Quantity</th>
                        <th>Remarks</th>
                        <!-- Add more headers if needed -->
                    </tr>
                </thead>
                <tbody>
                    <!-- Populate table 3 data -->
                    {{table3_data | safe}}
                </tbody>
            </table>

            <!-- Table 4 -->
            <h2>Bad Products</h2>
            <table border="1">
                <thead>
                    <tr>
                        <th>Product Description</th>
                        <th>Damaged Quantity</th>
                        <th>Shortage</th>
                        <th>Batch Number</th>
                        <!-- Add more headers if needed -->
                    </tr>
                </thead>
                <tbody>
                    <!-- Populate table 4 data -->
                    {{table4_data | safe}}
                </tbody>
            </table>

            <hr style="height: 3px; color: blue">
            <!-- Password Form -->
            <div style="color: #e97464">{{response}}</div>
            <h3>Enter your password below to approve:</h3>            
            <form method="post" action="/approve?email={{email}}&wtlog_id={{weight_log_id}}">
                <label for="password">Enter Password:</label>
                <input type="password" id="password" name="password">
                <input type="submit" value="Submit">
            </form>
        {% endblock content %}
    </body>
    </html>
    '''