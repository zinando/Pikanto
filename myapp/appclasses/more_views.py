import threading
from datetime import datetime
from appclasses.labelclass import MyLabel
from appclasses.email_class import SendMail
from appclasses.views import CreateAppView
from appclasses.buttonclass import MyButton
from appclasses.textbox_class import MyTexBox
from helpers import myfunctions as func
import tkinter as tk
from PIL import Image, ImageTk, ImageGrab
import tempfile
import subprocess
import os
import platform
import webbrowser
from tkinter import ttk
import customtkinter as ctk
from appclasses.toplevel_class import DialogueBox
from appclasses.report_messenger import Messenger
from appclasses.dotdict_class import DotDict
from appclasses.group_class import SubGroupCreator
import time
import os


class WindowViews(CreateAppView):
    """This extends the properties of CreateAppView class"""

    def __init__(self):
        """inherit the properties of CreateAppView class"""
        super(WindowViews, self).__init__()
        self.toplevel_sub_window = None
        self.toplevel_window = None
        self.saved_values = {}
        self.counter = 0
        self.bad_counter = 0

    def get_files_dict(self, file_listbox):
        """Generates a files dictionary from the file listbox"""
        files = {}
        count = 1
        for index in range(file_listbox.size()):
            # Get the filepath as listed in the listbox
            file_path = file_listbox.get(index)
            # Get the base name of the file
            base_name = os.path.basename(file_path)
            # Include file object and base name in the files dictionary
            files[f'file_{count}'] = (open(file_path, 'rb'), base_name)
            count += 1
        return files

    def display_data_details(self, data):
        # fetch the required data
        ticket, waybill, products, bad_products, files, approvals_data = self.fetch_details_data(data)
        if ticket is None:
            return

        ticket_data = ticket

        if waybill:
            company_info_data = waybill
        else:
            company_info_data = {
                "waybill_number": "",
                "date": "",
                "location": "",
                "company_ref": "",
                "customer_ref": "",
                "customer_name": "",
                "address": "",
                "vehicle_id": "",
                "transporter": ""
            }

        product_data = products

        bad_products_info = bad_products

        # Create the main window
        if self.toplevel_window is None:
            # Create the main window to fill the screen
            top = tk.Toplevel(self)
            self.toplevel_window = top
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            print("screen is: {}x{}".format(screen_width, screen_height))
            top_width = int(screen_width)
            top_height = int(screen_height * 0.95)
            top.geometry(
                f"{top_width}x{top_height}+{int((screen_width - top_width) / 2)}+{int((screen_height - top_height) / 2)}")
            top.title("Logistics Operations Information")
            # top.overrideredirect(True)
            # top.attributes('-fullscreen', True)

            # Create a frame to hold the ticket and waybill frames side by side
            main_frame = tk.Frame(top)
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Create submain_frame_1 to hold ticket_frame and action_buttons_frame
            submain_frame_1 = tk.Frame(main_frame)
            submain_frame_1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Create the ticket frame inside submain_frame_1
            ticket_frame = self.create_ticket_detail(submain_frame_1, ticket_data)
            ticket_frame.pack(fill=tk.BOTH, expand=True)

            # Create the action buttons frame inside submain_frame_1
            action_buttons_frame = tk.Frame(submain_frame_1)
            action_buttons_frame.pack(fill=tk.X)

            # Create the print button for the ticket frame
            ticket_print_button = ctk.CTkButton(action_buttons_frame, text="Print Ticket", height=25, width=50,
                                                bg_color="#F0F0F0", fg_color="grey", text_color="#ffffff")
            ticket_print_button.pack()

            # Create a thick line between the frames
            separator = tk.Frame(main_frame, width=3, bd=0, relief=tk.SUNKEN)
            separator.pack(side=tk.LEFT, fill=tk.Y)

            # Create submain_frame_2 to hold waybill_frame and waybill_action_buttons_frame
            submain_frame_2 = tk.Frame(main_frame)
            submain_frame_2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Create the waybill frame inside submain_frame_2
            waybill_frame = self.create_waybill_detail(submain_frame_2, company_info_data, product_data,
                                                       bad_products_info, approvals_data)
            waybill_frame.pack(fill=tk.BOTH, expand=True)

            # Create the action buttons frame for waybill inside submain_frame_2
            waybill_action_buttons_frame = tk.Frame(submain_frame_2)
            waybill_action_buttons_frame.pack(fill=tk.X)

            # Create the print button for the waybill frame
            waybill_print_button = ctk.CTkButton(waybill_action_buttons_frame, text="Print Waybill", height=25,
                                                 width=70, bg_color="#F0F0F0", fg_color="grey",
                                                 text_color="#ffffff")
            waybill_print_button.grid(row=0, column=0, padx=10)

            # Create button for approval of the waybill
            waybill_approval_button = ctk.CTkButton(waybill_action_buttons_frame, text="Approve Waybill", height=25,
                                                    width=70, bg_color="#F0F0F0", fg_color="grey",
                                                    text_color="#ffffff")
            waybill_approval_button.grid(row=0, column=1, padx=10)

            if data.approval_status == "approved" or not data.waybill_ready or not data.final_weight:
                waybill_approval_button.configure(state='disabled')

            def thread_request():
                thread = threading.Thread(target=self.approve_waybill, args=[data.id])
                thread.daemon = True  # Daemonize the thread to avoid issues on application exit
                thread.start()

            waybill_approval_button.configure(command=thread_request)

            def print_ticket():
                top.update()
                width = ticket_frame.winfo_width()
                height = ticket_frame.winfo_height()
                x = submain_frame_1.winfo_x()
                y = submain_frame_1.winfo_y()
                print(f"x: {x}, y: {y}, w: {width}, h: {height}")
                self.generate_printable_view(ticket_frame, width, height, x, y)

            def print_waybill():
                top.update()
                width = waybill_frame.winfo_width()
                height = waybill_frame.winfo_height()
                x = submain_frame_2.winfo_x()
                y = submain_frame_2.winfo_y()
                print(f"x: {x}, y: {y}, w: {width}, h: {height}")
                self.generate_printable_view(waybill_frame, width, height, x, y)

            ticket_print_button.configure(command=print_ticket)
            waybill_print_button.configure(command=print_waybill)

            top.protocol("WM_DELETE_WINDOW", self.on_closing)

            # Set weight to make frames equally expandable
            main_frame.grid_columnconfigure(0, weight=1)
            main_frame.grid_columnconfigure(2, weight=1)

        else:
            self.toplevel_window.focus()

    def view_waybill_detailbvb(self, data):
        # fetch the required data
        ticket, waybill, products, bad_products, files, approvals_data = self.fetch_details_data(data)
        if waybill is None:
            return

        if waybill:
            company_info_data = waybill
        else:
            company_info_data = {
                "waybill_number": "",
                "date": "",
                "location": "",
                "company_ref": "",
                "customer_ref": "",
                "customer_name": "",
                "address": "",
                "vehicle_id": "",
                "transporter": ""
            }

        product_data = products

        bad_products_info = bad_products

        # Create the main window
        if self.toplevel_window is None:
            # Create the main window to fill the screen
            top = tk.Toplevel(self)
            self.toplevel_window = top
            screen_width, screen_height = self.get_screen_resolution()
            print("screen is: {}x{}".format(screen_width, screen_height))
            top_width = int(screen_width)
            top_height = int(screen_height * 0.9)
            top.geometry(
                f"{top_width}x{top_height}+{int((screen_width - top_width) / 2)}+{int((screen_height - top_height) / 2)}")
            top.title("Logistics Operations Information")

            waybill_frame = self.create_waybill_detail(top, company_info_data, product_data,
                                                       bad_products_info, approvals_data)
            waybill_frame.pack(fill=tk.BOTH, expand=True)

            # Create the action buttons frame for waybill
            waybill_action_buttons_frame = tk.Frame(top)
            waybill_action_buttons_frame.pack(fill=tk.X)

            # Create the print button for the waybill frame
            waybill_print_button = ctk.CTkButton(waybill_action_buttons_frame, text="Print Waybill", height=25,
                                                 width=70, bg_color="#F0F0F0", fg_color="grey",
                                                 text_color="#ffffff")
            waybill_print_button.grid(row=0, column=0, padx=10)

            # Create button for approval of the waybill
            waybill_approval_button = ctk.CTkButton(waybill_action_buttons_frame, text="Approve Waybill", height=25,
                                                    width=70, bg_color="#F0F0F0", fg_color="grey",
                                                    text_color="#ffffff")
            waybill_approval_button.grid(row=0, column=1, padx=10)

            if data.approval_status == "approved" or not data.waybill_ready or not data.final_weight:
                waybill_approval_button.configure(state='disabled')

            def thread_request():
                thread = threading.Thread(target=self.approve_waybill, args=[data.id])
                thread.daemon = True  # Daemonize the thread to avoid issues on application exit
                thread.start()

            waybill_approval_button.configure(command=thread_request)

            def print_waybill():
                top.update()
                width = waybill_frame.winfo_width()
                height = waybill_frame.winfo_height()
                x = top.winfo_x()
                y = top.winfo_y()
                print(f"x: {x}, y: {y}, w: {width}, h: {height}")
                self.generate_printable_view(waybill_frame, width // 2, height // 2, x, y)

            waybill_print_button.configure(command=print_waybill)

            top.protocol("WM_DELETE_WINDOW", self.on_closing)

        else:
            self.toplevel_window.focus()

    def view_waybill_detail(self, data):
        # fetch the required data
        ticket, waybill, products, bad_products, files, approvals_data = self.fetch_details_data(data)
        if waybill is None:
            return

        if waybill:
            company_info_data = waybill
        else:
            company_info_data = {
                "waybill_number": "",
                "date": "",
                "location": "",
                "company_ref": "",
                "customer_ref": "",
                "customer_name": "",
                "address": "",
                "vehicle_id": "",
                "transporter": ""
            }

        products_data = products

        bad_products_info = bad_products

        # Create the main window
        if self.toplevel_window is None:
            # Create the main window to fill the screen
            w, h = self.get_screen_resolution2()
            top_height = int(h * 0.9)
            screen_width, screen_height = self.get_screen_resolution()  # size of A4
            top_width = screen_width
            top = DialogueBox(top_width, top_height, fg_color="#e3e7f0")

            # Load and resize the header image
            header_image = Image.open('assets/images/ugee_header.PNG')

            # Calculate new height to maintain image aspect ratio
            # aspect_ratio = header_image.width / header_image.height
            # new_height = int(screen_width / aspect_ratio)
            new_height = 200

            # Convert ImageTk.PhotoImage to CTkImage
            header_ctk_image = ctk.CTkImage(light_image=header_image, size=(screen_width, new_height))

            # Create a label to hold the header image
            header_label = MyLabel(top, image=header_ctk_image, width=screen_width, height=new_height,
                                   x=0, y=0).create_obj()
            header_label.place(x=0, y=0)

            # Assign the image to the label to prevent it from being garbage collected
            header_label.image = header_ctk_image

            # create a title for the waybill
            x = header_label.position_x
            y = int(header_label.cget("height")) + header_label.position_y + 2
            waybill_title_label = MyLabel(top, text="WAYBILL", font_size=18, font_weight="bold", x=x, y=y,
                                          font="TkDefaultFont", text_color="blue",
                                          fg_color="#ffffff", width=screen_width, height=25).create_obj()
            waybill_title_label.place(x=x, y=y)

            # create a frame to put canvas and a scroll bar
            h = canvas_height = (top_height - 360) * 2
            w = screen_width * 2
            x = waybill_title_label.position_x
            y = waybill_title_label.position_y + int(waybill_title_label.cget("height"))
            canvas_frame = ctk.CTkFrame(master=top, width=w, height=h)
            canvas_frame.position_x = x
            canvas_frame.position_y = y
            canvas_frame.place(x=x, y=y)

            # create a canvas and put content frame inside the canvas. should be scrollable
            w = int(canvas_frame.cget("width")) - 40
            waybill_canvas = tk.Canvas(canvas_frame, height=h, width=w)  # 1100
            waybill_scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=waybill_canvas.yview)

            # Pack the scrollbar to the right side and expand the canvas
            waybill_scrollbar.pack(side="right", fill="y")
            waybill_canvas.pack(side="left", fill="both", expand=True)

            # create a frame to hold waybill content including products
            content_frame = ctk.CTkFrame(master=waybill_canvas, width=screen_width, height=h)

            # position the content frame inside the canvas
            waybill_canvas.create_window((0, 0), window=content_frame, anchor="nw")
            waybill_canvas.configure(yscrollcommand=waybill_scrollbar.set)

            # create the contents inside the content frame
            # row 1
            content_w = (screen_width - 25) // 4
            h = 25
            x, y = 5, 0
            waybill_number_label = MyLabel(content_frame, text="Waybill Number:", anchor="w", width=content_w,
                                           font="TkDefaultFont", font_size=14, font_weight="bold",
                                           height=h, x=x, y=y).create_obj()
            waybill_number_label.place(x=x, y=y)

            x = x + int(waybill_number_label.cget("width")) + 5
            waybill_number_value_label = MyLabel(content_frame, text=company_info_data['waybill_number'],
                                                 anchor="w", width=content_w, height=h, x=x, y=y).create_obj()
            waybill_number_value_label.place(x=x, y=y)

            x = x + int(waybill_number_value_label.cget("width")) + 5
            date2_label = MyLabel(content_frame, text="Date:", anchor="w", width=content_w,
                                  font="TkDefaultFont", font_size=14, font_weight="bold", height=h, x=x, y=y
                                  ).create_obj()
            date2_label.place(x=x, y=y)

            x = x + int(date2_label.cget("width")) + 5
            date2_value_label = MyLabel(content_frame, text=company_info_data['date'],
                                        anchor="w", width=content_w, height=h, x=x, y=y).create_obj()
            date2_value_label.place(x=x, y=y)

            # row 2
            y = y + 2 + int(date2_value_label.cget("height"))
            x = 5
            location_label = MyLabel(content_frame, text="Location:", anchor="w", width=content_w,
                                     font="TkDefaultFont", font_size=14, font_weight="bold", height=h, x=x, y=y
                                     ).create_obj()
            location_label.place(x=x, y=y)

            x = x + int(location_label.cget("width")) + 5
            location_value_label = MyLabel(content_frame, text=company_info_data['location'],
                                           anchor="w", width=content_w, height=h, x=x, y=y).create_obj()
            location_value_label.place(x=x, y=y)

            x = x + int(location_value_label.cget("width")) + 5
            company_ref_label = MyLabel(content_frame, text="Ugee Ref No:", anchor="w", width=content_w,
                                        font="TkDefaultFont", font_size=14, font_weight="bold", height=h, x=x, y=y
                                        ).create_obj()
            company_ref_label.place(x=x, y=y)

            x = x + int(company_ref_label.cget("width")) + 5
            company_ref_value_label = MyLabel(content_frame, text=company_info_data['company_ref'],
                                              anchor="w", width=content_w, height=h, x=x, y=y).create_obj()
            company_ref_value_label.place(x=x, y=y)

            # row 3
            y = y + int(company_ref_value_label.cget("height")) + 2
            x = 5
            customer_ref_label = MyLabel(content_frame, text="Customer Ref No:", anchor="w", width=content_w,
                                         font="TkDefaultFont", font_size=14, font_weight="bold", height=h, x=x, y=y
                                         ).create_obj()
            customer_ref_label.place(x=x, y=y)

            x = x + int(customer_ref_label.cget("width")) + 5
            customer_ref_value_label = MyLabel(content_frame, text=company_info_data['customer_ref'],
                                               anchor="w", width=content_w, height=h, x=x, y=y).create_obj()
            customer_ref_value_label.place(x=x, y=y)

            x = x + int(customer_ref_value_label.cget("width")) + 5
            customer_name_label = MyLabel(content_frame, text="Customer Name:", anchor="w", width=content_w,
                                          font="TkDefaultFont", font_size=14, font_weight="bold", height=h, x=x, y=y
                                          ).create_obj()
            customer_name_label.place(x=x, y=y)

            x = x + int(customer_name_label.cget("width")) + 5
            customer_name_value_label = MyLabel(content_frame, text=company_info_data['customer_name'],
                                                anchor="w", width=content_w, height=h, x=x, y=y).create_obj()
            customer_name_value_label.place(x=x, y=y)

            # row 4
            y = y + int(customer_name_value_label.cget("height")) + 2
            x = 5
            address_label = MyLabel(content_frame, text="Delivery Address:", anchor="w", width=content_w,
                                    font="TkDefaultFont", font_size=14, font_weight="bold", height=h, x=x, y=y
                                    ).create_obj()
            address_label.place(x=x, y=y)

            x = x + int(address_label.cget("width")) + 5
            address_value_label = MyLabel(content_frame, text=company_info_data['address'],
                                          anchor="w", width=content_w, height=h, x=x, y=y).create_obj()
            address_value_label.place(x=x, y=y)

            x = x + int(address_value_label.cget("width")) + 5
            vehicle_id_label = MyLabel(content_frame, text="Vehicle No:", anchor="w", width=content_w,
                                       font="TkDefaultFont", font_size=14, font_weight="bold", height=h, x=x, y=y
                                       ).create_obj()
            vehicle_id_label.place(x=x, y=y)

            x = x + int(vehicle_id_label.cget("width")) + 5
            vehicle_id_value_label = MyLabel(content_frame, text=company_info_data['vehicle_id'],
                                             anchor="w", width=content_w, height=h, x=x, y=y).create_obj()
            vehicle_id_value_label.place(x=x, y=y)

            # row 5
            y = y + int(vehicle_id_value_label.cget("height")) + 2
            x = 5
            transporter_label = MyLabel(content_frame, text="Transporter:", anchor="w", width=content_w,
                                        font="TkDefaultFont", font_size=14, font_weight="bold", height=h, x=x, y=y
                                        ).create_obj()
            transporter_label.place(x=x, y=y)

            x = x + int(transporter_label.cget("width")) + 5
            transporter_value_label = MyLabel(content_frame, text=company_info_data['transporter'],
                                              anchor="w", width=content_w, height=h, x=x, y=y).create_obj()
            transporter_value_label.place(x=x, y=y)

            # create products title label
            y = y + 2 + int(transporter_value_label.cget("height"))
            x = 5
            w = screen_width - 10
            products_title_label = MyLabel(content_frame, text="Products", font_size=18, font_weight="bold", x=x, y=y,
                                           font="TkDefaultFont", text_color="grey",
                                           fg_color="#ffffff", width=w, height=25).create_obj()
            products_title_label.place(x=x, y=y)

            # create products label
            y = y + int(products_title_label.cget("height"))
            x = 0
            w = screen_width
            print(canvas_height)
            print(y)
            h = (canvas_height - y) // 2
            products_label = MyLabel(content_frame, text="", x=x, y=y,
                                     fg_color="#ffffff", width=w, height=h).create_obj()
            products_label.place(x=x, y=y)

            # create products detail
            self.create_product_detail(products_label, products_data)

            # create bad products title label
            y = y + 2 + int(products_label.cget("height"))
            x = 5
            w = screen_width - 10
            bad_products_title_label = MyLabel(content_frame, text="Bad Products", font_size=18, font_weight="bold",
                                               x=x, y=y,
                                               font="TkDefaultFont", text_color="grey",
                                               fg_color="#ffffff", width=w, height=25).create_obj()
            bad_products_title_label.place(x=x, y=y)

            # create bad products label
            y = y + int(bad_products_title_label.cget("height"))
            x = 0
            w = screen_width
            h = h - int(bad_products_title_label.cget("height"))
            bad_products_label = MyLabel(content_frame, text="", x=x, y=y,
                                         fg_color="#ffffff", width=w, height=h).create_obj()
            bad_products_label.place(x=x, y=y)

            # create bad products detail
            self.create_bad_product_detail(bad_products_label, bad_products_info)

            # create another frame for the approvals

            # create action buttons under the approval frame

            self.toplevel_window = top

            top.protocol("WM_DELETE_WINDOW", self.on_closing)

        else:
            self.toplevel_window.focus()

    def get_screen_resolution2(self):
        # Create a hidden Tkinter window to access screen information
        root = tk.Tk()
        root.attributes('-alpha', 0)  # Hide the window

        # Get the screen width and height in pixels
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        root.destroy()

        return screen_width, screen_height

    def create_ticket_detail(self, window, ticket_data):
        # create a frame for the ticket
        ticket_frame = tk.Frame(window, bd=3, relief=tk.SUNKEN)

        # create header image
        w, h = self.get_screen_resolution()
        image_width = w - 6  # 6 = 2x3 where 3 is the separator thickness btw the two frames
        image_frame = self.create_header_image(ticket_frame, int(image_width))
        image_frame.pack(fill=tk.X, pady=5)

        # Create a title label for "Weighbridge Slip"
        ticket_title_label = ctk.CTkLabel(ticket_frame, text="WEIGHBRIDGE SLIP",
                                          font=("TkDefaultFont", 18, "bold"), text_color="blue",
                                          fg_color="#ffffff")
        ticket_title_label.pack(fill=tk.X, pady=10)

        # create a label to display the ticket information
        ticket_content_label = tk.Frame(ticket_frame, bg="#ffffff")
        ticket_content_label.pack(fill=tk.X)

        # create labels for each content data
        # row 1
        date_label = ctk.CTkLabel(ticket_content_label, text="Date:", width=50, anchor="w",
                                  font=("TkDefaultFont", 14, "bold"))
        date_label.grid(row=0, column=0, padx=5, sticky="w")
        date_value_label = ctk.CTkLabel(ticket_content_label, text=ticket_data['date'], width=50, anchor="w")
        date_value_label.grid(row=0, column=1, padx=5, sticky="w")
        ticket_number_label = ctk.CTkLabel(ticket_content_label, text="Ticket Number:", width=50, anchor="w",
                                           font=("TkDefaultFont", 14, "bold"))
        ticket_number_label.grid(row=0, column=2, padx=5, sticky="w")
        ticket_number_value_label = ctk.CTkLabel(ticket_content_label, text=ticket_data['ticket_number'],
                                                 width=50, anchor="w")
        ticket_number_value_label.grid(row=0, column=3, padx=5, sticky="w")

        # row 2
        vehicle_label = ctk.CTkLabel(ticket_content_label, text="Vehicle Reg:", width=50, anchor="w",
                                     font=("TkDefaultFont", 14, "bold"))
        vehicle_label.grid(row=1, column=0, padx=5, sticky="w")
        vehicle_value_label = ctk.CTkLabel(ticket_content_label, text=ticket_data['vehicle_id'],
                                           width=50, anchor="w")
        vehicle_value_label.grid(row=1, column=1, padx=5, sticky="w")
        delivery_number_label = ctk.CTkLabel(ticket_content_label, text="Delivery Number:", width=50, anchor="w",
                                             font=("TkDefaultFont", 14, "bold"))
        delivery_number_label.grid(row=1, column=2, padx=5, sticky="w")
        delivery_number_value_label = ctk.CTkLabel(ticket_content_label, text=ticket_data['delivery_number'],
                                                   width=50, anchor="w")
        delivery_number_value_label.grid(row=1, column=3, padx=5, sticky="w")

        # row 3
        customer_label = ctk.CTkLabel(ticket_content_label, text="Customer:", width=50, anchor="w",
                                      font=("TkDefaultFont", 14, "bold"))
        customer_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        customer_value_label = ctk.CTkLabel(ticket_content_label, text=ticket_data['customer_name'],
                                            width=50, anchor="w")
        customer_value_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        order_number_label = ctk.CTkLabel(ticket_content_label, text="Order Number:", width=50, anchor="w",
                                          font=("TkDefaultFont", 14, "bold"))
        order_number_label.grid(row=2, column=2, padx=5, pady=5, sticky="w")
        order_number_value_label = ctk.CTkLabel(ticket_content_label, text=ticket_data['order_number'],
                                                width=50, anchor="w")
        order_number_value_label.grid(row=2, column=3, padx=5, pady=5, sticky="w")

        # row 4
        haulier_label = ctk.CTkLabel(ticket_content_label, text="Haulier:", width=50, anchor="w",
                                     font=("TkDefaultFont", 14, "bold"))
        haulier_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        haulier_value_label = ctk.CTkLabel(ticket_content_label, text=ticket_data['haulier'], width=50, anchor="w")
        haulier_value_label.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        destination_label = ctk.CTkLabel(ticket_content_label, text="Destination:", width=50, anchor="w",
                                         font=("TkDefaultFont", 14, "bold"))
        destination_label.grid(row=3, column=2, padx=5, pady=5, sticky="w")
        destination_value_label = ctk.CTkLabel(ticket_content_label, text=ticket_data['destination'],
                                               width=50, anchor="w")
        destination_value_label.grid(row=3, column=3, padx=5, pady=5, sticky="w")

        # row 5
        product_label = ctk.CTkLabel(ticket_content_label, text="Product:", width=50, anchor="w",
                                     font=("TkDefaultFont", 14, "bold"))
        product_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        product_value_label = ctk.CTkLabel(ticket_content_label, text=ticket_data['product'], width=50, anchor="w")
        product_value_label.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # row 6
        first_weight_label = ctk.CTkLabel(ticket_content_label, text="Gross Mass:", width=50, anchor="w",
                                          font=("TkDefaultFont", 14, "bold"))
        first_weight_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        first_weight_value_label = ctk.CTkLabel(ticket_content_label, text=ticket_data['final_weight'],
                                                width=50, anchor="w")
        first_weight_value_label.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        # row 7
        second_weight_label = ctk.CTkLabel(ticket_content_label, text="Tare Mass:", width=50, anchor="w",
                                           font=("TkDefaultFont", 14, "bold"))
        second_weight_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")
        second_weight_value_label = ctk.CTkLabel(ticket_content_label, text=ticket_data['initial_weight'],
                                                 width=50, anchor="w")
        second_weight_value_label.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        # row 8
        net_weight_label = ctk.CTkLabel(ticket_content_label, text="Net Mass:", width=50, anchor="w",
                                        font=("TkDefaultFont", 14, "bold"))
        net_weight_label.grid(row=7, column=0, padx=5, pady=5, sticky="w")
        net_weight_value_label = ctk.CTkLabel(ticket_content_label, text=ticket_data['net_weight'],
                                              width=50, anchor="w")
        net_weight_value_label.grid(row=7, column=1, padx=5, pady=5, sticky="w")

        # row 9
        driver_label = ctk.CTkLabel(ticket_content_label, text="Driver Name:", width=50, anchor="w",
                                    font=("TkDefaultFont", 14, "bold"))
        driver_label.grid(row=8, column=0, padx=5, pady=5, sticky="w")
        driver_value_label = ctk.CTkLabel(ticket_content_label, text=ticket_data['driver'],
                                          width=50, anchor="w")
        driver_value_label.grid(row=8, column=1, padx=5, pady=5, sticky="w")
        signature_label = ctk.CTkLabel(ticket_content_label, text="Driver Signature:", width=50, anchor="w",
                                       font=("TkDefaultFont", 14, "bold"))
        signature_label.grid(row=8, column=2, padx=5, pady=5, sticky="w")
        signature_value_label = ctk.CTkLabel(ticket_content_label, text="............................",
                                             width=50, anchor="w")
        signature_value_label.grid(row=8, column=3, padx=5, pady=5, sticky="w")

        return ticket_frame

    def create_waybill_detailvcv(self, window, company_info_data, product_info, bad_product_info, approvals_data):
        w, h = self.get_screen_resolution()
        # create a frame for the waybill
        waybill_frame = tk.Frame(window, bd=3, relief=tk.SUNKEN, height=h, width=w)

        # create header image
        image_width = w
        image_frame = self.create_header_image(waybill_frame, int(image_width))
        image_frame.pack(fill=tk.X, pady=5)

        # create a title for the waybill
        waybill_title_label = ctk.CTkLabel(waybill_frame, text="WAYBILL",
                                           font=("TkDefaultFont", 18, "bold"), text_color="blue",
                                           fg_color="#ffffff")
        waybill_title_label.pack(fill=tk.X, pady=10)

        # create a Frame for the contents
        waybill_content_frame = tk.Frame(waybill_frame, bg="#ffffff")
        waybill_content_frame.pack(fill=tk.X)

        # After creating the waybill_content_frame
        waybill_canvas = tk.Canvas(waybill_content_frame, height=h, width=w)  # 1100
        waybill_scrollbar = tk.Scrollbar(waybill_content_frame, orient="vertical", command=waybill_canvas.yview)
        waybill_scrollable_frame = tk.Frame(waybill_canvas, width=w)
        waybill_products_title_label = ctk.CTkLabel(waybill_canvas, text="Products", width=w,
                                                    font=("TkDefaultFont", 16, "bold"), text_color="black",
                                                    fg_color="#ffffff")
        waybill_products_frame = tk.Frame(waybill_canvas, width=w)
        waybill_bad_products_title_label = ctk.CTkLabel(waybill_canvas, text="Bad/Damaged Products",
                                                        font=("TkDefaultFont", 16, "bold"), width=w,
                                                        text_color="black", fg_color="#ffffff")
        waybill_approvals_frame = tk.Frame(waybill_canvas)
        waybill_bad_products_frame = tk.Frame(waybill_canvas, width=w)

        waybill_canvas.create_window((0, 0), window=waybill_scrollable_frame, anchor="nw")
        waybill_canvas.configure(yscrollcommand=waybill_scrollbar.set)

        # Pack the scrollbar to the right side and expand the canvas
        waybill_scrollbar.pack(side="right", fill="y")
        waybill_canvas.pack(side="left", fill="both", expand=True)

        # Configure scrollbar and canvas
        waybill_canvas.bind("<Configure>",
                            lambda e: waybill_canvas.configure(scrollregion=waybill_canvas.bbox("all")))

        # create labels for company info

        # row 1
        content_w = w // 700
        waybill_number_label = ctk.CTkLabel(waybill_scrollable_frame, text="Waybill Number:", anchor="w",
                                            font=("TkDefaultFont", 14, "bold"))
        waybill_number_label.grid(row=0, column=0, padx=5, sticky="nsew")
        window.columnconfigure(0, weight=1)

        waybill_number_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['waybill_number'],
                                                  anchor="w")
        waybill_number_value_label.grid(row=0, column=1, padx=5, sticky="nsew")
        window.columnconfigure(0, weight=1)

        date2_label = ctk.CTkLabel(waybill_scrollable_frame, text="Date:", anchor="w",
                                   font=("TkDefaultFont", 14, "bold"))
        date2_label.grid(row=0, column=2, padx=5, sticky="nsew")
        window.columnconfigure(0, weight=1)

        date2_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['date'],
                                         anchor="w")
        date2_value_label.grid(row=0, column=3, padx=5, sticky="nsew")
        window.columnconfigure(0, weight=1)

        location_label = ctk.CTkLabel(waybill_scrollable_frame, text="Location:", anchor="w",
                                      font=("TkDefaultFont", 14, "bold"))
        location_label.grid(row=0, column=4, padx=5, sticky="nsew")
        window.columnconfigure(0, weight=1)

        location_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['location'],
                                            anchor="w")
        location_value_label.grid(row=0, column=5, padx=5, sticky="nsew")
        window.columnconfigure(0, weight=1)

        # row 2
        company_ref_label = ctk.CTkLabel(waybill_scrollable_frame, text="Ugee Reference No:", anchor="w",
                                         font=("TkDefaultFont", 14, "bold"), width=140 * content_w)
        company_ref_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        company_ref_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['company_ref'],
                                               anchor="w", width=90 * content_w)
        company_ref_value_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        customer_ref_label = ctk.CTkLabel(waybill_scrollable_frame, text="Customer Ref No:", anchor="w",
                                          font=("TkDefaultFont", 14, "bold"), width=120 * content_w)
        customer_ref_label.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        customer_ref_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['customer_ref'],
                                                anchor="w", width=90 * content_w)
        customer_ref_value_label.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        customer_name_label = ctk.CTkLabel(waybill_scrollable_frame, text="Customer Name:", anchor="w",
                                           font=("TkDefaultFont", 14, "bold"), width=110 * content_w)
        customer_name_label.grid(row=1, column=4, padx=5, pady=5, sticky="w")
        customer_name_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['customer_name'],
                                                 anchor="w", width=90 * content_w)
        customer_name_value_label.grid(row=1, column=5, padx=5, pady=5, sticky="w")

        # row 3
        address_label = ctk.CTkLabel(waybill_scrollable_frame, text="Delivery Address:", anchor="w",
                                     font=("TkDefaultFont", 14, "bold"), width=140 * content_w)
        address_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        address_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['address'],
                                           anchor="w", width=90 * content_w)
        address_value_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        vehicle_id_label = ctk.CTkLabel(waybill_scrollable_frame, text="Vehicle No:", anchor="w",
                                        font=("TkDefaultFont", 14, "bold"), width=120 * content_w)
        vehicle_id_label.grid(row=2, column=2, padx=5, pady=5, sticky="w")
        vehicle_id_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['vehicle_id'],
                                              anchor="w", width=90 * content_w)
        vehicle_id_value_label.grid(row=2, column=3, padx=5, pady=5, sticky="w")
        transporter_label = ctk.CTkLabel(waybill_scrollable_frame, text="Transporter:", anchor="w",
                                         font=("TkDefaultFont", 14, "bold"), width=110 * content_w)
        transporter_label.grid(row=2, column=4, padx=5, pady=5, sticky="w")
        transporter_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['transporter'],
                                               anchor="w", width=90 * content_w)
        transporter_value_label.grid(row=2, column=5, padx=5, pady=5, sticky="w")

        waybill_canvas.create_window((0, 200), window=waybill_products_title_label, anchor="nw")

        waybill_canvas.create_window((0, 300), window=waybill_products_frame, anchor="nw")

        # create products detail
        self.create_product_detail(waybill_products_frame, product_info)

        waybill_canvas.create_window((0, 500), window=waybill_bad_products_title_label, anchor="nw")

        waybill_canvas.create_window((0, 600), window=waybill_bad_products_frame, anchor="nw")

        # create bad products detail
        self.create_bad_product_detail(waybill_bad_products_frame, bad_product_info)

        waybill_canvas.create_window((0, 800), window=waybill_approvals_frame, anchor="nw")

        # create approval detail
        self.create_waybill_approvals(waybill_approvals_frame, approvals_data)

        return waybill_frame

    def create_waybill_detail(self, window, company_info_data, product_info, bad_product_info, approvals_data):
        w, h = window.width, window.height
        # create a frame for the waybill
        waybill_frame = window

        # create header image
        image_width = w
        image_frame = self.create_header_image(waybill_frame, int(image_width))
        image_frame.pack(fill=tk.X, pady=5)

        # create a title for the waybill
        waybill_title_label = ctk.CTkLabel(waybill_frame, text="WAYBILL",
                                           font=("TkDefaultFont", 18, "bold"), text_color="blue",
                                           fg_color="#ffffff")
        waybill_title_label.pack(fill=tk.X, pady=10)

        # create a Frame for the contents
        waybill_content_frame = tk.Frame(waybill_frame, bg="#ffffff")
        waybill_content_frame.pack(fill=tk.X)

        # After creating the waybill_content_frame
        waybill_canvas = tk.Canvas(waybill_content_frame, height=h, width=w)  # 1100
        waybill_scrollbar = tk.Scrollbar(waybill_content_frame, orient="vertical", command=waybill_canvas.yview)
        waybill_scrollable_frame = tk.Frame(waybill_canvas, width=w)
        waybill_products_title_label = ctk.CTkLabel(waybill_canvas, text="Products", width=w,
                                                    font=("TkDefaultFont", 16, "bold"), text_color="black",
                                                    fg_color="#ffffff")
        waybill_products_frame = tk.Frame(waybill_canvas, width=w)
        waybill_bad_products_title_label = ctk.CTkLabel(waybill_canvas, text="Bad/Damaged Products",
                                                        font=("TkDefaultFont", 16, "bold"), width=w,
                                                        text_color="black", fg_color="#ffffff")
        waybill_approvals_frame = tk.Frame(waybill_canvas)
        waybill_bad_products_frame = tk.Frame(waybill_canvas, width=w)

        waybill_canvas.create_window((0, 0), window=waybill_scrollable_frame, anchor="nw")
        waybill_canvas.configure(yscrollcommand=waybill_scrollbar.set)

        # Pack the scrollbar to the right side and expand the canvas
        waybill_scrollbar.pack(side="right", fill="y")
        waybill_canvas.pack(side="left", fill="both", expand=True)

        # Configure scrollbar and canvas
        waybill_canvas.bind("<Configure>",
                            lambda e: waybill_canvas.configure(scrollregion=waybill_canvas.bbox("all")))

        # create labels for company info

        # row 1
        content_w = w // 700
        waybill_number_label = ctk.CTkLabel(waybill_scrollable_frame, text="Waybill Number:", anchor="w",
                                            font=("TkDefaultFont", 14, "bold"))
        waybill_number_label.grid(row=0, column=0, padx=5, sticky="nsew")
        window.columnconfigure(0, weight=1)

        waybill_number_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['waybill_number'],
                                                  anchor="w")
        waybill_number_value_label.grid(row=0, column=1, padx=5, sticky="nsew")
        window.columnconfigure(0, weight=1)

        date2_label = ctk.CTkLabel(waybill_scrollable_frame, text="Date:", anchor="w",
                                   font=("TkDefaultFont", 14, "bold"))
        date2_label.grid(row=0, column=2, padx=5, sticky="nsew")
        window.columnconfigure(0, weight=1)

        date2_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['date'],
                                         anchor="w")
        date2_value_label.grid(row=0, column=3, padx=5, sticky="nsew")
        window.columnconfigure(0, weight=1)

        location_label = ctk.CTkLabel(waybill_scrollable_frame, text="Location:", anchor="w",
                                      font=("TkDefaultFont", 14, "bold"))
        location_label.grid(row=0, column=4, padx=5, sticky="nsew")
        window.columnconfigure(0, weight=1)

        location_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['location'],
                                            anchor="w")
        location_value_label.grid(row=0, column=5, padx=5, sticky="nsew")
        window.columnconfigure(0, weight=1)

        # row 2
        company_ref_label = ctk.CTkLabel(waybill_scrollable_frame, text="Ugee Reference No:", anchor="w",
                                         font=("TkDefaultFont", 14, "bold"), width=140 * content_w)
        company_ref_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        company_ref_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['company_ref'],
                                               anchor="w", width=90 * content_w)
        company_ref_value_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        customer_ref_label = ctk.CTkLabel(waybill_scrollable_frame, text="Customer Ref No:", anchor="w",
                                          font=("TkDefaultFont", 14, "bold"), width=120 * content_w)
        customer_ref_label.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        customer_ref_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['customer_ref'],
                                                anchor="w", width=90 * content_w)
        customer_ref_value_label.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        customer_name_label = ctk.CTkLabel(waybill_scrollable_frame, text="Customer Name:", anchor="w",
                                           font=("TkDefaultFont", 14, "bold"), width=110 * content_w)
        customer_name_label.grid(row=1, column=4, padx=5, pady=5, sticky="w")
        customer_name_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['customer_name'],
                                                 anchor="w", width=90 * content_w)
        customer_name_value_label.grid(row=1, column=5, padx=5, pady=5, sticky="w")

        # row 3
        address_label = ctk.CTkLabel(waybill_scrollable_frame, text="Delivery Address:", anchor="w",
                                     font=("TkDefaultFont", 14, "bold"), width=140 * content_w)
        address_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        address_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['address'],
                                           anchor="w", width=90 * content_w)
        address_value_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        vehicle_id_label = ctk.CTkLabel(waybill_scrollable_frame, text="Vehicle No:", anchor="w",
                                        font=("TkDefaultFont", 14, "bold"), width=120 * content_w)
        vehicle_id_label.grid(row=2, column=2, padx=5, pady=5, sticky="w")
        vehicle_id_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['vehicle_id'],
                                              anchor="w", width=90 * content_w)
        vehicle_id_value_label.grid(row=2, column=3, padx=5, pady=5, sticky="w")
        transporter_label = ctk.CTkLabel(waybill_scrollable_frame, text="Transporter:", anchor="w",
                                         font=("TkDefaultFont", 14, "bold"), width=110 * content_w)
        transporter_label.grid(row=2, column=4, padx=5, pady=5, sticky="w")
        transporter_value_label = ctk.CTkLabel(waybill_scrollable_frame, text=company_info_data['transporter'],
                                               anchor="w", width=90 * content_w)
        transporter_value_label.grid(row=2, column=5, padx=5, pady=5, sticky="w")

        waybill_canvas.create_window((0, 200), window=waybill_products_title_label, anchor="nw")

        waybill_canvas.create_window((0, 300), window=waybill_products_frame, anchor="nw")

        # create products detail
        self.create_product_detail(waybill_products_frame, product_info)

        waybill_canvas.create_window((0, 500), window=waybill_bad_products_title_label, anchor="nw")

        waybill_canvas.create_window((0, 600), window=waybill_bad_products_frame, anchor="nw")

        # create bad products detail
        self.create_bad_product_detail(waybill_bad_products_frame, bad_product_info)

        waybill_canvas.create_window((0, 800), window=waybill_approvals_frame, anchor="nw")

        # create approval detail
        self.create_waybill_approvals(waybill_approvals_frame, approvals_data)

        return waybill_frame

    def create_waybill_approvals(self, widget, approvals_data):
        if approvals_data:
            data = approvals_data
        else:
            data = {}
            data['approval_status'] = "pending"
            data['received_by'] = ""
            data['approval_date'] = ""
            data['approver'] = ""
            data['delivered_by'] = ""
            data['received_date'] = ""

            # create three equal headers for the approvals
        sn_label = ctk.CTkLabel(widget, text="Received By", width=230, bg_color="#f0f0f0", height=50,
                                fg_color="#b2acab", text_color="black")
        sn_label.grid(row=0, column=0)
        description_label = ctk.CTkLabel(widget, text="Delivered By", width=230, bg_color="#f0f0f0",
                                         fg_color="#b2acab", text_color="black", height=50)
        description_label.grid(row=0, column=1)
        code_label = ctk.CTkLabel(widget, text="Authorized By", width=230, bg_color="#f0f0f0",
                                  fg_color="#b2acab", text_color="black", height=50)
        code_label.grid(row=0, column=2)

        # insert values under the headers
        for x in range(3):
            text = ""
            if x == 2:
                text += f"NAME:   {data['approver']}\n\n" if data['approval_status'] == "approved" else f"NAME:\n\n"
                text += f"SIGNATURE:   Approved.\n\n" if data['approval_status'] == "approved" else f"SIGNATURE:\n\n"
                text += f"DATE:   {data['approval_date']}" if data['approval_status'] == "approved" else f"DATE:"
            elif x == 1:
                text += f"NAME:   {data['delivered_by']}\n\n"
                text += f"SIGNATURE:   .................................\n\n"
                text += f"DATE:   {datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')}" if data[
                                                                                            'delivered_by'] != "" else f"DATE:\n\n"
            elif x == 0:
                text += f"NAME:   {data['received_by']}\n\n"
                text += f"SIGNATURE:   received by me.\n\n" if data['received_by'] != "" else f"SIGNATURE:\n\n"
                text += f"DATE:   {data['received_date']}"

            ctk.CTkLabel(widget, text=text, width=230, anchor="w", justify="left").grid(row=1, column=x)

        return

    def create_product_detail(self, widget, product_info):
        # create labels for the headers
        h = 35
        w = (int(widget.cget("width")) - 40) // 7
        x, y = 5, 5
        sn_label = MyLabel(widget, text="S/N", font_size=14, font_weight="bold", x=x, y=y,
                           font="TkDefaultFont", text_color="black", bg_color="#f0f0f0",
                           fg_color="#B2ACAB", width=w - 20, height=h).create_obj()
        sn_label.place(x=x, y=y)

        x = x + int(sn_label.cget("width")) + 5
        description_label = MyLabel(widget, text="Description", font_size=14, font_weight="bold", x=x, y=y,
                                    font="TkDefaultFont", text_color="black", bg_color="#f0f0f0",
                                    fg_color="#B2ACAB", width=w + 20, height=h).create_obj()
        description_label.place(x=x, y=y)

        x = x + int(description_label.cget("width")) + 5
        code_label = MyLabel(widget, text="Item Code", font_size=14, font_weight="bold", x=x, y=y,
                             font="TkDefaultFont", text_color="black", bg_color="#f0f0f0",
                             fg_color="#B2ACAB", width=w, height=h).create_obj()
        code_label.place(x=x, y=y)

        x = x + int(code_label.cget('width')) + 5
        packages_label = MyLabel(widget, text="No of Packages\n (Bags/Boxes)", font_size=14, font_weight="bold", x=x,
                                 y=y,
                                 font="TkDefaultFont", text_color="black", bg_color="#f0f0f0",
                                 fg_color="#B2ACAB", width=w, height=h).create_obj()
        packages_label.place(x=x, y=y)

        x = x + int(packages_label.cget("width")) + 5
        quantity_label = MyLabel(widget, text="Quantity\n (MT/NOs)", font_size=14, font_weight="bold", x=x, y=y,
                                 font="TkDefaultFont", text_color="black", bg_color="#f0f0f0",
                                 fg_color="#B2ACAB", width=w, height=h).create_obj()
        quantity_label.place(x=x, y=y)

        x = x + int(quantity_label.cget('width')) + 5
        accepted_label = MyLabel(widget, text="Accepted\n qty", font_size=14, font_weight="bold", x=x, y=y,
                                 font="TkDefaultFont", text_color="black", bg_color="#f0f0f0",
                                 fg_color="#B2ACAB", width=w, height=h).create_obj()
        accepted_label.place(x=x, y=y)

        x = x + int(accepted_label.cget("width")) + 5
        remarks_label = MyLabel(widget, text="Remarks", font_size=14, font_weight="bold", x=x, y=y,
                                font="TkDefaultFont", text_color="black", bg_color="#f0f0f0",
                                fg_color="#B2ACAB", width=w, height=h).create_obj()
        remarks_label.place(x=x, y=y)

        # populate the table with data
        counter = 1
        y = y + int(remarks_label.cget('height')) + 2
        if product_info:
            for item in product_info:
                col = 0
                x = 5
                col_1 = MyLabel(widget, text=counter, font_size=14, x=x, y=y,
                                text_color="black", width=w - 20, height=h).create_obj()
                col_1.place(x=x, y=y)

                x = x + int(col_1.cget("width")) + 5
                col_2 = MyLabel(widget, text=item['product_description'], font_size=14, x=x, y=y,
                                text_color="black", width=w + 20, height=h).create_obj()
                col_2.place(x=x, y=y)

                x = x + int(col_2.cget("width")) + 5
                col_3 = MyLabel(widget, text=item['item_code'], font_size=14, x=x, y=y,
                                text_color="black", width=w, height=h).create_obj()
                col_3.place(x=x, y=y)

                x = x + int(col_3.cget("width")) + 5
                col_4 = MyLabel(widget, text=item['packages'], font_size=14, x=x, y=y,
                                text_color="black", width=w, height=h).create_obj()
                col_4.place(x=x, y=y)

                x = x + int(col_4.cget("width")) + 5
                col_5 = MyLabel(widget, text=item['quantity'], font_size=14, x=x, y=y,
                                text_color="black", width=w, height=h).create_obj()
                col_5.place(x=x, y=y)

                x = x + int(col_5.cget("width")) + 5
                col_6 = MyLabel(widget, text=item['accepted'], font_size=14, x=x, y=y,
                                text_color="black", width=w, height=h).create_obj()
                col_6.place(x=x, y=y)

                x = x + int(col_6.cget("width")) + 5
                col_7 = MyLabel(widget, text=item['remarks'], font_size=14, x=x, y=y,
                                text_color="black", width=w, height=h).create_obj()
                col_7.place(x=x, y=y)

                y = y + int(col_7.cget("height")) + 2
                counter += 1
        return

    def create_bad_product_detail(self, widget, bad_product_info):
        # create labels for the headers
        # create labels for the headers
        h = 35
        w = (int(widget.cget("width")) - 30) // 5
        x, y = 5, 5
        sn_label = MyLabel(widget, text="S/N", font_size=14, font_weight="bold", x=x, y=y,
                           font="TkDefaultFont", text_color="black", bg_color="#f0f0f0",
                           fg_color="#B2ACAB", width=w - 20, height=h).create_obj()
        sn_label.place(x=x, y=y)

        x = x + int(sn_label.cget("width")) + 5
        description_label = MyLabel(widget, text="Description", font_size=14, font_weight="bold", x=x, y=y,
                                    font="TkDefaultFont", text_color="black", bg_color="#f0f0f0",
                                    fg_color="#B2ACAB", width=w + 20, height=h).create_obj()
        description_label.place(x=x, y=y)

        x = x + int(description_label.cget("width")) + 5
        code_label = MyLabel(widget, text="Damaged Qty", font_size=14, font_weight="bold", x=x, y=y,
                             font="TkDefaultFont", text_color="black", bg_color="#f0f0f0",
                             fg_color="#B2ACAB", width=w, height=h).create_obj()
        code_label.place(x=x, y=y)

        x = x + int(code_label.cget('width')) + 5
        packages_label = MyLabel(widget, text="Shortage Qty", font_size=14, font_weight="bold", x=x,
                                 y=y,
                                 font="TkDefaultFont", text_color="black", bg_color="#f0f0f0",
                                 fg_color="#B2ACAB", width=w, height=h).create_obj()
        packages_label.place(x=x, y=y)

        x = x + int(packages_label.cget("width")) + 5
        quantity_label = MyLabel(widget, text="Batch Number", font_size=14, font_weight="bold", x=x, y=y,
                                 font="TkDefaultFont", text_color="black", bg_color="#f0f0f0",
                                 fg_color="#B2ACAB", width=w, height=h).create_obj()
        quantity_label.place(x=x, y=y)

        # populate the table with data
        y = y + int(quantity_label.cget('height')) + 2
        if bad_product_info:
            counter = 1
            for item in bad_product_info:
                col = 0
                x = 5
                col_1 = MyLabel(widget, text=counter, font_size=14, x=x, y=y,
                                text_color="black", width=w - 20, height=h).create_obj()
                col_1.place(x=x, y=y)

                x = x + int(col_1.cget("width")) + 5
                col_2 = MyLabel(widget, text=item['product_description'], font_size=14, x=x, y=y,
                                text_color="black", width=w + 20, height=h).create_obj()
                col_2.place(x=x, y=y)

                x = x + int(col_2.cget("width")) + 5
                col_3 = MyLabel(widget, text=item['damaged_quantity'], font_size=14, x=x, y=y,
                                text_color="black", width=w, height=h).create_obj()
                col_3.place(x=x, y=y)

                x = x + int(col_3.cget("width")) + 5
                col_4 = MyLabel(widget, text=item['shortage_quantity'], font_size=14, x=x, y=y,
                                text_color="black", width=w, height=h).create_obj()
                col_4.place(x=x, y=y)

                x = x + int(col_4.cget("width")) + 5
                col_5 = MyLabel(widget, text=item['batch_number'], font_size=14, x=x, y=y,
                                text_color="black", width=w, height=h).create_obj()
                col_5.place(x=x, y=y)

                y = y + int(col_5.cget("height")) + 2
                counter += 1

        return

    def create_header_image(self, window, win_width):
        image_frame = tk.Frame(window)
        image_frame.pack(fill=tk.X)

        placeholder_image = Image.open('assets/images/ugee_header.PNG')
        image_width, image_height = placeholder_image.size

        # Resize the image to fit the width of the window
        window_width = win_width
        ratio = window_width / image_width
        new_height = int(image_height * ratio)
        resized_image = placeholder_image.resize((window_width, new_height), Image.ANTIALIAS)

        # Convert image for Tkinter
        img = ImageTk.PhotoImage(resized_image)

        # Create a label for the image and display it in the image frame
        image_label = tk.Label(image_frame, image=img)
        image_label.image = img  # Keep a reference to avoid garbage collection
        image_label.pack(fill=tk.X)
        return image_frame

    def open_customer_entry(self):
        """
        Opens a custom top-level window for logging customer information.
        """
        if self.toplevel_window is None:

            customer_window = ctk.CTkToplevel(self)
            customer_window.geometry("{}x{}".format(480, 230))
            customer_window.title("Customer Information")

            ctk.CTkLabel(customer_window, text="Customer Name:").grid(row=0, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Customer Address:").grid(row=1, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Registration (Ref) Number:").grid(row=2, column=0, padx=5, pady=10)

            name_entry = ctk.CTkEntry(customer_window, width=250)
            address_entry = ctk.CTkEntry(customer_window, width=250)
            reg_entry = ctk.CTkEntry(customer_window, width=250)

            name_entry.grid(row=0, column=1, padx=5, pady=10)
            address_entry.grid(row=1, column=1, padx=5, pady=10)
            reg_entry.grid(row=2, column=1, padx=5, pady=10)

            submit_btn = ctk.CTkButton(customer_window, text="Save")
            submit_btn.grid(row=3, column=0, padx=5, pady=10)

            def save_customer_info():
                """
                Fetches customer information from entry fields, creates a dictionary,
                and sends it to an API route to save it to a database.
                """
                submit_btn.configure(text="Processing...")
                customer_name = name_entry.get()
                customer_address = address_entry.get()
                customer_reg_number = reg_entry.get()

                if not customer_name or not customer_reg_number:
                    submit_btn.configure(text='Save')
                    func.notify_user('Customer name or reg number cannot be empty.')
                    self.toplevel_window.focus()
                    return

                customer_data = {
                    'name': customer_name,
                    'address': customer_address,
                    'ref': customer_reg_number
                }

                messenger = Messenger(self.server_url, '/customer?action=save_data')
                resp = messenger.query_server(data=customer_data)
                submit_btn.configure(text="Finished!")
                self.update_status(resp['message'])
                customer_window.destroy()
                self.toplevel_window = None
                return

            def cancel_window():
                """
                Closes the customer information window without saving any data.
                """
                self.toplevel_window = None
                customer_window.destroy()

            def thread_request():
                """Starts a thread that processes form and data and sends it to the database for storage"""
                # Start a thread to handle the database operation
                thread = threading.Thread(target=save_customer_info)
                thread.daemon = True  # Daemonize the thread to avoid issues on application exit
                thread.start()

            submit_btn.configure(command=thread_request)
            cancel_btn = ctk.CTkButton(customer_window, text="Cancel", command=cancel_window)
            cancel_btn.grid(row=3, column=1, padx=5, pady=10)

            customer_window.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.toplevel_window = customer_window

        else:
            self.toplevel_window.focus()

    def get_screen_resolution(self):
        # Create a hidden Tkinter window to access screen information
        root = tk.Tk()
        root.attributes('-alpha', 0)  # Hide the window

        # Get the screen width and height in pixels
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # A4 size in millimeters
        a4_width_mm = 210
        a4_height_mm = 297

        # Calculate A4 size in pixels based on screen resolution
        screen_width_in_mm = (screen_width * 25.4) / root.winfo_fpixels('1i')  # Convert screen width to mm
        screen_height_in_mm = (screen_height * 25.4) / root.winfo_fpixels('1i')  # Convert screen height to mm

        a4_width_pixels = int((a4_width_mm / screen_width_in_mm) * screen_width)
        a4_height_pixels = int((a4_height_mm / screen_height_in_mm) * screen_height)

        root.destroy()

        return a4_width_pixels, a4_height_pixels

    def open_haulier_entry(self):
        """
        Opens a custom top-level window for logging transport company information.
        """
        if self.toplevel_window is None:

            customer_window = ctk.CTkToplevel(self)
            customer_window.geometry("{}x{}".format(480, 230))
            customer_window.title("Transport Company Information")

            ctk.CTkLabel(customer_window, text="Haulier Name:").grid(row=0, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Address:").grid(row=1, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Registration (Ref) Number:").grid(row=2, column=0, padx=5, pady=10)

            name_entry = ctk.CTkEntry(customer_window, width=250)
            address_entry = ctk.CTkEntry(customer_window, width=250)
            reg_entry = ctk.CTkEntry(customer_window, width=250)

            name_entry.grid(row=0, column=1, padx=5, pady=10)
            address_entry.grid(row=1, column=1, padx=5, pady=10)
            reg_entry.grid(row=2, column=1, padx=5, pady=10)

            submit_btn = ctk.CTkButton(customer_window, text="Save")
            submit_btn.grid(row=3, column=0, padx=5, pady=10)

            def save_haulier_info():
                """
                Fetches haulier information from entry fields, creates a dictionary,
                and sends it to an API route to save it to a database.
                """
                submit_btn.configure(text="Processing...")
                haulier_name = name_entry.get()
                haulier_address = address_entry.get()
                haulier_reg_number = reg_entry.get()
                if not haulier_name or not haulier_reg_number:
                    submit_btn.configure(text='Save')
                    func.notify_user('Haulier name or reg number cannot be empty.')
                    self.toplevel_window.focus()
                    return

                haulier_data = {
                    'name': haulier_name,
                    'address': haulier_address,
                    'ref': haulier_reg_number
                }

                messenger = Messenger(self.server_url, '/haulier?action=save_data')
                resp = messenger.query_server(data=haulier_data)
                submit_btn.configure(text="Finished!")
                self.update_status(resp['message'])
                customer_window.destroy()
                self.toplevel_window = None
                return

            def cancel_window():
                """
                Closes the haulier information window without saving any data.
                """
                self.toplevel_window = None
                customer_window.destroy()

            def thread_request():
                """Starts a thread that processes form and data and sends it to the database for storage"""
                # Start a thread to handle the database operation
                thread = threading.Thread(target=save_haulier_info)
                thread.daemon = True  # Daemonize the thread to avoid issues on application exit
                thread.start()

            submit_btn.configure(command=thread_request)
            cancel_btn = ctk.CTkButton(customer_window, text="Cancel", command=cancel_window)
            cancel_btn.grid(row=3, column=1, padx=5, pady=10)

            customer_window.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.toplevel_window = customer_window

        else:
            self.toplevel_window.focus()

    def open_user_entry(self):
        """
        Opens a custom top-level window for logging user information.
        """
        if self.toplevel_window is None:

            customer_window = ctk.CTkToplevel(self)
            customer_window.geometry("{}x{}".format(420, 350))
            customer_window.title("New User Information")

            ctk.CTkLabel(customer_window, text="First Name:").grid(row=0, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Last Name:").grid(row=1, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Email:").grid(row=2, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Admin Type:").grid(row=3, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Password:").grid(row=4, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Confirm Password:").grid(row=5, column=0, padx=5, pady=10)

            first_name_entry = ctk.CTkEntry(customer_window, width=250)
            last_name_entry = ctk.CTkEntry(customer_window, width=250)
            email_entry = ctk.CTkEntry(customer_window, width=250)
            admin_type_entry = ctk.CTkComboBox(customer_window, values=["user", "admin", "approver"], width=250)
            password_entry = ctk.CTkEntry(customer_window, width=250)
            confirm_password_entry = ctk.CTkEntry(customer_window, width=250)
            admin_type_entry.set('Select')  # Set default value

            first_name_entry.grid(row=0, column=1, padx=5, pady=10)
            last_name_entry.grid(row=1, column=1, padx=5, pady=10)
            email_entry.grid(row=2, column=1, padx=5, pady=10)
            admin_type_entry.grid(row=3, column=1, padx=5, pady=10)
            password_entry.grid(row=4, column=1, padx=5, pady=10)
            confirm_password_entry.grid(row=5, column=1, padx=5, pady=10)

            submit_btn = ctk.CTkButton(customer_window, text="Save")
            submit_btn.grid(row=6, column=1, padx=5, pady=10)

            def save_user_info():
                """
                Fetches user information from entry fields, creates a dictionary,
                and sends it to an API route to save it to a database.
                """
                submit_btn.configure(text="Processing...")

                first_name = first_name_entry.get()
                last_name = last_name_entry.get()
                email = email_entry.get()
                # validate email
                if not func.is_valid_email(email) and email != 'admin':
                    submit_btn.configure(text='Save')
                    func.notify_user('Not a valid email!')
                    self.toplevel_window.focus()
                    return
                admin_type = admin_type_entry.get() if admin_type_entry.get() else 'user'

                # validate password
                if not password_entry.get() or password_entry.get() != confirm_password_entry.get():
                    submit_btn.configure(text='Save')
                    func.notify_user('The two passwords do not match!')
                    self.toplevel_window.focus()
                    return
                if len(password_entry.get()) < 8:
                    submit_btn.configure(text='Save')
                    func.notify_user('Password must be at least 8 characters long!')
                    self.toplevel_window.focus()
                    return

                password = password_entry.get()

                user_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'admin_type': admin_type,
                    'password': password
                }

                messenger = Messenger(self.server_url, '/user?action=save_data')
                resp = messenger.query_server(data=user_data)
                submit_btn.configure(text="Finished!")
                self.update_status(resp['message'])
                customer_window.destroy()
                self.toplevel_window = None
                return

            def cancel_window():
                """
                Closes the haulier information window without saving any data.
                """
                self.toplevel_window = None
                customer_window.destroy()

            def thread_request():
                """Starts a thread that processes form and data and sends it to the database for storage"""
                # Start a thread to handle the database operation
                thread = threading.Thread(target=save_user_info)
                thread.daemon = True  # Daemonize the thread to avoid issues on application exit
                thread.start()

            submit_btn.configure(command=thread_request)
            cancel_btn = ctk.CTkButton(customer_window, text="Cancel", command=cancel_window)
            cancel_btn.grid(row=6, column=0, padx=5, pady=10)

            customer_window.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.toplevel_window = customer_window

        else:
            self.toplevel_window.focus()

    def open_waybill_entry(self, item):
        """
        Opens a custom top-level window for logging waybill information.
        """
        customer_list = {}
        for customer in item.customers:
            customer_list[customer['customer_name']] = customer['customer_id']
        files = []
        counter = 0
        if self.toplevel_window is None:

            customer_window = ctk.CTkToplevel(self)
            customer_window.geometry("{}x{}".format(650, 640))
            customer_window.title("New Waybill Information")

            ctk.CTkLabel(customer_window, text="Customer:").grid(row=0, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Waybill Number:").grid(row=1, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Delivery Address:").grid(row=2, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Product Condition:").grid(row=3, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Transport Company:").grid(row=4, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Driver's Name:").grid(row=5, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Products:").grid(row=6, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Bad Products:").grid(row=7, column=0, padx=5, pady=10)
            log_product = ctk.CTkButton(customer_window, text="Log Products")
            log_product.grid(row=8, column=0, padx=5, pady=10)
            bad_product = ctk.CTkButton(customer_window, text="Log Bad Products")
            bad_product.grid(row=8, column=1, padx=5, pady=10)

            # create a table for displaying products added to the waybill
            product_frame, treeview = self.product_treeview(customer_window)
            product_frame.grid(row=6, column=1, padx=0, pady=10)

            # create a table for displaying bad products added to the waybill
            bad_product_frame, bad_treeview = self.bad_product_treeview(customer_window)
            bad_product_frame.grid(row=7, column=1, padx=0, pady=10)

            # create a function that will call for creation of product form
            def add_products():
                """opens the product entry form"""
                if self.toplevel_sub_window:
                    self.toplevel_sub_window.focus()
                    return
                self.open_product_entry(treeview)
                return

            # create a function that will call for creation of bad products form
            def add_bad_products():
                """opens the bad product entry form"""
                if self.toplevel_sub_window:
                    self.toplevel_sub_window.focus()
                    return
                self.open_bad_product_entry(bad_treeview)
                return

            # assign the functions to their respective buttons
            log_product.configure(command=add_products)
            bad_product.configure(command=add_bad_products)

            upload_btn = ctk.CTkButton(customer_window, text="Select files", width=40)
            upload_btn.grid(row=9, column=0, padx=5, pady=10)
            file_listbox = tk.Listbox(customer_window, cnf={'bg': '#EBEBEB'}, selectmode=tk.MULTIPLE, width=85,
                                      height=6,
                                      font=("Arial", 14))
            file_listbox.grid(row=9, column=1, padx=5, pady=10)

            def select_action():
                """allows user to select multiple files"""
                nonlocal files  # Accessing files from the outer scope
                new_file_paths = tk.filedialog.askopenfilenames()
                self.toplevel_window.focus()
                count = 1
                for file_path in new_file_paths:
                    if file_path in file_listbox.get(0, tk.END):
                        message = f"File '{file_path}' already added!"
                        func.notify_user(message)
                        self.toplevel_window.focus()
                        raise ValueError(message)
                    file_listbox.insert(tk.END, file_path)
                    # Get the base name of the file
                    base_name = os.path.basename(file_path)
                    # Include file object and base name in the files list
                    files.append((f'file_{count}', (open(file_path, 'rb'), base_name)))
                    count += 1

            upload_btn.configure(command=select_action)

            customer_entry = ctk.CTkComboBox(customer_window, values=list(customer_list.keys()), width=250)
            waybill_entry = ctk.CTkEntry(customer_window, width=250)
            address_entry = ctk.CTkEntry(customer_window, width=250)
            condition_entry = ctk.CTkComboBox(customer_window, values=["good", "bad"], width=250)

            # create text_variable for transport company
            tv1 = tk.StringVar()
            tv1.set(item.haulier)
            t_company_entry = ctk.CTkEntry(customer_window, width=250, textvariable=tv1)
            t_company_entry.configure(state='disabled')

            # create text_variable for driver name
            tv2 = tk.StringVar()
            tv2.set(item.driver_name)
            driver_entry = ctk.CTkEntry(customer_window, width=250, textvariable=tv2)
            driver_entry.configure(state='disabled')

            customer_entry.set('Select')  # Set default value
            condition_entry.set('Select')  # Set default value

            customer_entry.grid(row=0, column=1, padx=5, pady=10)
            waybill_entry.grid(row=1, column=1, padx=5, pady=10)
            address_entry.grid(row=2, column=1, padx=5, pady=10)
            condition_entry.grid(row=3, column=1, padx=5, pady=10)
            t_company_entry.grid(row=4, column=1, padx=5, pady=10)
            driver_entry.grid(row=5, column=1, padx=5, pady=10)

            submit_btn = ctk.CTkButton(customer_window, text="Save")
            submit_btn.grid(row=10, column=1, padx=5, pady=10)

            def save_waybill_info():
                """
                Fetches waybill information from entry fields, creates a dictionary,
                and sends it to an API route to save it to a database.
                """
                # check if a customer was selected
                if customer_entry.get() is None or customer_entry.get() == 'Select':
                    func.notify_user('You did not select customer.')
                    self.toplevel_window.focus()
                    return

                submit_btn.configure(text="Processing...")

                customer_id = customer_list[customer_entry.get()]
                waybill_number = waybill_entry.get()
                address = address_entry.get()
                product_condition = condition_entry.get()
                haulier = t_company_entry.get()
                driver = driver_entry.get()
                if 'products' in self.saved_values:
                    products = self.saved_values['products']
                else:
                    products = []
                if 'bad_products' in self.saved_values:
                    bad_products = self.saved_values['bad_products']
                else:
                    bad_products = []

                waybill_data = {
                    'customer_id': customer_id,
                    'waybill_number': waybill_number,
                    'address': address,
                    'product_condition': product_condition,
                    'haulier': haulier,
                    'haulier_id': item.haulier_id,
                    'driver': driver,
                    'products': products,
                    'bad_products': bad_products,
                    'weight_log_id': item.id
                }

                # process the files
                files_dict = dict(files)

                messenger = Messenger(self.server_url, '/create_waybill?action=save_data')
                resp = messenger.query_server(data=waybill_data)
                if resp['status'] == 300:
                    self.update_status("{}. Will attempt to update waybill data...".format(resp['message']))
                    messenger = Messenger(self.server_url, '/create_waybill?action=edit_data')
                    resp = messenger.query_server(data=waybill_data)

                if resp['status'] == 1:
                    self.update_status(resp['message'])
                    if len(files) > 0:
                        messenger = Messenger(self.server_url,
                                              '/create_waybill?action=save_file&waybill_id={}&vehicle_id={}' \
                                              .format(resp['data']['waybill_id'], resp['data']['vehicle_id']))
                        response = messenger.query_server(files=files_dict)
                        self.update_status(response['message'])
                else:
                    self.update_status(resp['message'])

                submit_btn.configure(text="Finished!")
                customer_window.destroy()
                self.toplevel_window = None
                self.bad_counter = 0
                self.counter = 0
                return

            def cancel_window():
                """
                Closes the haulier information window without saving any data.
                """
                self.toplevel_window = None
                self.bad_counter = 0
                self.counter = 0
                customer_window.destroy()

            def thread_request():
                """Starts a thread that processes form and data and sends it to the database for storage"""
                # Start a thread to handle the database operation
                thread = threading.Thread(target=save_waybill_info)
                thread.daemon = True  # Daemonize the thread to avoid issues on application exit
                thread.start()

            submit_btn.configure(command=thread_request)
            cancel_btn = ctk.CTkButton(customer_window, text="Cancel", command=cancel_window)
            cancel_btn.grid(row=10, column=0, padx=5, pady=10)

            customer_window.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.toplevel_window = customer_window

        else:
            self.toplevel_window.focus()

    def product_treeview(self, window):
        """creates and returns treeview object"""
        # Create Treeview widget with scrollbar
        tree_frame = ttk.Frame(window)

        tree = ttk.Treeview(tree_frame,
                            columns=('s/n', 'description', 'code', 'count', 'weight', 'accepted qty', 'remarks'),
                            show='headings')

        # Define headings
        tree.heading('s/n', text='S/N', anchor='w')
        tree.heading('description', text='Description', anchor='w')
        tree.heading('code', text='Code', anchor='w')
        tree.heading('count', text='Count', anchor='w')
        tree.heading('weight', text='Weight', anchor='w')
        tree.heading('accepted qty', text='Accepted Qty', anchor='w')
        tree.heading('remarks', text='Remarks', anchor='w')

        # Set column widths
        tree.column('s/n', width=50)
        tree.column('description', width=150)
        tree.column('code', width=100)
        tree.column('count', width=80)
        tree.column('weight', width=80)
        tree.column('accepted qty', width=100)
        tree.column('remarks', width=150)

        # Create vertical scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Set maximum height to accommodate 4 rows
        tree_height = min(4, len(tree.get_children()))
        tree_height_in_pixels = tree_height * tree.winfo_reqheight()
        tree.config(height=tree_height)

        # Pack the Treeview widget
        tree.pack(side='left', fill='both', expand=True)

        return tree_frame, tree

    def bad_product_treeview(self, window):
        """creates and returns treeview object"""
        # Create Treeview widget with scrollbar
        tree_frame = ttk.Frame(window)

        tree = ttk.Treeview(tree_frame,
                            columns=('s/n', 'description', 'damaged quantity', 'shortage', 'batch number'),
                            show='headings')

        # Define headings
        tree.heading('s/n', text='S/N', anchor='w')
        tree.heading('description', text='Description', anchor='w')
        tree.heading('damaged quantity', text='Damaged Quantity', anchor='w')
        tree.heading('shortage', text='Shortage', anchor='w')
        tree.heading('batch number', text='Batch Number', anchor='w')

        # Set column widths
        tree.column('s/n', width=50)
        tree.column('description', width=250)
        tree.column('damaged quantity', width=170)
        tree.column('shortage', width=110)
        tree.column('batch number', width=130)

        # Create vertical scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Set maximum height to accommodate 4 rows
        tree_height = min(4, len(tree.get_children()))
        tree_height_in_pixels = tree_height * tree.winfo_reqheight()
        tree.config(height=tree_height)

        # Pack the Treeview widget
        tree.pack(side='left', fill='both', expand=True)

        return tree_frame, tree

    def open_product_entry(self, object_to_modify):
        """
        Opens a custom top-level window for logging waybill products information.
        """

        def populate_listbox(product_data):
            """
            Adds a product to the table.

            Args:
            - product_data (dict): A dictionary containing product information.
              Keys: 's/n', 'description', 'code', 'count', 'weight', 'accepted qty', 'remarks'
            """
            object_to_modify.insert('', 'end', values=(
                product_data['counter'],
                product_data['description'],
                product_data['code'],
                product_data['count'],
                product_data['weight'],
                product_data['quantity'],
                product_data['remarks']
            ))

        self.saved_values['products'] = []
        if self.toplevel_sub_window is None:

            customer_window = ctk.CTkToplevel(self)
            customer_window.geometry("{}x{}".format(500, 350))
            customer_window.title("Waybill Product Information")

            ctk.CTkLabel(customer_window, text="Product Description:").grid(row=0, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Product Code:").grid(row=1, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Number of Packages (Bags/Boxes):").grid(row=2, column=0, padx=5,
                                                                                        pady=10)
            ctk.CTkLabel(customer_window, text="Quantity (MT/NOs):").grid(row=3, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Accepted Quantity:").grid(row=4, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Remarks:").grid(row=5, column=0, padx=5, pady=10)

            description_entry = ctk.CTkEntry(customer_window, width=250)
            code_entry = ctk.CTkEntry(customer_window, width=250)
            count_entry = ctk.CTkEntry(customer_window, width=250)
            weight_entry = ctk.CTkEntry(customer_window, width=250)
            quantity_entry = ctk.CTkEntry(customer_window, width=250)
            remarks_entry = ctk.CTkEntry(customer_window, width=250)

            description_entry.grid(row=0, column=1, padx=5, pady=10)
            code_entry.grid(row=1, column=1, padx=5, pady=10)
            count_entry.grid(row=2, column=1, padx=5, pady=10)
            weight_entry.grid(row=3, column=1, padx=5, pady=10)
            quantity_entry.grid(row=4, column=1, padx=5, pady=10)
            remarks_entry.grid(row=5, column=1, padx=5, pady=10)

            submit_btn = ctk.CTkButton(customer_window, text="Add Product")
            submit_btn.grid(row=6, column=1, padx=5, pady=10)

            def save_product_info():
                """
                Fetches product information from entry fields, creates a dictionary,
                and returns the dictionary.
                """
                description = description_entry.get()
                code = code_entry.get()
                count = count_entry.get()
                weight = weight_entry.get()
                quantity = quantity_entry.get()
                remarks = remarks_entry.get()
                self.counter += 1

                product_data = {
                    'counter': self.counter,
                    'description': description,
                    'code': code,
                    'count': count,
                    'weight': weight,
                    'quantity': quantity,
                    'remarks': remarks
                }

                populate_listbox(product_data)
                self.saved_values['products'].append(product_data)
                customer_window.destroy()
                self.update_status('Product added to waybill')
                self.toplevel_sub_window = None
                return

            def cancel_window():
                """
                Closes the haulier information window without saving any data.
                """
                self.toplevel_sub_window = None
                customer_window.destroy()

            submit_btn.configure(command=save_product_info)
            cancel_btn = ctk.CTkButton(customer_window, text="Cancel", command=cancel_window)
            cancel_btn.grid(row=6, column=0, padx=5, pady=10)

            customer_window.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.toplevel_sub_window = customer_window
            return customer_window
        else:
            self.toplevel_sub_window.focus()

    def open_bad_product_entry(self, object_to_modify):
        """
        Opens a custom top-level window for logging bad product information.
        """

        def populate_listbox(product_data):
            """
            Adds a product to the table.

            Args:
            - product_data (dict): A dictionary containing product information.
              Keys: 's/n', 'description', 'code', 'count', 'weight', 'accepted qty', 'remarks'
            """
            object_to_modify.insert('', 'end', values=(
                product_data['counter'],
                product_data['description'],
                product_data['damage'],
                product_data['shortage'],
                product_data['batch_number']
            ))

        self.saved_values['bad_products'] = []
        if self.toplevel_sub_window is None:

            customer_window = ctk.CTkToplevel(self)
            customer_window.geometry("{}x{}".format(420, 250))
            customer_window.title("Bad Product Entry")

            ctk.CTkLabel(customer_window, text="Product Description:").grid(row=0, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Damaged Quantity:").grid(row=1, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Shortage:").grid(row=2, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Batch Number:").grid(row=3, column=0, padx=5, pady=10)

            description_entry = ctk.CTkEntry(customer_window, width=250)
            damage_entry = ctk.CTkEntry(customer_window, width=250)
            shortage_entry = ctk.CTkEntry(customer_window, width=250)
            batch_number_entry = ctk.CTkEntry(customer_window, width=250)

            description_entry.grid(row=0, column=1, padx=5, pady=10)
            damage_entry.grid(row=1, column=1, padx=5, pady=10)
            shortage_entry.grid(row=2, column=1, padx=5, pady=10)
            batch_number_entry.grid(row=3, column=1, padx=5, pady=10)

            submit_btn = ctk.CTkButton(customer_window, text="Add Bad Product")
            submit_btn.grid(row=4, column=1, padx=5, pady=10)

            def save_product_info():
                """
                Fetches product information from entry fields, creates a dictionary,
                and returns the dictionary.
                """
                description = description_entry.get()
                damage = damage_entry.get()
                shortage = shortage_entry.get()
                batch_number = batch_number_entry.get()
                self.bad_counter += 1

                bad_product_data = {
                    'counter': self.bad_counter,
                    'description': description,
                    'damage': damage,
                    'shortage': shortage,
                    'batch_number': batch_number
                }

                populate_listbox(bad_product_data)
                self.saved_values['bad_products'].append(bad_product_data)
                customer_window.destroy()
                self.update_status('Bad product added to waybill')
                self.toplevel_sub_window = None
                return

            def cancel_window():
                """
                Closes the haulier information window without saving any data.
                """
                self.toplevel_sub_window = None
                self.saved_values['bad_products'] = None
                customer_window.destroy()

            submit_btn.configure(command=save_product_info)
            cancel_btn = ctk.CTkButton(customer_window, text="Cancel", command=cancel_window)
            cancel_btn.grid(row=4, column=0, padx=5, pady=10)

            customer_window.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.toplevel_sub_window = customer_window
            return customer_window
        else:
            self.toplevel_sub_window.focus()

    def send_approval_request(self, item):
        """
        Generates a dialogue box for user to select the appropriate approval,
        sends approval request to selected approval.
        """
        # process item data
        approver_list = {}
        if len(item.users) == 0:
            self.update_status('No user record found.')
            return
        approvals = [x for x in item.users if x['admin_type'] == 'approver']
        if len(approvals) == 0:
            self.update_status('No approvals found.')
            return

        for x in approvals:
            approver_list[x['full_name']] = x['user_id']

        if self.toplevel_sub_window is None:

            customer_window = ctk.CTkToplevel(self)
            customer_window.geometry("{}x{}".format(320, 200))
            customer_window.title("Select Waybill Approval")

            ctk.CTkLabel(customer_window, text="Who Should Approve This?:").grid(row=0, column=0, padx=5, pady=10)
            approver_entry = ctk.CTkComboBox(customer_window, values=list(approver_list.keys()), width=250)
            approver_entry.grid(row=1, column=0, padx=25, pady=10)
            approver_entry.set('Select approval')

            submit_btn = ctk.CTkButton(customer_window, text="send request", width=80)
            submit_btn.grid(row=2, column=0, padx=5, pady=10)

            def send_request():
                """
                Extracts approval information from users list and sends approval request to them
                """
                approver_info = [x for x in approvals if x['full_name'] == approver_entry.get()][0]  # dict data
                customer_window.destroy()

                request_email = approver_info['email']
                email_body, attachment_files = self.prepare_template_data(item, request_email)
                subject = 'Waybill Approval Request'
                sender = 'belovedsamex@yahoo.com'  # 'zinando2000@gmail.com'
                messenger = SendMail(sender, request_email, subject)

                messenger.send_email_with_application(email_body, attachment_files)
                # messenger.elastic_email_by_smtp(email_body, attachment_files)

                self.update_status('Email sent successfully.')
                self.toplevel_sub_window = None
                return

            def cancel_window():
                """
                Closes the haulier information window without saving any data.
                """
                self.toplevel_sub_window = None
                customer_window.destroy()

            def thread_request():
                """Starts a thread that processes form and data and sends it to the database for storage"""
                # Start a thread to handle the database operation
                thread = threading.Thread(target=send_request)
                thread.daemon = True  # Daemonize the thread to avoid issues on application exit
                thread.start()

            submit_btn.configure(command=thread_request)
            cancel_btn = ctk.CTkButton(customer_window, text="Cancel", command=cancel_window, width=80)
            cancel_btn.grid(row=3, column=0, padx=5, pady=25)

            customer_window.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.toplevel_sub_window = customer_window
            return customer_window
        else:
            self.toplevel_sub_window.focus()

    def on_closing(self):
        """function to execute when dialogue box is about to close"""
        self.status_message = None
        self.toplevel_window.destroy()
        self.toplevel_window = None
        self.toplevel_sub_window = None

    def generate_email_template(self, table1_data, table2_data, table3_data, table4_data, email, weight_log_id):
        # HTML template with placeholders for table data
        email_template = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Waybill Information</title>
        </head>
        <body>
            <!-- Logo -->
            <img src="https://i.imgur.com/iP3xtXj.png" alt="Company Logo" class="img-fluid" style="max-width: 100%;">
                
            <p>You have been requested to review the following information and to append your approval of the waybill
            by clicking any of the links shared below.</p>
            <p> Please <b>note</b> that you will need your Pikanto app credentials to be able to append your approval.</p>
            
            <!-- Table 1 -->
            <h2>WEIGHBRIDGE SLIP</h2>
            <table>                
                {table1_data}
            </table>

            <!-- Table 2 -->
            <hr style="height: 3px; color: blue">
            <h2>WAYBILL DATA</h2>
            <table >                
                {table2_data}
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
                    {table3_data}
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
                    {table4_data}
                </tbody>
            </table>
            <p>Use any of these links to access the approval page:</p>
            <p><b>From Mobile Device:  <b> <a href="https://roughy-topical-easily.ngrok-free.app/approve?email={email}&wtlog_id={weight_log_id}"> click here</a></p>
            <p><b>From PC:  <b> <a href="http://localhost:8088/approve?email={email}&wtlog_id={weight_log_id}"> click here</a></p>
        </body>
        </html>        
        '''

        return email_template

    def prepare_template_data(self, itemm, email):
        """formats data for the email template"""
        # fetch data needed
        my_query = Messenger(self.server_url, '/fetch_resources/email_data')
        response = my_query.query_server({'weight_log_id': itemm.id})
        if response['status'] != 1:
            func.notify_user('No records found!')
            return
        ticket_data = response['ticket_data']  # dict
        waybill_data = response['waybill_data']  # dict
        products = response['products']  # list
        bad_products = response['bad_products']  # list
        files = response['files']  # list

        # format table1-data: weighbridge slip
        ticket_list = [x.title() for x in ticket_data.keys()]
        html = ''
        for item in ticket_list:
            html += '<tr>'
            html += f'<th>{item}</ht>'
            html += f"<td>{ticket_data.get(item.lower())}</td>"
            html += '</tr>'
        table1_data = html

        # format table2-data: waybill data
        waybill_list = [x.title() for x in waybill_data.keys()]
        html = ''
        for item in waybill_list:
            html += '<tr>'
            html += f'<th>{item}</th>'
            html += f"<td>{waybill_data.get(item.lower())}</td>"
            html += '</tr>'
        table2_data = html

        # format table3-data: product data
        html = ''
        if len(products) > 0:
            for item in products:
                html += '<tr>'
                html += f"<td>{item['description']}</td>"
                html += f"<td>{item['code']}</td>"
                html += f"<td>{item['count']}</td>"
                html += f"<td>{item['weight']}</td>"
                html += f"<td>{item['quantity']}</td>"
                html += f"<td>{item['remarks']}</td>"
                html += '</tr>'
        table3_data = html

        # format table4-data: product data
        html = ''
        if len(bad_products) > 0:
            for item in bad_products:
                html += '<tr>'
                html += f"<td>{item['description']}</td>"
                html += f"<td>{item['damage']}</td>"
                html += f"<td>{item['shortage']}</td>"
                html += f"<td>{item['batch_number']}</td>"
                html += '</tr>'
        table4_data = html

        template = self.generate_email_template(table1_data, table2_data, table3_data, table4_data, email, itemm.id)

        # prepare a text_based email body instead

        body = "You have been requested to review and approve a waybill information, "
        body += "please click any of the links below to visit the waybill information page.\n\n"

        body += "NOTE: You will be required to provide your Pikanto app user credentials in order to be able to "
        body += "append your approval.\n\n"
        body += f"From mobile device, use this link: https://roughy-topical-easily.ngrok-free.app/approve?email={email}&wtlog_id={itemm.id}\n\n"
        body += f"From PC use:  http://localhost:8088/approve?email={email}&wtlog_id={itemm.id}"

        return body, files

    def generate_printable_view(self, widget, w, h, x, y):
        if widget:
            # Capture the content as an image
            image = ImageGrab.grab(bbox=(x, y, x + w, y + h))

            # Save the captured image temporarily
            temp_image_path = os.path.join(tempfile.gettempdir(), 'printable_view.png')
            image.save(temp_image_path)

            # Open the saved image using the default system image viewer
            try:
                if platform.system() == 'Darwin':  # For macOS
                    subprocess.run(['open', temp_image_path])
                elif platform.system() == 'Windows':  # For Windows
                    os.startfile(temp_image_path)
                else:  # For Linux
                    subprocess.run(['xdg-open', temp_image_path])
            except FileNotFoundError:
                func.notify_user("Could not open image with the default viewer. Check your system commands.")

            # delete the temp file when the image viewer has been closed by user
            def delete_temp_file():
                try:
                    while True:
                        # Check if the image viewer process has terminated
                        if platform.system() == 'Windows':
                            subprocess.run(['tasklist', '|', 'findstr', 'Microsoft.Photos.exe'], shell=True,
                                           stdout=subprocess.DEVNULL)
                        else:
                            subprocess.run(['pgrep', '-f', temp_image_path], stdout=subprocess.DEVNULL)
                        time.sleep(1)
                except KeyboardInterrupt:  # Handle manual interruption (Ctrl+C)
                    pass
                finally:
                    # Delete the temporary file
                    try:
                        os.remove(temp_image_path)
                    except Exception as e:
                        func.notify_user(f"Error deleting temporary file: {e}")

            self.thread_request(delete_temp_file)

    def fetch_details_data(self, itemm):
        # check if there is internet connection
        if not func.is_internet_connected():
            self.check_internet_connection()
            return None, None, None, None, None, None

        ticket_data, waybill_data, products, bad_products, files, approvals_data = None, None, None, None, None, None

        # fetch data needed
        my_query = Messenger(self.server_url, '/fetch_resources/email_data')
        response = my_query.query_server({'weight_log_id': itemm.id})
        if response['status'] == 1:
            ticket = response['ticket_data']
            ticket_data = {}
            ticket_data["date"] = ticket['date']
            ticket_data["vehicle_id"] = ticket['vehicle id']
            ticket_data["customer_name"] = ticket['customer']
            ticket_data["haulier"] = ticket['haulier']
            ticket_data["destination"] = ticket['destination']
            ticket_data["product"] = ticket['product']
            ticket_data["ticket_number"] = ticket['ticket number']
            ticket_data["delivery_number"] = ticket['delivery number']
            ticket_data["order_number"] = ticket['order number']
            ticket_data["final_weight"] = ticket['gross mass']
            ticket_data["initial_weight"] = ticket['tare mass']
            ticket_data["net_weight"] = ticket['net mass']
            ticket_data["driver"] = ticket['driver']

            if 'waybill number' in response['waybill_data']:
                waybill = response['waybill_data']
                waybill_data = {}
                waybill_data["waybill_number"] = waybill['waybill number']
                waybill_data["date"] = waybill['date']
                waybill_data["location"] = waybill['location']
                waybill_data["company_ref"] = waybill['ugee ref number']
                waybill_data["customer_ref"] = waybill['customer ref number']
                waybill_data["customer_name"] = waybill['customer name']
                waybill_data["address"] = waybill['delivery address']
                waybill_data["vehicle_id"] = waybill['vehicle id']
                waybill_data["transporter"] = waybill['transporter']

                if len(response['products']) > 0:
                    products = []
                    for pro in response['products']:
                        mr = {}
                        mr["product_description"] = pro['description']
                        mr["item_code"] = pro['code']
                        mr["packages"] = pro['count']
                        mr["quantity"] = pro['weight']
                        mr["accepted"] = pro['quantity']
                        mr["remarks"] = pro['remarks']
                        products.append(mr)

                if len(response['bad_products']) > 0:
                    bad_products = []
                    for pro in response['bad_products']:
                        mr = {}
                        mr["product_description"] = pro['description']
                        mr["damaged_quantity"] = pro['damage']
                        mr["shortage_quantity"] = pro['shortage']
                        mr["batch_number"] = pro['batch_number']
                        bad_products.append(mr)

                if len(response['files']) > 0:
                    files = response['files']

                approvals_data = response['approvals_data']
        else:
            func.notify_user('No records found!')

        return ticket_data, waybill_data, products, bad_products, files, approvals_data

    def approve_waybill(self, weight_log_id):
        """approves the waybill"""
        # check if there is internet connection
        if not func.is_internet_connected():
            self.check_internet_connection()
            return

        my_query = Messenger(self.server_url, '/create_waybill?action=approve_waybill')
        mr = {}
        mr['weight_log_id'] = weight_log_id
        mr['approver'] = 'Ndubumma Samuel'
        # add other user data

        response = my_query.query_server(mr)
        func.notify_user(response['message'])
        self.update_status(response['message'])
        return
