"""This view module hosts the codes for creating different views of Pikanto app"""
import customtkinter as ctk
from appclasses.labelclass import MyLabel
from appclasses.email_class import SendMail
from appclasses.buttonclass import MyButton
from appclasses.frameclass import MyFrame
from helpers import myfunctions as func
from pyngrok import ngrok
import threading
import requests
import os
import time
import random
import serial

class CreateAppView(ctk.CTk):
    """This class creates the various views after the main window is created"""

    def __init__(self):
        """initialized with the properties of the main window class"""
        super(CreateAppView, self).__init__()
        self.data_display_label = None
        self.display_label = None
        self.status_report_display = None
        self.buffer_text = None
        self.server_url = 'http://localhost:8088'
        self.state_objects = {}
        self.port_number = None
        self.record_view_display = None
        self.status_message = None
        self.unit = "Kg"
        self.weight_data = None
        self.resizable(False, False)
        width, height = 1000, 600
        self.w, self.h = width, height
        position_x = (self.winfo_screenwidth() // 2) - (width // 2)
        position_y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry("{}x{}+{}+{}".format(width, height, position_x, position_y))
        self.iconbitmap('assets/icons/app_icon.ico')
        self.title('Pikanto - logistics weight station data manager')

    def create_base_view(self):
        """creates the different widgets found on the app as the main window opens"""

        #  Labels. These are spaces that contain buttons of used to display data

        #  main label. This contains everything visible in the main window
        bg_label = MyLabel(self, text="", bg_color="#2f6c60", fg_color="#2f6c60", height=self.h,
                           width=self.w).create_obj()
        bg_label.place(x=0, y=0)

        #  Ngrok (server) label
        x = 20 + 10 + 100
        y = 10
        server_label = MyLabel(bg_label, text="", bg_color="#2f6c60", fg_color="#2f6c60", height=60, width=100,
                               x=x, y=y).create_obj()
        server_label.place(x=x, y=y)

        #  server title text
        server_text_label = MyLabel(server_label, text="server", bg_color="#2f6c60", fg_color="#ffffff", height=15,
                                    text_color="#6699cc", font_size=10, font="Silkscreen", width=100, x=0, y=0) \
            .create_obj()
        server_text_label.place(x=0, y=0)

        # indicator area
        h, w = 20, int(server_label.cget('width'))
        x, y = server_text_label.position_x, server_text_label.position_y + int(server_text_label.cget('height'))
        indicator = self.create_server_indicator_objects(server_label, w, h, x, y)

        # server start/stop button label
        w = int(server_label.cget('width'))
        h = int(server_label.cget('height')) - int(server_text_label.cget('height')) - int(indicator.cget('height'))
        x = indicator.position_x
        y = indicator.position_y + int(indicator.cget('height'))
        server_button_label = MyLabel(server_label, text="server", bg_color="#2f6c60", fg_color="#2f6c60", height=h,
                                      width=w, x=x, y=y) \
            .create_obj()
        server_button_label.place(x=x, y=y)

        #  action status
        status_report_label_text = MyLabel(bg_label, text="Action Status:", text_color="#6699cc", font_size=14,
                                           font="Silkscreen", bg_color="#2f6c60", fg_color="#2f6c60", height=40,
                                           width=118, x=270, y=10).create_obj()
        status_report_label_text.place(x=270, y=10)

        #  status display area
        d_x = func.addspace(status_report_label_text.position_x, int(status_report_label_text.cget("width"))) + 10
        d_y = status_report_label_text.position_y - 5
        w = self.w - 290 - int(status_report_label_text.cget("width"))
        h = int(status_report_label_text.cget("height")) + 10
        status_report_label = MyLabel(bg_label, text="", text_color="#ffffff", bg_color="#2f6c60", fg_color="#25564c",
                                      height=h, x=d_x, y=d_y, width=w).create_obj()
        status_report_label.place(x=d_x, y=d_y)
        self.status_report_display = status_report_label

        #  main display label area in white fg
        d_y = func.addspace(status_report_label.position_y, int(status_report_label.cget("height"))) + 5
        d_x = status_report_label_text.position_x
        h = self.h - 100
        w = self.w - 280
        self.display_label = MyLabel(self, text="", bg_color="#2f6c60", fg_color="#ffffff", height=h,
                                     width=w, x=d_x, y=d_y).create_obj()
        self.display_label.place(x=d_x, y=d_y)

        #  display for weight inside main display label in cream fg
        w = int(status_report_label.cget("width")) + 40
        h = int(status_report_label.cget("height"))
        x = (int(self.display_label.cget("width")) - w) // 2
        d_y = 5
        self.data_display_label = MyLabel(self.display_label, text="0.0 kg", font_size=22, text_color="#2f6c60",
                                          bg_color="#ffffff",
                                          fg_color="#f5f5f5", height=h, width=w, x=d_x, y=d_y).create_obj()
        self.data_display_label.place(x=x, y=d_y)

        #  read data button area label
        y = func.addspace(10, 50) + 40
        x = 20
        data_manipulation_btns_label = MyLabel(self, text="", bg_color="#2f6c60", fg_color="#25564c", height=100,
                                               width=230, x=x, y=y).create_obj()
        data_manipulation_btns_label.place(x=x, y=y)

        #  report buttons label
        y = 40 + func.addspace(data_manipulation_btns_label.position_y,
                               int(data_manipulation_btns_label.cget("height")))
        x = 20
        request_btns_label = MyLabel(self, text="", bg_color="#2f6c60", fg_color="#25564c", height=100,
                                     width=230, x=x, y=y).create_obj()
        request_btns_label.place(x=x, y=y)

        #  tutorial labels
        y = func.addspace(request_btns_label.position_y, int(request_btns_label.cget("height"))) + 40
        x = request_btns_label.position_x
        tutorial_btns_label = MyLabel(self, text="", bg_color="#2f6c60", fg_color="#25564c", height=150,
                                      width=250, x=x, y=y).create_obj()
        tutorial_btns_label.place(x=x - 10, y=y)

        #  tutorial labels title
        y = 0
        x = 0
        w = int(tutorial_btns_label.cget("width"))
        tutorial_btns_label_title = MyLabel(tutorial_btns_label, text="TUTORIALS", bg_color="#2f6c60",
                                            fg_color="#25564c", height=30, text_color="#ffffff", width=w, x=x, y=y) \
            .create_obj()
        tutorial_btns_label_title.place(x=x, y=y)

        #  buttons

        #  settings button
        settings_btn = MyButton(self, text="Settings", command=self.open_settings_form, font_size=16,
                                font_weight="bold", text_color="#000000", bg_color="#2f6c60", fg_color="#6699cc",
                                height=50, width=100, x=20, y=10).create_obj()
        settings_btn.place(x=20, y=10)

        def thread_request():
            """Starts a thread that processes form and data and sends it to the database for storage"""
            # Start a thread to handle the database operation
            thread = threading.Thread(target=self.start_ngrok)
            thread.daemon = True  # Daemonize the thread to avoid issues on application exit
            thread.start()

        # server start/stop button
        h = int(server_button_label.cget('height')) - 4
        w = int(server_button_label.cget('width')) - 4
        x, y = 2, 2
        server_btn = MyButton(server_button_label, text="Start Server", command=thread_request, font_size=13,
                              text_color="#ffffff", bg_color="#2f6c60", fg_color="#0080ff", corner_radius=0,
                              height=h, width=w, x=x, y=y).create_obj()
        server_btn.place(x=x, y=y)
        self.state_objects['server_button'] = server_btn

        # read data button
        h = (int(data_manipulation_btns_label.cget("height")) - 15) // 2
        w = (int(data_manipulation_btns_label.cget("width")) - 15) // 2
        x = 5
        y = 5
        read_data_btn = MyButton(data_manipulation_btns_label, text="Read Data", command=self.show_scale_data,
                                 font_size=14,
                                 text_color="#ffbf00", bg_color="#2f6c60", fg_color="#6699cc", height=h,
                                 width=w, x=x, y=y).create_obj()
        read_data_btn.place(x=x, y=y)

        #  clear data button
        x = read_data_btn.position_x + int(read_data_btn.cget("width")) + 5
        y = read_data_btn.position_y
        clear_data_btn = MyButton(data_manipulation_btns_label, text="Clear Data", command=self.clear_data,
                                  font_size=14, text_color="#ffbf00",
                                  bg_color="#2f6c60", fg_color="#6699cc", height=h, width=w, x=x, y=y).create_obj()
        clear_data_btn.place(x=x, y=y)

        #  record data button
        y = read_data_btn.position_y + int(read_data_btn.cget("height")) + 5
        x = read_data_btn.position_x
        record_data_btn = MyButton(data_manipulation_btns_label, text="Record Data", command=self.record_data,
                                   font_size=14, text_color="#ffbf00", bg_color="#2f6c60", fg_color="#6699cc",
                                   height=h, width=w, x=x, y=y).create_obj()
        record_data_btn.place(x=x, y=y)

        #  view data records button
        x = clear_data_btn.position_x
        y = record_data_btn.position_y
        view_records_btn = MyButton(data_manipulation_btns_label, text="View Records", command=self.view_weight_records,
                                    font_size=14, text_color="#ffbf00", bg_color="#2f6c60", fg_color="#6699cc",
                                    height=h, width=w, x=x, y=y).create_obj()
        view_records_btn.place(x=x, y=y)

        # generate report button
        h = (int(request_btns_label.cget("height")) - 15) // 2
        w = (int(request_btns_label.cget("width")) - 15) // 2
        x = 5
        y = 5
        generate_report_btn = MyButton(request_btns_label, text="Add Customer", command=self.open_customer_entry,
                                       font_size=14, text_color="#ffbf00", bg_color="#2f6c60", fg_color="#6699cc",
                                       height=h, width=w, x=x, y=y).create_obj()
        generate_report_btn.place(x=x, y=y)

        #  report logs button
        x = generate_report_btn.position_x + int(generate_report_btn.cget("width")) + 5
        y = generate_report_btn.position_y
        report_log_btn = MyButton(request_btns_label, text="Add Haulier", command=self.open_haulier_entry,
                                  font_size=14, text_color="#ffbf00",
                                  bg_color="#2f6c60", fg_color="#6699cc", height=h, width=w, x=x, y=y).create_obj()
        report_log_btn.place(x=x, y=y)

        #  report drafts button
        y = generate_report_btn.position_y + int(generate_report_btn.cget("height")) + 5
        x = generate_report_btn.position_x
        report_drafts_btn = MyButton(request_btns_label, text="Add User", command=self.open_user_entry, font_size=14,
                                     text_color="#ffbf00", bg_color="#2f6c60", fg_color="#6699cc",
                                     height=h, width=w, x=x, y=y).create_obj()
        report_drafts_btn.place(x=x, y=y)

        #  other button
        x = report_log_btn.position_x
        y = report_drafts_btn.position_y
        other_btn = MyButton(request_btns_label, text="Report Report", command=None, font_size=14,
                             text_color="#ffbf00", bg_color="#2f6c60", fg_color="#6699cc", height=h,
                             width=w, x=x, y=y).create_obj()
        other_btn.place(x=x, y=y)

        # tutorial one button
        h = (int(tutorial_btns_label.cget("height")) - int(tutorial_btns_label_title.cget("height")) - 15) // 2
        w = (int(tutorial_btns_label.cget("width")) - 15) // 2
        x = 5
        y = tutorial_btns_label_title.position_y + int(tutorial_btns_label_title.cget("height")) + 5
        tutorial_one_btn = MyButton(tutorial_btns_label, text="Tutorial 1", command=None,
                                    font_size=14, text_color="#000000", bg_color="#25564c", fg_color="#e3b448",
                                    height=h, width=w, x=x, y=y).create_obj()
        tutorial_one_btn.place(x=x, y=y)

        # tutorial two button
        x = tutorial_one_btn.position_x + int(tutorial_one_btn.cget("width")) + 5
        y = tutorial_one_btn.position_y
        tutorial_two_btn = MyButton(tutorial_btns_label, text="Tutorial 2", command=self.show_scale_data,
                                    font_size=14, text_color="#000000", bg_color="#25564c", fg_color="#e3b448",
                                    height=h, width=w, x=x, y=y).create_obj()
        tutorial_two_btn.place(x=x, y=y)

        # tutorial three button
        x = tutorial_one_btn.position_x
        y = tutorial_one_btn.position_y + int(tutorial_one_btn.cget("height")) + 5
        tutorial_three_btn = MyButton(tutorial_btns_label, text="Tutorial 3", command=self.show_scale_data,
                                      font_size=14, text_color="#000000", bg_color="#25564c", fg_color="#e3b448",
                                      height=h, width=w, x=x, y=y).create_obj()
        tutorial_three_btn.place(x=x, y=y)

        # tutorial four button
        x = tutorial_two_btn.position_x
        y = tutorial_three_btn.position_y
        tutorial_four_btn = MyButton(tutorial_btns_label, text="Tutorial 4", command=self.show_scale_data,
                                     font_size=14, text_color="#000000", bg_color="#25564c", fg_color="#e3b448",
                                     height=h, width=w, x=x, y=y).create_obj()
        tutorial_four_btn.place(x=x, y=y)

        welcome_text = "Welcome to PIKANTO application. Enjoy the ride!"
        # self.display_text(welcome_text)
        self.display_data("0.0")

    def show_scale_data(self):
        """Retrieves the reading on the scale with the set port number"""
        port = '/COM3'
        baudrate = 9600
        parity = serial.PARITY_NONE
        stopbits = serial.STOPBITS_ONE
        bytesize = serial.EIGHTBITS

        val = func.get_mass()
        self.display_data(val)

        return

    def update_status(self, message):
        """Pauses animation message on the status display and displays message"""
        self.status_message = message
        self.status_report_display.configure(text=self.status_message)
        self.update()
        time.sleep(5)
        self.status_report_display.configure(text="")
        self.update()
        self.status_message = None

    def save_settings(self, **kwargs):
        """Saves the entries in the settings frame and updates status message display"""
        message = "Entries were saved successfuly!"
        self.port_number = kwargs["port_number"] if "port_number" in kwargs else None
        self.update_status(message)
        self.settings_frame.destroy()

    def clear_data(self):
        """Clears the current data on the data screen and replaces it with 0.0"""
        self.weight_data = None
        self.display_data("0.0")
        self.update()

    def display_data(self, data=None):
        """Displays data on the data_display label"""
        self.weight_data = data

        def load_data():
            self.data_display_label.configure(text="{} {}".format(self.weight_data, self.unit))
            self.update()

        if self.weight_data:
            load_data()
            self.data_display_label.after(300, self.display_data)
        else:
            return

    def open_settings_form(self):
        """creates a form for setting the scale port number"""

        self.settings_frame = MyFrame(self, fg_color="gray", height=int(self.display_label.cget("height")),
                                      width=int(self.display_label.cget("width")))
        self.update()
        port_field = self.settings_frame.create_entry(height=40, width=230, pht="port number to read data from",
                                                      x=self.settings_frame.winfo_x() + 10,
                                                      y=self.settings_frame.winfo_y() + 20)

        d_x = self.settings_frame.winfo_x() + (self.settings_frame.width / 2) - 57
        d_y = self.settings_frame.winfo_y() + (self.settings_frame.height) - 50
        save_btn = self.settings_frame.create_button(width=114, height=30, x=d_x, y=d_y, text="Save Settings",
                                                     bg_color="gray", fg_color="#6699cc",
                                                     command=lambda: self.save_settings(port_number=port_field.get()))

        self.settings_frame.place(x=self.display_label.winfo_x(), y=self.display_label.winfo_y())

        return

    def start_ngrok(self):
        """starts the application that issues the public url for our local app"""

        # notify user
        self.state_objects['server_status_text'].configure(text='connecting...')

        # connect ngrok
        try:
            # disable button action
            self.state_objects['server_button'].configure(command=None)

            # delay the process. This time should be sufficient to allow the backend server to start running
            time.sleep(5)

            # connect ngrok
            my_url = ngrok.connect(8088, domain='roughy-topical-easily.ngrok-free.app') \
                .public_url

            # change states
            self.state_objects['server_status_light'].configure(fg_color='#f0f725')
            time.sleep(1)
            self.update_status('Server Started!')
            self.state_objects['server_status_text'].configure(text='server running...')
            self.state_objects['server_button'].configure(text='Stop Server', command=lambda: self.stop_ngrok(my_url))

            #  print url on the cli
            print(' * TUNNEL URL: ' + my_url)
        except Exception as e:
            self.update_status('Start up operation failed with the error: ' + str(e))
            self.state_objects['server_status_text'].configure(text='Startup failed!')

    def stop_ngrok(self, url: str):
        """ disconnects ngrock agent from localhost"""
        try:
            ngrok.disconnect(url)
            # change states
            self.state_objects['server_status_light'].configure(fg_color='grey')
            time.sleep(1)
            self.update_status('Server Has Stopped!')
            self.state_objects['server_status_text'].configure(text='server stopped.')
            self.state_objects['server_button'].configure(text='Start Server', command=self.start_ngrok)
        except Exception as e:
            self.update_status('Stop operation failed with the error: ' + str(e))
            self.state_objects['server_status_text'].configure(text='Failed to stop.')

    def display_text(self, text=None):
        """Displays continuous text on the screen letter_by_letter"""
        if self.status_message is None:
            if text:
                self.buffer_text = text

            textlist = self.buffer_text.split()
            self.status_report_display.configure(text=" ")

            for xk in textlist:
                count = 0
                while count < len(xk):
                    y = self.status_report_display.cget("text")
                    self.status_report_display.configure(text=y + xk[count])
                    self.update()
                    count += 1
                    time.sleep(0.1)
                y = self.status_report_display.cget("text") + " "
                self.status_report_display.configure(text=y)

        self.status_report_display.after(5000, self.display_text)

    def create_server_indicator_objects(self, window, w, h, x, y):
        """creates the indicator for server status and its side text"""
        #  wrapper label
        indicator = MyLabel(window, text="", bg_color="#2f6c60", fg_color="#25564c", height=h,
                            width=w, x=x, y=y).create_obj()
        indicator.place(x=x, y=y)

        #  indicator light
        x, y = 5, 2
        indicator_light = MyLabel(indicator, text="", bg_color="#2f6c60", fg_color="grey", height=16,
                                  width=16, x=x, y=y, border_radius=8).create_obj()
        indicator_light.place(x=x, y=y)

        # add indicator text to state objects
        self.state_objects['server_status_light'] = indicator_light

        #  indicator text
        w = int(indicator.cget('width')) - 5 - int(indicator_light.cget('width'))
        h = int(indicator.cget('height'))
        x = indicator_light.position_x + int(indicator_light.cget('width')) + 5
        y = indicator_light.position_y
        indicator_text = MyLabel(indicator, text="server stopped.", bg_color="#2f6c60", fg_color="#2f6c60",
                                 height=h, width=w, x=x, y=y, text_color="#ffffff", font_style="italic",
                                 font_size=10).create_obj()
        indicator_text.place(x=x, y=y)

        # add indicator text to state objects
        self.state_objects['server_status_text'] = indicator_text

        return indicator

    def send_report(self):
        """sends report to a designated email"""
        self.update_status('sending report, please wait...')
        self.status_message = 'wait'
        SendMail().elastic_email_by_smtp()
        self.status_message = None

        return

