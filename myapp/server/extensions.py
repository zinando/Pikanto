""" this module will help create instances of extensions such as db"""
from flask import Flask, session, render_template, render_template_string, request, flash
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import func
import json
from server.appclass.email_class import EmailService
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from flask_session import Session
import os
from flask_mail import Mail
from sqlalchemy.dialects.mysql import ENUM
from flask_login import UserMixin

app = Flask(__name__, template_folder='templates')
app.config.from_pyfile('config.py')
cors = CORS(app)


Session(app)
mail = Mail(app)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
migrate = Migrate(app, db)


#  MODELS

class User(UserMixin, db.Model):
    """User class"""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    sname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True)
    admin_type = db.Column(db.String(20), ENUM('approver', 'user', 'admin'),
                           default='user')
    password = db.Column(db.String(225), nullable=False)
    created = db.Column(db.DateTime, default=func.now())
    passresetcode = db.Column(db.String(255), nullable=True)
    last_login = db.Column(db.DateTime, default=func.now())
    last_password_reset = db.Column(db.String(50), nullable=True)
    activated = db.Column(db.Integer, default=0)
    activatecode = db.Column(db.String(255), nullable=True)
    last_activation_code_time = db.Column(db.DateTime(), nullable=True)


class WeightLog(db.Model):
    """this holds weight information for each weighing activity"""

    __tablename__ = "student_class"

    wid = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.String(50), nullable=False, unique=True)
    vehicle_name = db.Column(db.String(50))
    initial_weight = db.Column(db.Integer, nullable=True)  # weight in grams
    initial_time = db.Column(db.DateTime(), default=func.now())
    final_weight = db.Column(db.Integer, nullable=True)  # weight in grams
    final_time = db.Column(db.DateTime())
    # subjects = db.relationship("Subjects", backref="cohort")


class ReportLog(db.Model):
    """This is the report model"""

    __tablename__ = "subjects"

    rid = db.Column(db.Integer, primary_key=True)
    report_date = db.Column(db.DateTime(), default=func.now())
    weight_log_id = db.Column(db.Integer, nullable=True)
    net_weight = db.Column(db.Integer, nullable=True)
    draft_status = db.Column(db.Integer, default=0)
    approval_status = db.Column(db.String(20), ENUM('approved', 'pending'),
                                default='pending')
    approved_by = db.Column(db.String(50))  # approval's email
    approval_time = db.Column(db.DateTime())


class AppSettings(db.Model):
    __tablename__ = 'settings'

    sid = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(50))
    port = db.Column(db.String(50))
    parity = db.Column(db.String(50))
    stopbits = db.Column(db.String(50))
    bytesize = db.Column(db.Integer)
    unit = db.Column(db.String(50))
    number_of_approver = db.Column(db.Integer)
    reg = db.Column(db.DateTime, default=func.now())

    def __repr__(self):
        return self.device_name


#  Functions and Routes

def shutdown_server():
    funck = request.environ.get("werkzeug.server.shutdown")
    if funck is None:
        raise RuntimeError("Flask app is not running with werkzeug server")
    funck()


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.filter_by(id=user_id).first()


@app.get('/shutdown')
def shutdown():
    token = request.args.get('token')
    if token == '0170.0040.1989':
        shutdown_server()
        message = 'server is shutting down'
    else:
        message = 'Not authorized'
    print(message)
    return message


@app.route('/', methods=['POST', 'GET'])
def index():
    email = request.args.get('recipient_email')
    session['email'] = email
    #  return render_template('email_template.html')
    return render_template_string("""
            {% if session['email'] %}
                <h3>Welcome {{ session['email'] }}! Please enter your password to approve this request.</h3>
            {% else %}
                <h3>Welcome! Please enter your password to approve this request</a></h3>
            {% endif %}
            <form method="POST" action="/xws_dse_xgde_dgbnxej_dhegs">
            <label for="email">Enter your password here.</label>
            <input type="password" id="password" name="password" required />
            <button type="submit">Submit</button
        </form>
        """)


@app.route('/xws_dse_xgde_dgbnxej_dhegs', methods=['POST', 'GET'])
def approve_report():
    email = session['email']
    password = request.form['password']
    # user = db.session.query(User).filter(User.email == email).first()
    # if not check_password_hash(user.password, password):
    # flash("Wrong user credentials")
    # return redirect(url_for('index'))
    flash("successfully approved")
    return render_template_string("""     
                {% with messages = get_flashed_messages() %}
                {% if messages %}
                    <div class="notification is-danger">
                        {{ messages[0] }}. Go to <a href="{{ url_for('index') }}">Home Page</a>.
                    </div>
                {% endif %}
                {% endwith %}       
                <h3>Successfully approved</a></h3>            
        """)


@app.route('/send_email', methods=['POST'])
def send_email():
    email_server = EmailService()
    data = request.get_json()
    email_server.recipient_email = data['email']
    email_server.title = data['title']
    email_body = email_server.prepare_email(data['content'])
    response = email_server.sendmail(email_body)

    return json.dumps(response)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8088)
