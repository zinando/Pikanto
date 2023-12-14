"""This is the welcome page class module"""
import customtkinter as ctk
from appclasses.labelclass import MyLabel
from helpers import myfunctions as func
from appclasses.report_messenger import Messenger
import os
import threading


class Welcome(ctk.CTk):
    """This creates an instance of a welcome page that appears before the main app window"""

    def __init__(self):
        super(Welcome, self).__init__()
        self.counter = 0
        self.overrideredirect(True)
        self.resizable(False, False)
        width, height = 530, 430
        position_x = (self.winfo_screenwidth() // 2) - (width // 2)
        position_y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry("{}x{}+{}+{}".format(width, height, position_x, position_y))

        bg_image = func.create_image_obj("assets/images/welcome_bg.PNG", size=(460, 260))

        bg_label = MyLabel(self, text="", bg_color="#2f6c60", fg_color="#2f6c60", height=height,
                           width=width).create_obj()
        bg_label.place(x=0, y=0)

        bg_label_image = MyLabel(self, image=bg_image, bg_color="#2f6c60").create_obj()
        bg_label_image.place(x=35, y=65)

        welcome_label = MyLabel(self, text="Logistics Weight Station Console", bg_color="#2f6c60",
                                font="Trebuchet Ms", font_size=22, font_weight="bold", text_color="white",
                                fg_color="#2f6c60").create_obj()
        welcome_label.place(x=102, y=25)

        progress_bar_label = MyLabel(self, text="Loading . . .", font="Trebuchet Ms", font_size=13, font_weight="bold",
                                     fg_color="#2f6c60", bg_color="#2f6c60", text_color="#ffffff").create_obj()
        progress_bar_label.place(x=190, y=350)

        progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", width=400, height=10,
                                          progress_color="#ffbf00",
                                          mode="determinate", determinate_speed=5, corner_radius=5, border_width=1,
                                          bg_color="#2f6c60", fg_color="#2f6c60", border_color="#2f6c60")
        progress_bar.place(x=60, y=380)

        def load_main_window():
            """This will load the main app window and destroy the welcome page"""
            self.load_login_page()
            #self.withdraw()
            #os.system("python main.py")
            #self.destroy()

        def show_progress():
            """This will run the progress bar when counter is equal to or less than 10"""

            if self.counter <= 10:
                txt = "Loading . . .    " + (str(10 * self.counter) + "%")
                progress_bar_label.configure(text=txt)
                progress_bar_label.after(600, show_progress)
                progress_bar.set((10 * self.counter) / 100)
                self.counter += 0.5
            else:
                load_main_window()

        show_progress()

    def load_login_page(self):
        self.withdraw()
        login_page = LoginPage()
        login_page.show_login()


class LoginPage(ctk.CTk):
    def __init__(self):
        super(LoginPage, self).__init__()
        self.resizable(False, False)
        width, height = 1000, 600
        self.w, self.h = width, height
        position_x = (self.winfo_screenwidth() // 2) - (width // 2)
        position_y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry("{}x{}+{}+{}".format(width, height, position_x, position_y))
        self.iconbitmap('assets/icons/app_icon.ico')
        self.title('Pikanto - logistics weight station data manager')
        self.configure(bg="#2f6c60")

        #bg_image = func.create_image_obj("assets/images/welcome_bg.PNG", size=(460, 260))
        #bg_label_image = MyLabel(self, image=bg_image, bg_color="#2f6c60").create_obj()
        #.place(x=35, y=65)

        welcome_label = MyLabel(self, text="Logistics Weight Station Console", bg_color="#2f6c60",
                                font="Trebuchet Ms", font_size=22, font_weight="bold", text_color="white",
                                fg_color="#2f6c60").create_obj()
        welcome_label.place(x=102, y=25)

        email_label = MyLabel(self, text="Email:", font="Trebuchet Ms", font_size=13, fg_color="#ffffff",
                              bg_color="#2f6c60").create_obj()
        email_label.place(x=100, y=150)

        password_label = MyLabel(self, text="Password:", font="Trebuchet Ms", font_size=13, fg_color="#ffffff",
                                 bg_color="#2f6c60").create_obj()
        password_label.place(x=100, y=190)

        self.email_entry = ctk.CTkEntry(self)
        self.email_entry.place(x=200, y=150)

        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_entry.place(x=200, y=190)

        submit_button = ctk.CTkButton(self, text="Submit", command=self.thread_request)
        submit_button.place(x=250, y=230)

    def show_login(self):
        self.mainloop()

    def submit_data(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        # Simulating a response from the database
        response = self.submit_to_database({'email': email, 'password': password})
        if response['status'] == 1:
            self.destroy()  # Close the login page if the submission is successful
            os.system("python main.py")  # Load the main page here
        else:
            error_label = MyLabel(self, text=response['message'], font="Trebuchet Ms", font_size=12,
                                  fg_color="red", bg_color="#2f6c60").create_obj()
            error_label.place(x=150, y=270)

    def thread_request(self):
        """Starts a thread that processes form and data and sends it to the database for storage"""
        # Start a thread to handle the database operation
        thread = threading.Thread(target=self.submit_data)
        thread.daemon = True  # Daemonize the thread to avoid issues on application exit
        thread.start()

    def submit_to_database(self, data):
        worker = Messenger('http://localhost:8088', '/user?action=login')
        response = worker.query_server(data)
        return response


if __name__ == "__main__":
    app = Welcome()
    app.mainloop()
