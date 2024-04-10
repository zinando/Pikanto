"""This view module hosts the codes for creating different views of Pikanto app"""
import customtkinter as ctk
import tkinter as tk
from appclasses.labelclass import MyLabel
from appclasses.email_class import SendMail
from appclasses.buttonclass import MyButton
from appclasses.frameclass import MyFrame
from helpers import myfunctions as func
from appclasses.report_messenger import Messenger
from pyngrok import ngrok
import threading
import requests
import os
import time
import random
import serial


class CreateAppView(ctk.CTk):
    """This class creates the various views after the main window is created"""
    weight_data = None

    def __init__(self):
        """initialized with the properties of the main window class"""
        super(CreateAppView, self).__init__()
        self.data_display_label = None
        self.display_label = None
        self.status_report_display = None
        self.buffer_text = None
        self.server_url = None
        self.state_objects = {}
        self.settings_frame = None
        self.record_view_display = None
        self.status_message = None
        self.unit = None
        self.waybill_tech_email = ''
        self.ngrok_url = None
        # self.weight_data = None
        self.resizable(False, False)
        width, height = 1000, 600
        self.w, self.h = width, height
        position_x = (self.winfo_screenwidth() // 2) - (width // 2)
        position_y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry("{}x{}+{}+{}".format(width, height, position_x, position_y))
        self.iconbitmap('assets/icons/app_icon.ico')
        self.title('Pikanto - logistics weight station data manager')
        self.configure_app_settings()

    def conv(self, st):
        try:
            return int(st)
        except ValueError: #If you get a ValueError
            return float(st)

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
        server_btn = MyButton(server_button_label, text="LogOut", command=self.logout_user, font_size=13,
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
        other_btn = MyButton(request_btns_label, text="Manage", command=self.create_manager_view, font_size=14,
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
        tutorial_two_btn = MyButton(tutorial_btns_label, text="Tutorial 2", command=None,
                                    font_size=14, text_color="#000000", bg_color="#25564c", fg_color="#e3b448",
                                    height=h, width=w, x=x, y=y).create_obj()
        tutorial_two_btn.place(x=x, y=y)

        # tutorial three button
        x = tutorial_one_btn.position_x
        y = tutorial_one_btn.position_y + int(tutorial_one_btn.cget("height")) + 5
        tutorial_three_btn = MyButton(tutorial_btns_label, text="Tutorial 3", command=None,
                                      font_size=14, text_color="#000000", bg_color="#25564c", fg_color="#e3b448",
                                      height=h, width=w, x=x, y=y).create_obj()
        tutorial_three_btn.place(x=x, y=y)

        # tutorial four button
        x = tutorial_two_btn.position_x
        y = tutorial_three_btn.position_y
        tutorial_four_btn = MyButton(tutorial_btns_label, text="Tutorial 4", command=None,
                                     font_size=14, text_color="#000000", bg_color="#25564c", fg_color="#e3b448",
                                     height=h, width=w, x=x, y=y).create_obj()
        tutorial_four_btn.place(x=x, y=y)

        welcome_text = "Welcome to PIKANTO application. Enjoy the ride!"
        # self.display_text(welcome_text)
        self.display_data("0.0")

    def show_scale_data(self):
        """Retrieves the reading on the scale with the set port number"""
        # get scale settings data
        data = self.get_settings_data()

        response = func.get_mass(data)
        if response['status'] != 1:
            self.update_status(response['message'])
            return
        val = response['data']
        self.weight_data = val
        self.display_data(val)

        return

    def configure_app_settings(self):
        """reads the app settings to get settings data and assign to class attributes"""
        data = self.get_settings_data()
        self.unit = data['unit']
        self.server_url = data['server_url']
        self.ngrok_url = data['ngrok_url']
        self.waybill_tech_email = data['waybill_tech_email']
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

    def save_settings(self, data: dict):
        """saves settings data from settings form"""
        func.store_app_settings(data)
        func.notify_user("Settings info updated successfully.")
        return

    def get_settings_data(self):
        """reads the app settings to get all data"""
        mr = {}
        mr['port'] = "COM2"
        mr['baudrate'] = 9600
        mr['parity'] = 'N'
        mr['stopbits'] = 1
        mr['bytesize'] = 8
        mr['server_url'] = self.server_url
        mr['ngrok_url'] = None
        mr['unit'] = 'Kg'
        mr['waybill_tech_email'] = ''

        response = func.read_app_settings()
        if response['status'] == 1:
            if 'port' in response['data'] or 'server_url' in response['data']:
                mr = response['data']

        return mr

    def clear_data(self):
        """Clears the current data on the data screen and replaces it with 0.0"""
        self.weight_data = None
        self.display_data(f"{float(0)}")
        self.update()

    def display_data(self, data=None):
        """Displays data on the data_display label"""
        #self.weight_data = data

        def load_data():
            self.data_display_label.configure(text="{} {}".format(self.weight_data, self.unit))
            self.update()

        if self.weight_data:
            load_data()
            # self.data_display_label.after(300, self.display_data)
            return
        else:
            return

    def open_settings_form(self):
        """creates a form for configuring the app"""
        if not self.settings_frame:
            # get saved settings data
            data = self.get_settings_data()

            def set_value(obj, index):
                """sets value to entry fields ['Com Port:', 'Baudrate:', 'Parity:', 'Stopbits:', 'Bytesize:']"""
                if index == 0:
                    obj.insert(0, f'{data["port"] if data["port"] else ""}')
                elif index == 1:
                    obj.insert(0, f'{data["baudrate"] if data["baudrate"] else ""}')
                elif index == 2:
                    obj.insert(0, f'{data["parity"] if data["parity"] else ""}')
                elif index == 3:
                    obj.insert(0, f'{data["stopbits"] if data["stopbits"] else ""}')
                elif index == 4:
                    obj.insert(0, f'{data["bytesize"] if data["bytesize"] else ""}')
                elif index == 5:
                    obj.insert(0, f'{data["server_url"] if data["server_url"] else ""}')
                elif index == 6:
                    obj.insert(0, f'{data["ngrok_url"] if data["ngrok_url"] else ""}')
                elif index == 7:
                    obj.insert(0, f'{data["waybill_tech_email"] if data["waybill_tech_email"] else ""}')
                elif index == 8:
                    obj.insert(0, f'{data["unit"] if data["unit"] else "Kg"}')

                return

            width = int(self.display_label.cget('width'))
            height = int(self.display_label.cget('height'))

            x, y = 0, 0
            self.settings_frame = ctk.CTkFrame(self.display_label, fg_color="#f0f0f0", height=height, width=width)
            self.settings_frame.place(x=x, y=y)

            # System Settings
            w = width
            dh = (height // 3) + (height // 3) // 2
            system_settings_frame = MyLabel(self.settings_frame, text='', width=width, height=dh,
                                            fg_color="#f0f0f0", x=x, y=y).create_obj()
            system_settings_frame.place(x=x, y=y)

            h = 25
            system_label = MyLabel(system_settings_frame, text="System Settings", height=h, width=w).create_obj()
            system_label.place(x=x, y=y)

            system_labels = ['Comm Port:', 'Baudrate:', 'Parity:', 'Stopbits:', 'Bytesize:']
            system_entries = []

            w = (int(system_settings_frame.cget('width')) - 50) // 4
            h = (int(system_settings_frame.cget('height')) - (int(system_label.cget('height')) + 50)) // 5
            x = 10
            y += int(system_label.cget('height')) + 10

            index = 0
            for label_text in system_labels:
                label = MyLabel(system_settings_frame, text=label_text, width=w, height=h, x=x, y=y
                                ).create_obj()
                label.place(x=x, y=y)

                entry = ctk.CTkEntry(system_settings_frame, width=w)
                dx = x + 10 + label.cget('width')
                entry.position_y, entry.position_x = y, dx
                entry.place(x=dx, y=y)
                system_entries.append(entry)
                # set value for entry
                set_value(entry, index)
                y += 10 + int(label.cget('height'))
                index += 1

            # Server Settings
            x = system_settings_frame.position_x
            y = system_settings_frame.position_y + int(system_settings_frame.cget('height'))
            server_settings_frame = MyLabel(self.settings_frame, text='', width=width, height=height // 3,
                                            fg_color="#f0f0f0", x=x, y=y).create_obj()
            server_settings_frame.place(x=x, y=y)

            h = 25
            x, y = 0, 0
            server_label = MyLabel(server_settings_frame, text="Server Settings", height=h, width=width,
                                   x=x, y=y).create_obj()
            server_label.place(x=x, y=y)

            server_labels = ['Server URL:', 'Ngrok URL:', 'Waybill Tech Email']
            server_entries = []

            w = (int(server_settings_frame.cget('width')) - 50) // 4
            h = int(system_entries[0].cget('height'))
            x = 10
            y += int(server_label.cget('height')) + 10

            for server_label_text in server_labels:
                label = MyLabel(server_settings_frame, text=server_label_text, width=w, height=h, x=x, y=y
                                ).create_obj()
                label.place(x=x, y=y)

                entry = ctk.CTkEntry(server_settings_frame, width=width // 2)
                dx = x + 10 + label.cget('width')
                entry.position_y, entry.position_x = y, dx
                entry.place(x=dx, y=y)
                server_entries.append(entry)
                # set value for entry
                set_value(entry, index)
                y += 10 + int(label.cget('height'))
                index += 1

            # App Settings
            x = server_settings_frame.position_x
            dh = (height // 3) - (height // 3) // 2
            y = server_settings_frame.position_y + int(server_settings_frame.cget('height'))
            app_settings_frame = MyLabel(self.settings_frame, text='', width=width, height=dh,
                                         fg_color="#f0f0f0", x=x, y=y).create_obj()
            app_settings_frame.place(x=x, y=y)

            h = 25
            x, y = 0, 0
            app_label = MyLabel(app_settings_frame, text="App Settings", height=h, width=width,
                                x=x, y=y).create_obj()
            app_label.place(x=x, y=y)

            # add item to any of the frames that have enough space
            w = (int(system_settings_frame.cget('width')) - 50) // 4
            h = (int(system_settings_frame.cget('height')) - (int(system_label.cget('height')) + 50)) // 5
            x = system_entries[0].position_x + int(system_entries[0].cget('width')) + 10
            y = system_entries[0].position_y
            unit_label = MyLabel(system_settings_frame, text="Unit of Measure", width=w, height=h, x=x, y=y
                                 ).create_obj()
            unit_label.place(x=x, y=y)

            unit_entry = ctk.CTkEntry(system_settings_frame, width=w)
            x = x + 10 + int(unit_label.cget('width'))
            unit_entry.place(x=x, y=y)

            # set value for entry
            set_value(unit_entry, index)
            index += 1

            # create buttons inside app settings
            h = 25
            w = 100
            x = (int(app_settings_frame.cget('width')) - (w * 2 + 25)) // 2
            y = app_label.position_y + int(app_label.cget('height')) + 15
            cancel_btn = MyButton(app_settings_frame, text="Cancel", command=None,
                                  font_size=14, text_color="#ffbf00", bg_color="#f0f0f0", fg_color="#6699cc",
                                  height=h, width=w, x=x, y=y).create_obj()
            cancel_btn.place(x=x, y=y)

            x = x + int(cancel_btn.cget('width')) + 25
            submit_btn = MyButton(app_settings_frame, text="Save", command=None,
                                  font_size=14, text_color="#ffbf00", bg_color="#f0f0f0", fg_color="#6699cc",
                                  height=h, width=w, x=x, y=y).create_obj()
            submit_btn.place(x=x, y=y)

            def save_action():
                """saves the entries from the fields"""
                mr = {}
                mr['port'] = system_entries[0].get()
                mr['baudrate'] = int(system_entries[1].get())
                mr['parity'] = system_entries[2].get()
                mr['stopbits'] = int(system_entries[3].get())
                mr['bytesize'] = int(system_entries[4].get())
                mr['server_url'] = server_entries[0].get() if server_entries[0].get() else self.server_url
                mr['ngrok_url'] = server_entries[1].get()
                mr['waybill_tech_email'] = server_entries[2].get()
                mr['unit'] = unit_entry.get() if unit_entry.get() else 'Kg'

                # validate email
                if mr['waybill_tech_email']:
                    if not func.is_valid_email(mr['waybill_tech_email']):
                        msg = "Wrong email. Please input a valid email address"
                        func.notify_user(msg)
                        return

                # validate server url
                if not func.is_valid_url(mr['server_url']):
                    msg = "Wrong server url. Please input a valid url"
                    func.notify_user(msg)
                    return

                self.save_settings(mr)

                # update class variables
                self.configure_app_settings()

                self.settings_frame.destroy()
                self.settings_frame = None
                return

            def cancel_action():
                self.settings_frame.destroy()
                self.settings_frame = None
                return

            submit_btn.configure(command=save_action)
            cancel_btn.configure(command=cancel_action)

        return

    
    def start_ngrok(self):
        """starts the application that issues the public url for our local app"""

        # notify user
        self.state_objects['server_status_text'].configure(text='connecting...')

        # connect ngrok
        try:
            # delay the process. This time should be sufficient to allow the backend server to start running
            time.sleep(2)

            # connect ngrok
            self.ngrok_url = ngrok.connect(8088, domain='roughy-topical-easily.ngrok-free.app') \
                .public_url

            # change states
            self.state_objects['server_status_light'].configure(fg_color='#f0f725')
            time.sleep(1)
            self.update_status('Server Started!')
            self.state_objects['server_status_text'].configure(text='server running...')

            #  print url on the cli
            print(' * TUNNEL URL: ' + self.ngrok_url)
        except Exception as e:
            self.update_status('Start up operation failed with the error: ' + str(e))
            self.state_objects['server_status_text'].configure(text='Startup failed!')

    
    def stop_ngrok(self, url: str):
        """ disconnects ngrock agent from localhost"""
        try:
            ngrok.disconnect(url)
            self.ngrok_url = None

            # change states
            self.state_objects['server_status_light'].configure(fg_color='grey')
            time.sleep(1)
            self.update_status('Server Has Stopped!')
            self.state_objects['server_status_text'].configure(text='server stopped.')
        except Exception as e:
            self.update_status('Stop operation failed with the error: ' + str(e))
            self.state_objects['server_status_text'].configure(text='Failed to stop.')

    def display_text(self, text=None):
        """Displays continuous text on the screen letter_by_letter"""
        if text:
            self.buffer_text = text

        if self.buffer_text:
            words = self.buffer_text.split()
            self.clear_display()
            for word in words:
                self.display_word_letter_by_letter(word)
                time.sleep(0.5)  # Adjust the delay between words as needed
                self.status_report_display.configure(text=self.status_report_display.cget("text") + " ")

        # Schedule the function to run again after 5 seconds
        self.status_report_display.after(5000, self.display_text)

    def clear_display(self):
        self.status_report_display.configure(text="")
        self.update()

    def display_word_letter_by_letter(self, word):
        for letter in word:
            self.status_report_display.configure(text=self.status_report_display.cget("text") + letter)
            self.update()
            time.sleep(0.1)  # Adjust the delay between letters as needed

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

    def thread_request(self, func, *args, **kwargs):
        """Starts a thread that invokes functions for specific actions"""
        # Start a thread to handle the database operation
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True  # Daemonize the thread to avoid issues on application exit
        thread.start()

    def delete_resource(self, resource_id, resource_type, obj):
        """deletes the given resource from database using the id"""
        if self.current_user.admin_type != 'super':
            func.notify_user('You are not authorized to perform this action')
            self.update_status('permission denied.')
            return
        # change the button text
        obj.configure(text="wait...", state='disabled')

        def delete_item(data, url):
            worker = Messenger(self.server_url, url)
            response = worker.query_server(data)
            self.update_status(response['message'])
            func.notify_user(response['message'])
            if response['status'] == 1:
                if resource_type == 'user':
                    self.fetched_resource['users'] = response['data']
                elif resource_type == 'haulier':
                    self.fetched_resource['hauliers'] = response['data']
                elif resource_type == 'customer':
                    self.fetched_resource['customers'] = response['data']
            self.create_manager_view()

            return

        # warn the user if the want to proceed with action
        proceed = tk.messagebox.askokcancel('warning', f'Are you sure you want to delete this {resource_type}')
        if proceed and resource_type == "user":
            url = '/user?action=delete_user'
            data = {'id': resource_id}
            self.thread_request(delete_item, data, url)
        elif proceed and resource_type == "customer":
            url = '/customer?action=delete_customer'
            data = {'id': resource_id}
            self.thread_request(delete_item, data, url)
        elif proceed and resource_type == "haulier":
            url = '/haulier?action=delete_haulier'
            data = {'id': resource_id}
            self.thread_request(delete_item, data, url)

        else:
            obj.configure(text="Delete", state='enabled')

        return
