"""This is the welcome page class module"""
import customtkinter as ctk
from appclasses.labelclass import MyLabel
from appclasses.buttonclass import MyButton
from helpers import myfunctions as func
from appclasses.report_messenger import Messenger
import os
import sys
import requests
import threading


class Welcome(ctk.CTk):
    """This creates an instance of a welcome page that appears before the main app window"""

    def __init__(self):
        super(Welcome, self).__init__()
        self.user_info = None
        self.submit_btn = None
        self.counter = 0
        self.url_entry = None
        self.overrideredirect(True)
        self.resizable(False, False)
        width, height = 730, 630  # 530, 430
        self.height = height
        self.width = width
        position_x = (self.winfo_screenwidth() // 2) - (width // 2)
        position_y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry("{}x{}+{}+{}".format(width, height, position_x, position_y))
        self.server_url = self.get_server_url()        

        # calculate image size such that it leaves 35 spaces at side and top
        img_width = width - 70
        img_height = 260

        bg_image = func.create_image_obj("assets/images/welcome_bg.png", size=(img_width, img_height))

        bg_label = MyLabel(self, text="", bg_color="#2f6c60", fg_color="#2f6c60", height=height,
                           width=width).create_obj()
        bg_label.place(x=0, y=0)

        # x = 102
        w = 400
        h = 25
        y = 25
        x = (width - w) // 2
        welcome_label = MyLabel(self, text="Logistics Weight Station Console", bg_color="#2f6c60",
                                font="Trebuchet Ms", font_size=22, font_weight="bold", text_color="white",
                                fg_color="#2f6c60", y=y, width=w, height=h).create_obj()
        welcome_label.place(x=x, y=y)

        w = img_width
        h = img_height
        x = (width - w) // 2
        y = y + int(welcome_label.cget('height')) + 20
        bg_label_image = MyLabel(self, image=bg_image, bg_color="#2f6c60", width=w, height=h,
                                 x=x, y=y).create_obj()
        bg_label_image.place(x=x, y=y)

        w = 400
        self.progress_x = (self.width - w) // 2
        self.progress_y = y + int(bg_label_image.cget('height')) + 30
        self.progress_bar = progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", width=w, height=10,
                                                              progress_color="#ffbf00",
                                                              mode="determinate", determinate_speed=5, corner_radius=5,
                                                              border_width=1,
                                                              bg_color="#2f6c60", fg_color="#2f6c60",
                                                              border_color="#2f6c60")

        self.progress_label_x = 190
        self.progress_label_y = self.progress_y + int(progress_bar.cget('height')) + 50
        self.progress_bar_label = progress_bar_label = MyLabel(self, text="Loading . . .", font="Trebuchet Ms",
                                                               font_size=13, font_weight="bold",
                                                               fg_color="#2f6c60", bg_color="#2f6c60",
                                                               text_color="#ffffff", font_style='italic',
                                                               x=x, y=y).create_obj()
        self.email_entry = None
        self.password_entry = None
        self.repeat_password_entry = None
        self.signup_form = None
        self.login_form = None

        if self.server_url is None:
            self.settings_form = form = self.create_settings_form()
        else:
            self.login_form = form = self.create_login_form()

        h = 50
        w = self.width - 200
        x = (self.width - w) // 2
        y = form.position_y + int(form.cget('height'))
        fg_color = "#2f6c60"
        self.query_status_display = MyLabel(self, text="", fg_color=fg_color, bg_color="#2f6c60",
                                            text_color="#ffbf00", height=h, width=w,
                                            x=x, y=y).create_obj()
        self.query_status_display.place(x=x, y=y)
        self.check_flask_server()

    def check_flask_server(self):
        if not self.server_url:
            self.server_url = "http://localhost:8088"

        try:
            # Try making a request to the local Flask server
            response = requests.get(self.server_url)
            if response.status_code == 200:
                self.display_error_message("Flask server is already running.")
        except requests.ConnectionError:
            self.display_error_message("Flask server is not running.")
            # Start the Flask server
            self.start_flask_server()
        

        return

    def start_flask_server(self):
        print("Starting Flask server...")

        def run_flask_server():
            if os.path.isfile('flask_app.py'):            
                os.system(f"python flask_app.py")
            else:
                os.system(f"flask_app.exe")
            return

        func.thread_request(run_flask_server)


    def create_login_form(self, event=None):
        """creates a form for user login"""
        # reset repeat_password
        self.repeat_password_entry = None

        # destroy signup form if it exists
        if self.signup_form:
            self.signup_form.destroy()

        # create a label to hold the login form fields
        h = 220
        w = self.width - 200
        x = (self.width - w) // 2
        y = self.progress_y
        fg_color = "#2f6c60"
        login_label = MyLabel(self, text="", fg_color=fg_color, bg_color="#2f6c60",
                              text_color="#ffffff", font_style='italic', height=h, width=w,
                              x=x, y=y).create_obj()
        login_label.place(x=x, y=y)

        # create title
        w = int(12.5 * 5)  # 5 is the number of char
        h = 40
        y = 0
        x = (int(login_label.cget('width')) - w) // 2
        title_label = MyLabel(login_label, text="Login", bg_color="#2f6c60",
                              font="Trebuchet Ms", font_size=22, font_weight="bold", text_color="#ffbf00",
                              fg_color="#2f6c60", y=y, width=w, height=h).create_obj()
        title_label.place(x=x, y=y)

        # create login forms

        w = int(12.5 * 9)
        x = 25
        y = y + int(title_label.cget('height')) + 10
        email_label = MyLabel(login_label, text="Email:", bg_color="#2f6c60",
                              font="Trebuchet Ms", font_size=16, text_color="#ffffff",
                              fg_color="#2f6c60", y=y, width=w, height=h).create_obj()
        email_label.place(x=x, y=y)

        x = x + int(email_label.cget('width')) + 20
        self.email_entry = ctk.CTkEntry(login_label, fg_color="transparent", width=350, height=h, text_color="#ffffff")
        self.email_entry.place(x=x, y=y)

        x = 25
        y = y + int(self.email_entry.cget('height')) + 10
        password_label = MyLabel(login_label, text="Password:", bg_color="#2f6c60",
                                 font="Trebuchet Ms", font_size=16, text_color="#ffffff",
                                 fg_color="#2f6c60", y=y, width=w, height=h).create_obj()
        password_label.place(x=x, y=y)

        x = x + int(password_label.cget('width')) + 20
        self.password_entry = ctk.CTkEntry(login_label, fg_color="transparent", width=350, height=h,
                                           text_color="#ffffff", show="*")
        self.password_entry.place(x=x, y=y)

        w = 100
        x = (int(login_label.cget('width')) - w) // 2
        y = y + int(self.password_entry.cget('height')) + 15
        submit_btn = MyButton(login_label, text="Login", command=lambda: func.thread_request(self.login_user),
                              font_size=14, text_color="#ffbf00", bg_color="#2f6c60", fg_color="#6699cc",
                              height=h, width=w, x=x, y=y).create_obj()
        submit_btn.place(x=x, y=y)
        self.submit_btn = submit_btn

        w = int(12.5 * 7)
        x = x + int(submit_btn.cget('width')) + 10
        signup_btn = MyLabel(login_label, text="Sign up here.", bg_color="#2f6c60",
                             font="Trebuchet Ms", font_size=13, text_color="#ffffff",
                             fg_color="#2f6c60", y=y, width=w, height=h, cursor="hand2").create_obj()
        signup_btn.place(x=x, y=y)
        # bind a click event to the text
        signup_btn.bind("<Button-1>", self.create_signup_form)

        # create a link for settings
        w = int(12.5 * 5)
        x = x + int(signup_btn.cget('width')) + 10
        settings_btn = MyLabel(login_label, text="settings", bg_color="#2f6c60",
                               font="Trebuchet Ms", font_size=13, text_color="blue",
                               fg_color="#2f6c60", y=y, width=w, height=h, cursor="hand2").create_obj()
        settings_btn.place(x=x, y=y)

        settings_btn.bind("<Button-1>", self.create_settings_form)

        self.login_form = login_label

        return login_label

    def create_signup_form(self, event=None):
        """creates a form for user signup"""
        # destroy login form
        if self.login_form:
            self.login_form.destroy()

        # create a label to hold the signup form fields
        h = 220
        w = self.width - 200
        x = (self.width - w) // 2
        y = self.progress_y
        fg_color = "#2f6c60"
        signup_label = MyLabel(self, text="", fg_color=fg_color, bg_color="#2f6c60",
                               text_color="#ffffff", font_style='italic', height=h, width=w,
                               x=x, y=y).create_obj()
        signup_label.place(x=x, y=y)

        # create title
        w = int(12.5 * 18)  # 5 is the number of char
        h = 40
        y = 0
        x = (int(signup_label.cget('width')) - w) // 2
        title_label = MyLabel(signup_label, text="Super Admin Signup", bg_color="#2f6c60",
                              font="Trebuchet Ms", font_size=22, font_weight="bold", text_color="#ffbf00",
                              fg_color="#2f6c60", y=y, width=w, height=h).create_obj()
        title_label.place(x=x, y=y)

        # create signup forms

        w = int(12.5 * 9)
        x = 10
        y = y + int(title_label.cget('height')) + 10
        email_label = MyLabel(signup_label, text="Your Email:", bg_color="#2f6c60",
                              font="Trebuchet Ms", font_size=16, text_color="#ffffff",
                              fg_color="#2f6c60", y=y, width=w, height=h).create_obj()
        email_label.place(x=x, y=y)

        x = x + int(email_label.cget('width')) + 10
        self.email_entry = ctk.CTkEntry(signup_label, fg_color="transparent", width=370, height=h, text_color="#ffffff")
        self.email_entry.place(x=x, y=y)

        x = 10
        y = y + int(self.email_entry.cget('height')) + 10
        password_label = MyLabel(signup_label, text="Password:", bg_color="#2f6c60",
                                 font="Trebuchet Ms", font_size=16, text_color="#ffffff",
                                 fg_color="#2f6c60", y=y, width=w, height=h).create_obj()
        password_label.place(x=x, y=y)

        x = x + int(password_label.cget('width')) + 10
        self.password_entry = ctk.CTkEntry(signup_label, fg_color="transparent", width=180, height=h,
                                           text_color="#ffffff", show="*")
        self.password_entry.place(x=x, y=y)

        x = x + int(self.password_entry.cget('width')) + 10
        self.repeat_password_entry = ctk.CTkEntry(signup_label, fg_color="transparent", width=180, height=h,
                                                  text_color="#ffffff", show="*",
                                                  placeholder_text="Repeat password")
        self.repeat_password_entry.place(x=x, y=y)

        w = 100
        x = (int(signup_label.cget('width')) - w) // 2
        y = y + int(self.password_entry.cget('height')) + 15
        submit_btn = MyButton(signup_label, text="Signup", command=lambda: func.thread_request(self.signup_user),
                              font_size=14, text_color="#ffbf00", bg_color="#2f6c60", fg_color="#6699cc",
                              height=h, width=w, x=x, y=y).create_obj()
        submit_btn.place(x=x, y=y)
        self.submit_btn = submit_btn

        w = int(12.5 * 7)
        x = x + int(submit_btn.cget('width')) + 10
        login_btn = MyLabel(signup_label, text="Log in here.", bg_color="#2f6c60",
                            font="Trebuchet Ms", font_size=13, text_color="#ffffff",
                            fg_color="#2f6c60", y=y, width=w, height=h, cursor="hand2").create_obj()
        login_btn.place(x=x, y=y)

        # bind a click event to the text
        login_btn.bind("<Button-1>", self.create_login_form)

        # create a link for settings
        w = int(12.5 * 5)
        x = x + int(login_btn.cget('width')) + 10
        settings_btn = MyLabel(signup_label, text="settings", bg_color="#2f6c60",
                               font="Trebuchet Ms", font_size=13, text_color="blue",
                               fg_color="#2f6c60", y=y, width=w, height=h, cursor="hand2").create_obj()
        settings_btn.place(x=x, y=y)

        settings_btn.bind("<Button-1>", self.create_settings_form)

        self.signup_form = signup_label

        return signup_label

    def create_settings_form(self, event=None):
        """creates a form for user login"""
        # destroy forms if it exists
        if self.signup_form:
            self.signup_form.destroy()
        if self.login_form:
            self.login_form.destroy()

        # create a label to hold the settings form fields
        h = 220
        w = self.width - 200
        x = (self.width - w) // 2
        y = self.progress_y
        fg_color = "#2f6c60"
        login_label = MyLabel(self, text="", fg_color=fg_color, bg_color="#2f6c60",
                              text_color="#ffffff", font_style='italic', height=h, width=w,
                              x=x, y=y).create_obj()
        login_label.place(x=x, y=y)

        # create title
        w = int(12.5 * 10)  # 5 is the number of char
        h = 40
        y = 0
        x = (int(login_label.cget('width')) - w) // 2
        title_label = MyLabel(login_label, text="App Settings", bg_color="#2f6c60",
                              font="Trebuchet Ms", font_size=22, font_weight="bold", text_color="#ffbf00",
                              fg_color="#2f6c60", y=y, width=w, height=h).create_obj()
        title_label.place(x=x, y=y)

        # create form field

        w = int(12.5 * 10)
        x = 25
        y = y + int(title_label.cget('height')) + 10
        url_label = MyLabel(login_label, text="server url", bg_color="#2f6c60",
                            font="Trebuchet Ms", font_size=16, text_color="#ffffff",
                            fg_color="#2f6c60", y=y, width=w, height=h).create_obj()
        url_label.place(x=x, y=y)

        x = x + int(url_label.cget('width')) + 20
        self.url_entry = ctk.CTkEntry(login_label, fg_color="transparent", width=350, height=h, text_color="#ffffff")
        self.url_entry.place(x=x, y=y)

        if self.server_url:
            self.url_entry.insert(0, self.server_url)

        def cancel_action():
            """cancels form"""
            self.create_login_form()
            self.settings_form.destroy()
            self.settings_form = None
            return

        w = 100
        x = (int(login_label.cget('width')) - (w * 2 + 25)) // 2
        y = y + int(self.url_entry.cget('height')) + 15
        cancel_btn = MyButton(login_label, text="Cancel", command=cancel_action,
                              font_size=14, text_color="#ffbf00", bg_color="#2f6c60", fg_color="#6699cc",
                              height=h, width=w, x=x, y=y).create_obj()
        cancel_btn.place(x=x, y=y)

        x = x + int(cancel_btn.cget('width')) + 25
        submit_btn = MyButton(login_label, text="Save", command=self.save_settings,
                              font_size=14, text_color="#ffbf00", bg_color="#2f6c60", fg_color="#6699cc",
                              height=h, width=w, x=x, y=y).create_obj()
        submit_btn.place(x=x, y=y)

        self.settings_form = login_label

        return login_label

    def save_settings(self):
        """retrieves entry data from settings form and saves it"""
        # check it field if empty
        self.display_error_message('')

        if not func.is_valid_url(self.url_entry.get()):
            msg = "Wrong url. Please input a valid url"
            self.display_error_message(msg)
            return

        self.server_url = self.url_entry.get()
        mr = {}
        default = {'port': "COM2", 'baudrate': 9600, 'parity': 'N',
                    'stopbits':1, 'bytesize':8, 'server_url': self.server_url,
                    'ngrok_url': None, 'unit': 'Kg', 'waybill_tech_email': ''}

        # get previous settings data
        prev = func.read_app_settings()
        if prev['status'] != 1:

            # initialize all necessary params with default value
            mr = default
        elif prev['status'] == 1:
            # check if any key in the default dict is missing in the settings data
            for x in default.keys():
                if x not in prev['data'].keys():
                    mr[x] = default.get(x)
        
        mr['server_url'] = self.server_url

        func.store_app_settings(mr)
        func.notify_user("Url saved successfully. You can now log in")

        self.create_login_form()

        self.settings_form.destroy()
        self.settings_form = None

        # check server
        func.thread_request(self.check_flask_server)

        return

    def load_main_window(self):
        """This will load the main app window and destroy the welcome page"""
        
        # check if the packaged app is available otherwise open the unpackaged app
        if os.path.isfile('main.py'):
            self.withdraw()
            os.system(f"python main.py {self.user_info['user_id']}")
            self.destroy()
        elif os.path.isfile('main.exe'):
            self.withdraw()
            os.system(f"main.exe {self.user_info['user_id']}")
            self.destroy()
        else:
            self.display_error_message('main application files not found.')
        return

    def show_progress(self):
        """This will run the progress bar when counter is equal to or less than 10"""
        # remove the login form
        # self.display_error_message("")
        self.login_form.destroy()

        # show progress bar and loading label
        self.progress_bar.place(x=self.progress_x, y=self.progress_y)
        self.progress_bar_label.place(x=self.progress_label_x, y=self.progress_label_y)

        if self.counter <= 10:
            txt = "Loading . . .    " + (str(10 * self.counter) + "%")
            self.progress_bar_label.configure(text=txt)
            self.progress_bar_label.after(600, self.show_progress)
            self.progress_bar.set((10 * self.counter) / 100)
            self.counter += 0.5
        else:
            self.load_main_window()

    # show_progress()
    def display_error_message(self, msg):
        """submits form entries"""
        self.query_status_display.configure(text="")
        self.query_status_display.configure(text=msg)

    def get_form_entries(self):
        """retrieves the text from the entry fields"""
        email = self.email_entry.get()
        password = self.password_entry.get()

        # validate entries
        if not email:
            msg = "email field cannot be empty"
            self.display_error_message(msg)
            return None

        if not func.is_valid_email(email):
            msg = "wrong email format"
            self.display_error_message(msg)
            return None

        if not password:
            msg = "password field cannot be empty"
            self.display_error_message(msg)
            return None

        if self.repeat_password_entry:
            if self.repeat_password_entry.get() != password:
                msg = "Passwords do not match"
                self.display_error_message(msg)
                return None

        # clear all error messages
        self.display_error_message('')

        mr = {}
        mr['email'] = email
        mr['password'] = password

        return mr

    def login_user(self):
        """logs user in after successful authentication"""
        data = self.get_form_entries()

        if data is not None:
            # check for internet connection
            self.check_internet_connection()

            # add sys ip here
            ip = func.get_ip_address()
            self.display_error_message(ip)
            data['ip'] = ip

            # authenticate user here
            worker = Messenger(self.server_url, "/user?action=login-user")
            response = worker.query_server(data)
            if response['status'] != 1:
                self.display_error_message(response['error'])
                return

            self.user_info = response['data']
            self.display_error_message(response['message'])
            self.show_progress()

        return

    def signup_user(self):
        """signs user up and displays the login form"""
        data = self.get_form_entries()

        if data is not None:
            # check for internet connection
            self.check_internet_connection()

            # save user data to database here
            worker = Messenger(self.server_url, "/user?action=signup-super-admin")
            response = worker.query_server(data)
            if response['status'] != 1:
                self.display_error_message(response['error'])
                return

            func.notify_user(response['message'])
            self.create_login_form()

        return

    def check_internet_connection(self):
        """checks that device has internet connection and notifies user"""
        word = "Your device does not have internet connection. Please connect to an active network!"

        def run_notification():
            while not func.is_internet_connected():
                self.submit_btn.configure(state='disabled')
                self.display_error_message(word)
            self.submit_btn.configure(state='enabled')
            self.display_error_message('Internet Connection was restored!')

        if not func.is_internet_connected():
            run_notification()

        return

    def get_server_url(self):
        """reads the app settings to get server url"""
        response = func.read_app_settings()
        if response['status'] == 1:
            url = response['data']['server_url']
        else:
            url = None

        return url


if __name__ == "__main__":
    gui = Welcome()
    gui.mainloop()
