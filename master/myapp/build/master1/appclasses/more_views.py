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
from docx2pdf import convert
from functools import partial
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
        self.saved_values = {}
        self.counter = 0
        self.bad_counter = 0
        self.tabview = None

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

    def view_ticket_details(self, data):
        if self.toplevel_window is None:
            # fetch the required data
            ticket, waybill, products, bad_products, files, approvals_data = self.fetch_details_data(data)
            if ticket is None:
                return

            ticket_data = ticket

            # Create the main window to fill the screen
            top = ctk.CTkToplevel(self)
            self.toplevel_window = top
            top_height = 600
            top_width = 1100
            top.title("Ticket For Logistics Operation")

            # Get screen width and height
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()

            # Calculate x and y coordinates for the window to be centered
            dx = (screen_width / 2) - (top_width / 2)
            dy = (screen_height / 2) - (top_height / 2)

            # Set window dimensions and position
            top.geometry('%dx%d+%d+%d' % (top_width, top_height, dx, dy))

            # Create submain_frame_1 to hold ticket_frame
            h = top_height - 200
            submain_frame_1 = ctk.CTkFrame(top, width=top_width, height=h)
            submain_frame_1.pack(fill=tk.BOTH, expand=True)

            # Create the ticket frame inside submain_frame_1
            self.create_ticket_detail(submain_frame_1, ticket_data)

            # Create the action buttons frame
            action_buttons_frame = ctk.CTkFrame(top, height=100, width=top_width)
            action_buttons_frame.pack(fill=tk.BOTH, expand=True)

            # Create the print button for the ticket frame
            ticket_print_button = ctk.CTkButton(action_buttons_frame, text="Print Ticket", height=25, width=50,
                                                bg_color="#DBDBDB", fg_color="grey", text_color="#ffffff")
            ticket_print_button.pack(side=tk.LEFT, padx=5, pady=5)

            # Create edit button
            edit_button = ctk.CTkButton(action_buttons_frame, text="Edit Ticket", height=25, width=50,
                                        bg_color="#DBDBDB", fg_color="grey", text_color="#ffffff")
            edit_button.pack(side=tk.LEFT, padx=5, pady=5)
            edit_button.configure(command=lambda: self.thread_request(self.edit_ticket, ticket_data['id'], edit_button))

            def print_tickets():
                top.update()
                width = submain_frame_1.winfo_width() - 25
                height = submain_frame_1.winfo_height()
                x = top.winfo_x() + 15
                y = top.winfo_y() + 50
                self.generate_printable_view(submain_frame_1, width, height, x, y)

            ticket_print_button.configure(command=lambda: self.print_ticket(ticket_data))

            top.protocol("WM_DELETE_WINDOW", self.on_closing)

        else:
            self.toplevel_window.focus()

    def print_ticket(self, data: dict):
        """updates the ticket template information and gets it ready for printing"""

        # create a dictionary of the variables to update template with and update template
        replacements = {'[date]': f'{data["date"]}',
                        '[product]': f"{data['product']}",
                        '[vehicle reg]': f'{data["vehicle_id"]}',
                        '[client]': f'{data["customer_name"]}',
                        '[hauler]': f'{data["haulier"]}',
                        '[destination]': f'{data["destination"]}',
                        '[gross mass]': f'{data["final_weight"]}',
                        '[tare mass]': f'{data["initial_weight"]}',
                        '[net mass]': f'{data["net_weight"]}',
                        '[driver]': f'{data["driver"]}',
                        '[ticket number]': f'{data["id"]}',
                        '[delivery number]': f'{data["delivery_number"]}',
                        '[order number]': f'{data["order_number"]}'}

        ticket_temp_file = 'ticket_temp.docx'
        output_path = 'output.docx'
        pdf_file = 'output.pdf'

        func.update_template(replacements, ticket_temp_file, output_path)

        # convert updated template (doc file) into pdf
        convert(output_path, pdf_file)

        # delete the doc file
        os.remove(output_path)

        # open the pdf in a default web browser
        webbrowser.open(pdf_file)

        return

    def print_waybill(self, ticket, waybill, products, bad_products, approvals):
        """updates the waybill template information and gets it ready for printing"""
        # create a dictionary of the variables to update template with and update template
        replacements = {'[date]': '',
                        '[waybill number]': '',
                        '[location]': '',
                        '[company id]': '',
                        '[c ref]': '',
                        '[customer]': '',
                        '[delivery address]': '',
                        '[vehicle number]': '',
                        '[transporter]': '',
                        '[package total]': '',
                        '[qty total]': '',
                        '[gross mass]': '',
                        '[damage]': '',
                        '[shortage]': '',
                        'products': [],
                        '[driver]': '',
                        '[batch]': '',
                        '[whse tech]': '',
                        '[receive date]': '',
                        '[delivery date]': f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
                        '[status]': '',
                        '[approver]': '',
                        '[approval date]': ''}

        if ticket:
            replacements['[gross mass]'] = f'{ticket["final_weight"]}'
        if waybill:
            replacements['[date]'] = f'{waybill["date"]}'
            replacements['[waybill number]'] = f"{waybill['waybill_number']}"
            replacements['[location]'] = f"{waybill['location']}"
            replacements['[company id]'] = f"{waybill['company_ref']}"
            replacements['[c ref]'] = f"{waybill['customer_ref']}"
            replacements['[customer]'] = f"{waybill['customer_name']}"
            replacements['[delivery address]'] = f"{waybill['address']}"
            replacements['[vehicle number]'] = f'{waybill["vehicle_id"]}'
            replacements['[transporter]'] = f'{waybill["transporter"]}'
        if products:
            print(products)
            replacements['[package total]'] = f'{sum([int(x["packages"]) for x in products])}'
            replacements['[qty total]'] = f'{sum([int(x["quantity"]) for x in products])}'
            replacements['products'] = products
        if bad_products:
            bad_products = bad_products[0]
            replacements['[damage]'] = f'{bad_products["damaged_quantity"]}'
            replacements['[shortage]'] = f'{bad_products["shortage_quantity"]}'
            replacements['[batch]'] = f'{bad_products["batch_number"]}'
        if approvals:
            replacements['[driver]'] = f'{approvals["delivered_by"]}'
            replacements['[whse tech]'] = f'{approvals["received_by"]}'
            replacements['[receive date]'] = f"{approvals['received_date']}"
            replacements['[delivery date]'] = f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
            replacements['[status]'] = f"{approvals['approval_status'].upper()}"
            replacements['[approver]'] = f"{approvals['approver']}"
            replacements['[approval date]'] = f"{approvals['approval_date']}"

        waybill_temp_file = 'waybill_temp.docx'
        output_path = 'output.docx'
        pdf_file = 'output.pdf'

        func.update_template(replacements, waybill_temp_file, output_path)

        # convert updated template (doc file) into pdf
        convert(output_path, pdf_file)

        # delete the doc file
        os.remove(output_path)

        # open the pdf in a default web browser
        webbrowser.open(pdf_file)

        return

    def view_waybill_detail(self, data):
        if self.toplevel_window is None:
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

            products_data = products if products else []

            bad_products_info = bad_products if bad_products else []

            # Create the main window to fill the screen
            screen_width, screen_height = 800, 700
            top = DialogueBox(screen_width, screen_height, fg_color="#e3e7f0")

            # create a title for the waybill
            x = 0
            y = 0
            waybill_title_label = MyLabel(top, text="WAYBILL", font_size=18, font_weight="bold", x=x, y=y,
                                          font="TkDefaultFont", text_color="blue",
                                          fg_color="#ffffff", width=screen_width, height=25).create_obj()
            waybill_title_label.place(x=x, y=y)

            # create a frame to hold waybill content including products
            y = y + 10 + int(waybill_title_label.cget('height'))
            content_frame = ctk.CTkFrame(master=top, width=screen_width)
            content_frame.position_y = y
            content_frame.position_x = x
            content_frame.place(x=x, y=y)

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

            content_frame_height = y + int(transporter_value_label.cget('height'))

            # create products title label
            y = y + 20 + int(transporter_value_label.cget("height"))
            x = 5
            w = screen_width - 10
            products_title_label = MyLabel(content_frame, text="Products", font_size=18, font_weight="bold", x=x, y=y,
                                           font="TkDefaultFont", text_color="grey",
                                           fg_color="#ffffff", width=w, height=25).create_obj()
            products_title_label.place(x=x, y=y)
            content_frame_height += 20 + int(products_title_label.cget('height'))

            # create products label
            y = y + int(products_title_label.cget("height")) + 20
            x = 0
            w = screen_width
            h = (35 + (len(products_data) * 30))  # fixed height of headers plus 30 per line of product
            products_label = MyLabel(content_frame, text="", x=x, y=y,
                                     fg_color="#ffffff", width=w, height=h).create_obj()
            products_label.place(x=x, y=y)

            # create products detail
            self.create_product_detail(products_label, products_data)

            content_frame_height += int(products_label.cget('height')) + 20

            # create bad products title label
            y = y + 20 + int(products_label.cget("height"))
            x = 5
            w = screen_width - 10
            bad_products_title_label = MyLabel(content_frame, text="Bad Products", font_size=18,
                                               font_weight="bold", x=x, y=y, font="TkDefaultFont", text_color="grey",
                                               fg_color="#ffffff", width=w, height=25).create_obj()
            bad_products_title_label.place(x=x, y=y)

            content_frame_height += 20 + int(bad_products_title_label.cget('height'))

            # create bad products label
            y = y + int(bad_products_title_label.cget("height")) + 20
            x = 0
            w = screen_width
            # h = h - int(bad_products_title_label.cget("height"))
            h = (35 + (len(bad_products_info) * 30))
            bad_products_label = MyLabel(content_frame, text="", x=x, y=y,
                                         fg_color="#ffffff", width=w, height=h).create_obj()
            bad_products_label.place(x=x, y=y)

            # create bad products detail
            self.create_bad_product_detail(bad_products_label, bad_products_info)

            content_frame_height += int(bad_products_label.cget('height')) + 20

            # configure content frame height: company_info height, product title, product label, bad product title,
            # bad product label
            content_frame.configure(height=content_frame_height)

            # create another frame for the approvals
            w = screen_width
            h = 90  # based on values used to create approvals infor
            y = content_frame.position_y + int(content_frame.cget('height')) + 20
            x = content_frame.position_x
            approvals_frame = ctk.CTkFrame(master=top, width=w, height=h)
            approvals_frame.place(x=x, y=y)

            self.create_waybill_approvals(approvals_frame, approvals_data)

            # Create the action buttons frame for waybill inside submain_frame_2
            y = y + int(approvals_frame.cget("height")) + 10
            waybill_action_buttons_frame = ctk.CTkFrame(master=top, width=w, height=40, bg_color="#E3E7F0",
                                                        fg_color="#E3E7F0")
            waybill_action_buttons_frame.place(x=x, y=y)

            # Create the print button for the waybill frame
            waybill_print_button = ctk.CTkButton(waybill_action_buttons_frame, text="Print Waybill", height=25,
                                                 width=70, bg_color="#E3E7F0", fg_color="grey",
                                                 text_color="#ffffff")
            waybill_print_button.grid(row=0, column=0, padx=10, pady=5)

            # Create button for approval of the waybill
            waybill_approval_button = ctk.CTkButton(waybill_action_buttons_frame, text="Approve Waybill", height=25,
                                                    width=70, bg_color="#E3E7F0", fg_color="grey",
                                                    text_color="#ffffff")
            waybill_approval_button.grid(row=0, column=1, padx=10, pady=5)

            if data.approval_status == "approved" or not data.waybill_ready or not data.final_weight:
                waybill_approval_button.configure(state='disabled')

            # Create button for waybill data replacement
            replace_button = ctk.CTkButton(waybill_action_buttons_frame, text="Replace Waybill", height=25,
                                           width=70, bg_color="#E3E7F0", fg_color="grey",
                                           text_color="#ffffff")
            replace_button.grid(row=0, column=2, padx=10, pady=5)
            replace_button.configure(command=lambda: self.thread_request(self.edit_waybill, data, waybill))

            def thread_request():
                thread = threading.Thread(target=self.approve_waybill, args=[data.id])
                thread.daemon = True  # Daemonize the thread to avoid issues on application exit
                thread.start()

            waybill_approval_button.configure(command=thread_request)

            def print_waybill():
                exclude = int(waybill_action_buttons_frame.cget("height")) + 20  # exclude action buttons part
                x = top.winfo_rootx()
                y = top.winfo_rooty()
                width = top.winfo_width()
                height = top.winfo_height() - exclude
                print(f"x: {x}, y: {y}, w: {width}, h: {height}")
                self.generate_printable_view(top, width, height, x, y)

            waybill_print_button.configure(command=lambda: self.print_waybill(ticket, waybill, products, bad_products, approvals_data))

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
        # calc window width and use it to create content label width
        win_width = int(window.cget('width'))
        win_height = int(window.cget('height'))

        # Create a title label for "Weighbridge Slip"
        x, y = 0, 0
        w = win_width
        h = 25
        ticket_title_label = MyLabel(window, text="WEIGHBRIDGE SLIP", font_size=18, font_weight="bold", x=x, y=y,
                                     font="TkDefaultFont", text_color="blue", bg_color="#f0f0f0",
                                     fg_color="#ffffff", width=w, height=h).create_obj()
        ticket_title_label.place(x=x, y=y)

        # create a frame to display the ticket information
        h = win_height - y - h - 10  # dist btw title and frame (10)
        y = y + int(ticket_title_label.cget('height')) + 10
        ticket_content_frame = ctk.CTkFrame(window, bg_color="#ffffff", fg_color="#ffffff",
                                            width=w, height=h)
        ticket_content_frame.place(x=x, y=y)

        # create labels for each content data
        content_width = (int(ticket_content_frame.cget('width')) - 160) // 4
        content_height = h // 10

        # row 1
        x, y = 40, 0
        w = content_width
        h = content_height
        date_label = MyLabel(ticket_content_frame, text="Date:", width=w, anchor="w", height=h,
                             font="TkDefaultFont", font_size=16, font_weight="bold", x=x, y=y).create_obj()
        date_label.place(x=x, y=y)

        x = x + 20 + int(date_label.cget('width'))
        date_value_label = MyLabel(ticket_content_frame, text=ticket_data['date'], width=w, anchor="w", height=h,
                                   font_size=16, x=x, y=y).create_obj()
        date_value_label.place(x=x, y=y)

        # row 2
        y = y + int(date_value_label.cget("height"))
        x = 40
        vehicle_label = MyLabel(ticket_content_frame, text="Vehicle Reg:", width=w, anchor="w", height=h,
                                font="TkDefaultFont", font_size=16, font_weight="bold", x=x, y=y
                                ).create_obj()
        vehicle_label.place(x=x, y=y)

        x = x + 20 + int(vehicle_label.cget('width'))
        vehicle_value_label = MyLabel(ticket_content_frame, text=ticket_data['vehicle_id'],
                                      width=w, height=h, anchor="w", font_size=16, x=x, y=y
                                      ).create_obj()
        vehicle_value_label.place(x=x, y=y)

        x = x + 40 + int(vehicle_value_label.cget('width'))
        delivery_number_label = MyLabel(ticket_content_frame, text="Delivery Number:", width=w, anchor="w",
                                        font="TkDefaultFont", font_size=16, font_weight="bold",
                                        x=x, height=h, y=y).create_obj()
        delivery_number_label.place(x=x, y=y)

        x = x + 20 + int(delivery_number_label.cget('width'))
        delivery_number_value_label = MyLabel(ticket_content_frame, text=ticket_data['delivery_number'],
                                              width=w, anchor="w", x=x, y=y, height=h, font_size=16).create_obj()
        delivery_number_value_label.place(x=x, y=y)

        # row 3
        y = y + int(delivery_number_value_label.cget('height'))
        x = 40
        customer_label = MyLabel(ticket_content_frame, text="Customer:", width=w, anchor="w",
                                 font="TkDefaultFont", font_size=16, font_weight="bold",
                                 x=x, height=h, y=y).create_obj()
        customer_label.place(x=x, y=y)

        x = x + 20 + int(customer_label.cget('width'))
        customer_value_label = MyLabel(ticket_content_frame, text=ticket_data['customer_name'],
                                       width=w, anchor="w", x=x, y=y, height=h, font_size=16).create_obj()
        customer_value_label.place(x=x, y=y)

        x = x + 40 + int(customer_value_label.cget('width'))
        order_number_label = MyLabel(ticket_content_frame, text="Order Number:", width=w, anchor="w",
                                     font="TkDefaultFont", font_size=16, font_weight="bold",
                                     x=x, height=h, y=y).create_obj()
        order_number_label.place(x=x, y=y)

        x = x + 20 + int(order_number_label.cget('width'))
        order_number_value_label = MyLabel(ticket_content_frame, text=ticket_data['order_number'],
                                           width=w, anchor="w", x=x, y=y, height=h, font_size=16).create_obj()
        order_number_value_label.place(x=x, y=y)

        # row 4
        y = y + int(order_number_value_label.cget('height'))
        x = 40
        haulier_label = MyLabel(ticket_content_frame, text="Haulier:", width=w, anchor="w",
                                font="TkDefaultFont", font_size=16, font_weight="bold",
                                x=x, height=h, y=y).create_obj()
        haulier_label.place(x=x, y=y)

        x = x + 20 + int(haulier_label.cget('width'))
        haulier_value_label = MyLabel(ticket_content_frame, text=ticket_data['haulier'],
                                      width=w, anchor="w", x=x, y=y, height=h, font_size=16).create_obj()
        haulier_value_label.place(x=x, y=y)

        x = x + 40 + int(haulier_value_label.cget('width'))
        destination_label = MyLabel(ticket_content_frame, text="Destination:", width=w, anchor="w",
                                    font="TkDefaultFont", font_size=16, font_weight="bold",
                                    x=x, height=h, y=y).create_obj()
        destination_label.place(x=x, y=y)

        x = x + 20 + int(destination_label.cget('width'))
        destination_value_label = MyLabel(ticket_content_frame, text=ticket_data['destination'],
                                          width=w, anchor="w", x=x, y=y, height=h, font_size=16).create_obj()
        destination_value_label.place(x=x, y=y)

        # row 5
        y = y + int(destination_value_label.cget('height'))
        x = 40
        product_label = MyLabel(ticket_content_frame, text="Product:", width=w, anchor="w",
                                font="TkDefaultFont", font_size=16, font_weight="bold",
                                x=x, height=h, y=y).create_obj()
        product_label.place(x=x, y=y)

        x = x + 20 + int(product_label.cget('width'))
        product_value_label = MyLabel(ticket_content_frame, text=ticket_data['product'],
                                      width=w, anchor="w", x=x, y=y, height=h, font_size=16).create_obj()
        product_value_label.place(x=x, y=y)

        x = x + 40 + int(product_value_label.cget('width'))
        ticket_number_label = MyLabel(ticket_content_frame, text="Ticket Number:", width=w, anchor="w",
                                      font="TkDefaultFont", font_size=16, font_weight="bold", x=x, y=y,
                                      height=h).create_obj()
        ticket_number_label.place(x=x, y=y)

        x = x + 20 + int(ticket_number_label.cget('width'))
        ticket_number_value_label = MyLabel(ticket_content_frame, text=ticket_data['ticket_number'], height=h,
                                            width=w, anchor="w", x=x, y=y, font_size=16).create_obj()
        ticket_number_value_label.place(x=x, y=y)

        # row 6
        y = y + int(ticket_number_value_label.cget('height'))
        x = 40
        first_weight_label = MyLabel(ticket_content_frame, text="Gross Mass:", width=w, anchor="w",
                                     font="TkDefaultFont", font_size=16, font_weight="bold",
                                     x=x, height=h, y=y).create_obj()
        first_weight_label.place(x=x, y=y)

        x = x + 20 + int(first_weight_label.cget('width'))
        first_weight_value_label = MyLabel(ticket_content_frame, text=ticket_data['final_weight'],
                                           width=w, anchor="w", x=x, y=y, height=h, font_size=16).create_obj()
        first_weight_value_label.place(x=x, y=y)

        # row 7
        y = y + int(first_weight_value_label.cget('height'))
        x = 40
        second_weight_label = MyLabel(ticket_content_frame, text="Tare Mass:", width=w, anchor="w",
                                      font="TkDefaultFont", font_size=16, font_weight="bold",
                                      x=x, height=h, y=y).create_obj()
        second_weight_label.place(x=x, y=y)

        x = x + 20 + int(second_weight_label.cget('width'))
        second_weight_value_label = MyLabel(ticket_content_frame, text=ticket_data['initial_weight'],
                                            width=w, anchor="w", x=x, y=y, height=h, font_size=16).create_obj()
        second_weight_value_label.place(x=x, y=y)

        # row 8
        y = y + int(second_weight_value_label.cget('height'))
        x = 40
        net_weight_label = MyLabel(ticket_content_frame, text="Net Mass:", width=w, anchor="w",
                                   font="TkDefaultFont", font_size=16, font_weight="bold",
                                   x=x, height=h, y=y).create_obj()
        net_weight_label.place(x=x, y=y)

        x = x + 20 + int(net_weight_label.cget('width'))
        net_weight_value_label = MyLabel(ticket_content_frame, text=ticket_data['net_weight'],
                                         width=w, anchor="w", x=x, y=y, height=h, font_size=16).create_obj()
        net_weight_value_label.place(x=x, y=y)

        # row 9
        y = y + int(net_weight_value_label.cget('height'))
        x = 40
        driver_label = MyLabel(ticket_content_frame, text="Driver Name:", width=w, anchor="w",
                               font="TkDefaultFont", font_size=16, font_weight="bold",
                               x=x, height=h, y=y).create_obj()
        driver_label.place(x=x, y=y)

        x = x + 20 + int(driver_label.cget('width'))
        driver_value_label = MyLabel(ticket_content_frame, text=ticket_data['driver'],
                                     width=w, anchor="w", x=x, y=y, height=h, font_size=16).create_obj()
        driver_value_label.place(x=x, y=y)

        x = x + 40 + int(driver_value_label.cget('width'))
        signature_label = MyLabel(ticket_content_frame, text="Driver Signature:", width=w, anchor="w",
                                  font="TkDefaultFont", font_size=16, font_weight="bold",
                                  x=x, height=h, y=y).create_obj()
        signature_label.place(x=x, y=y)

        x = x + 20 + int(signature_label.cget('width'))
        signature_value_label = MyLabel(ticket_content_frame, text="...............................",
                                        width=w, anchor="w", x=x, y=y, height=h, font_size=16).create_obj()
        signature_value_label.place(x=x, y=y)

        return  # ticket_frame

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

        h = 25
        w = (int(widget.cget('width')) - 10) // 3
        x, y = 0, 0
        received_by_label = MyLabel(widget, text="Received By", font_size=14,
                                    font_weight="bold", x=x, y=y, font="TkDefaultFont", text_color="grey",
                                    fg_color="#f0f0f0", width=w, height=h).create_obj()
        received_by_label.place(x=x, y=y)

        x = x + int(received_by_label.cget('width')) + 5
        delivered_by_label = MyLabel(widget, text="Delivered By", font_size=14,
                                     font_weight="bold", x=x, y=y, font="TkDefaultFont", text_color="grey",
                                     fg_color="#f0f0f0", width=w, height=h).create_obj()
        delivered_by_label.place(x=x, y=y)

        x = x + int(delivered_by_label.cget('width')) + 5
        authorized_by_label = MyLabel(widget, text="Authorized By", font_size=14,
                                      font_weight="bold", x=x, y=y, font="TkDefaultFont", text_color="grey",
                                      fg_color="#f0f0f0", width=w, height=h).create_obj()
        authorized_by_label.place(x=x, y=y)

        # insert values under the headers
        h = 20
        x = 5
        y = y + int(delivered_by_label.cget('height')) + 2
        for key in range(3):
            text = ""
            if key == 2:
                text += f"NAME:   {data['approver']}\n\n" if data['approval_status'] == "approved" else f"NAME:\n\n"
                text += f"SIGNATURE:   Approved.\n" if data['approval_status'] == "approved" else f"SIGNATURE:\n"
                text += f"DATE:   {data['approval_date']}" if data['approval_status'] == "approved" else f"DATE:"
            elif key == 1:
                text += f"NAME:   {data['delivered_by']}\n\n"
                text += f"SIGNATURE:   .................................\n"
                text += f"DATE:   {datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')}" if data[
                                                                                            'delivered_by'] != "" else f"DATE:\n\n"
            elif key == 0:
                text += f"NAME:   {data['received_by']}\n\n"
                text += f"SIGNATURE:   received by me.\n" if data['received_by'] != "" else f"SIGNATURE:\n"
                text += f"DATE:   {data['received_date']}"

            item_label = MyLabel(widget, text=text, x=x, y=y, text_color="#000000",
                                 fg_color="#ffffff", width=w - 5, height=h, justify="left").create_obj()
            item_label.place(x=x, y=y)
            x = x + int(item_label.cget('width')) + 5
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
        h = 25
        if len(product_info) > 0:
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
        h = 25
        if len(bad_product_info) > 0:
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

    def open_customer_entry(self, customer_data=None):
        """
        Opens a custom top-level window for logging customer information.
        """
        if self.toplevel_window is None:

            customer_window = ctk.CTkToplevel(self)
            width = 480
            height = 230
            position_x = (self.winfo_screenwidth() // 2) - (width // 2)
            position_y = (self.winfo_screenheight() // 2) - (height // 2)
            customer_window.geometry("{}x{}+{}+{}".format(width, height, position_x, position_y))
            # customer_window.geometry("{}x{}".format(480, 230))
            customer_window.title("Customer Information")

            ctk.CTkLabel(customer_window, text="Customer Name:").grid(row=0, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Customer Address:").grid(row=1, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Registration (Ref) Number:").grid(row=2, column=0, padx=5, pady=10)

            name_entry = ctk.CTkEntry(customer_window, width=250)
            address_entry = ctk.CTkEntry(customer_window, width=250)
            reg_entry = ctk.CTkEntry(customer_window, width=250)
            if customer_data:
                name_entry.insert(0, customer_data.customer_name)
                address_entry.insert(0, customer_data.customer_address)
                reg_entry.insert(0, customer_data.customer_ref)

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
                submit_btn.configure(text="Processing...", state='disabled')
                customer_name = name_entry.get()
                customer_address = address_entry.get()
                customer_reg_number = reg_entry.get()

                if not customer_name or not customer_reg_number:
                    submit_btn.configure(text='Save')
                    func.notify_user('Customer name or reg number cannot be empty.')
                    self.toplevel_window.focus()
                    return

                customer_info = {
                    'name': customer_name,
                    'address': customer_address,
                    'ref': customer_reg_number
                }
                url = '/customer?action=save_data'
                if customer_data:
                    customer_info['id'] = customer_data.customer_id
                    url = '/customer?action=edit_customer_data'

                messenger = Messenger(self.server_url, url)
                resp = messenger.query_server(data=customer_info)
                submit_btn.configure(text="Finished!")
                self.update_status(resp['message'])
                if resp['status'] == 1 and 'customers' in self.fetched_resource:
                    self.fetched_resource['customers'] = resp['data']
                    customer_window.destroy()
                    self.toplevel_window = None
                else:
                    submit_btn.configure(text="Save", state='enabled')
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

    def open_haulier_entry(self, haulier_data=None):
        """
        Opens a custom top-level window for logging transport company information.
        """
        if self.toplevel_window is None:

            customer_window = ctk.CTkToplevel(self)
            width = 480
            height = 230
            position_x = (self.winfo_screenwidth() // 2) - (width // 2)
            position_y = (self.winfo_screenheight() // 2) - (height // 2)
            customer_window.geometry("{}x{}+{}+{}".format(width, height, position_x, position_y))
            # customer_window.geometry("{}x{}".format(480, 230))
            customer_window.title("Transport Company Information")

            ctk.CTkLabel(customer_window, text="Haulier Name:").grid(row=0, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Address:").grid(row=1, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Registration (Ref) Number:").grid(row=2, column=0, padx=5, pady=10)

            name_entry = ctk.CTkEntry(customer_window, width=250)
            address_entry = ctk.CTkEntry(customer_window, width=250)
            reg_entry = ctk.CTkEntry(customer_window, width=250)
            if haulier_data:
                name_entry.insert(0, haulier_data.haulier_name)
                address_entry.insert(0, haulier_data.haulier_address)
                reg_entry.insert(0, haulier_data.haulier_ref)

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
                submit_btn.configure(text="Processing...", state='disabled')
                haulier_name = name_entry.get()
                haulier_address = address_entry.get()
                haulier_reg_number = reg_entry.get()
                if not haulier_name or not haulier_reg_number:
                    submit_btn.configure(text='Save')
                    func.notify_user('Haulier name or reg number cannot be empty.')
                    self.toplevel_window.focus()
                    return

                haulier_info = {
                    'name': haulier_name,
                    'address': haulier_address,
                    'ref': haulier_reg_number
                }
                url = '/haulier?action=save_data'
                if haulier_data:
                    haulier_info['id'] = haulier_data.haulier_id
                    url = '/haulier?action=edit_haulier_data'

                messenger = Messenger(self.server_url, url)
                resp = messenger.query_server(data=haulier_info)
                submit_btn.configure(text="Finished!")
                self.update_status(resp['message'])
                if resp['status'] == 1 and 'hauliers' in self.fetched_resource:
                    self.fetched_resource['hauliers'] = resp['data']
                    customer_window.destroy()
                    self.toplevel_window = None
                else:
                    submit_btn.configure(text="Save", state='enabled')

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

    def open_user_entry(self, user_data=None):
        """
        Opens a custom top-level window for logging user information.
        """
        if self.toplevel_window is None:

            customer_window = ctk.CTkToplevel(self)
            width = 420
            height = 350
            position_x = (self.winfo_screenwidth() // 2) - (width // 2)
            position_y = (self.winfo_screenheight() // 2) - (height // 2)
            customer_window.geometry("{}x{}+{}+{}".format(width, height, position_x, position_y))
            # customer_window.geometry("{}x{}".format(420, 350))
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
            admin_type_entry = ctk.CTkComboBox(customer_window, values=["user", "admin", "approver", "super"],
                                               width=250)
            password_entry = ctk.CTkEntry(customer_window, width=250)
            confirm_password_entry = ctk.CTkEntry(customer_window, width=250)
            admin_type_entry.set('Select')  # Set default value
            if user_data:
                first_name_entry.insert(0, user_data.first_name)
                last_name_entry.insert(0, user_data.last_name)
                email_entry.insert(0, user_data.email)
                admin_type_entry.set(user_data.admin_type)

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
                submit_btn.configure(text="Processing...", state='disabled')

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

                # validate password only if user_data is None
                if not user_data:
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

                user_info = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'admin_type': admin_type,
                    'password': password
                }
                url = '/user?action=save_data'
                if user_data:
                    user_info['id'] = user_data.user_id
                    url = '/user?action=edit_user_data'

                messenger = Messenger(self.server_url, url)
                resp = messenger.query_server(data=user_info)
                self.update_status(resp['message'])
                submit_btn.configure(text="Finished!")
                if resp['status'] == 1 and 'users' in self.fetched_resource:
                    self.fetched_resource['users'] = resp['data']
                    customer_window.destroy()
                    self.toplevel_window = None
                else:
                    submit_btn.configure(text="Save", state="enabled")

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
                    'weight_log_id': item.id,
                    'received_by': self.current_user.full_name
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

                    submit_btn.configure(text="Finished!")
                    customer_window.destroy()
                    self.saved_values = {}
                    self.toplevel_window = None
                    self.bad_counter = 0
                    self.counter = 0
                else:
                    self.update_status(resp['message'])

                return

            def cancel_window():
                """
                Closes the haulier information window without saving any data.
                """
                self.toplevel_window = None
                self.saved_values = {}
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
            # initialize saved_values attr
            if 'products' not in self.saved_values:
                self.saved_values['products'] = []

            object_to_modify.insert('', 'end', values=(
                product_data['counter'],
                product_data['description'],
                product_data['code'],
                product_data['count'],
                product_data['weight'],
                product_data['quantity'],
                product_data['remarks']
            ))

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
            # initialize saved values
            if 'bad_products' not in self.saved_values:
                self.saved_values['bad_products'] = []

            object_to_modify.insert('', 'end', values=(
                product_data['counter'],
                product_data['description'],
                product_data['damage'],
                product_data['shortage'],
                product_data['batch_number']
            ))

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
        # check if user is admin
        if self.current_user.admin_type != "admin" and self.current_user.admin_type != "super":
            func.notify_user("You are not authorized to perform this action")
            return

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
                sender = self.waybill_tech_email
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

            def delete_temp_file_after_conversion():
                # convert the temp image into pdf
                func.image_to_pdf_with_pyfpdf_open(temp_image_path)

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

            self.thread_request(delete_temp_file_after_conversion)

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
            ticket_data['id'] = ticket['id']
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
                waybill_data['id'] = waybill['id']
                waybill_data["waybill_number"] = waybill['waybill number']
                waybill_data["date"] = waybill['date']
                waybill_data["location"] = waybill['location']
                waybill_data["company_ref"] = waybill['ugee ref number']
                waybill_data["customer_ref"] = waybill['customer ref number']
                waybill_data["customer_name"] = waybill['customer name']
                waybill_data["address"] = waybill['delivery address']
                waybill_data["vehicle_id"] = waybill['vehicle id']
                waybill_data["transporter"] = waybill['transporter']

                if response['products']:
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

                if response['bad_products']:
                    if len(response['bad_products']) > 0:
                        bad_products = []
                        for pro in response['bad_products']:
                            mr = {}
                            mr["product_description"] = pro['description']
                            mr["damaged_quantity"] = pro['damage']
                            mr["shortage_quantity"] = pro['shortage']
                            mr["batch_number"] = pro['batch_number']
                            bad_products.append(mr)

                if response['files']:
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
        # check if user is authorized approver
        if self.current_user.admin_type != "approver":
            func.notify_user('You are not authorized to perform this action.')
            return

        my_query = Messenger(self.server_url, '/create_waybill?action=approve_waybill')
        mr = {}
        mr['weight_log_id'] = weight_log_id
        mr['approver'] = self.current_user.full_name
        # add other user data

        response = my_query.query_server(mr)
        func.notify_user(response['message'])
        self.update_status(response['message'])
        return

    def create_manager_view(self):
        """creates a tabview for managing app resources"""
        # import your data from database here
        if 'users' not in self.fetched_resource:
            self.fetch_resources()

        if self.tabview:
            self.tabview.destroy()

        # create a frame inside the main display area
        tabview_frame = ctk.CTkFrame(master=self.display_label, fg_color="#2f6c60")
        tabview_frame.place(x=0, y=0)
        self.tabview = tabview_frame

        # create tabview inside the frame
        width = int(self.display_label.cget('width'))
        height = int(self.display_label.cget('height'))
        exit_btn_frame_height = 35

        w = width
        h = height - exit_btn_frame_height
        tabview = ctk.CTkTabview(master=tabview_frame, width=w, height=h, fg_color="#e3e7f0",
                                 segmented_button_fg_color="#25564C", segmented_button_unselected_color="#e3e7f0",
                                 text_color="#000000", segmented_button_selected_color="#25564C")
        tabview.pack(padx=0, pady=0)

        tab_1 = tabview.add("Manage Users")  # add tab at the end
        tab_2 = tabview.add("Manage Customers")  # add tab at the end
        tab_3 = tabview.add("Manage Haulier")  # add tab at the end
        tab_4 = tabview.add("Find Record")  # add tab at the end

        tabview.set("Manage Users")  # set currently visible tab

        # create content wrapper for all the tabs
        h = h - 70
        w = w - 50
        tab_1_wrapper = ctk.CTkLabel(tab_1, text='', fg_color="#ffffff", height=h, width=w)
        tab_1_wrapper.pack()
        tab_2_wrapper = ctk.CTkLabel(tab_2, text='', fg_color="#ffffff", height=h, width=w)
        tab_2_wrapper.pack()
        tab_3_wrapper = ctk.CTkLabel(tab_3, text='', fg_color="#ffffff", height=h, width=w)
        tab_3_wrapper.pack()
        tab_4_wrapper = ctk.CTkLabel(tab_4, text='', fg_color="#ffffff", height=h, width=w)
        tab_4_wrapper.pack()

        self.manage_users(tab_1_wrapper, self.fetched_resource['users'])
        self.manage_customers(tab_2_wrapper, self.fetched_resource['customers'])
        self.manage_hauliers(tab_3_wrapper, self.fetched_resource['hauliers'])

        # create a textfield inside the tab_3_wrapper
        w = (int(tab_4_wrapper.cget('width')) // 3) * 2
        x = (int(tab_4_wrapper.cget('width')) - w) // 2
        h = 30
        y = int(tab_4_wrapper.cget('height')) // 3
        search_field = ctk.CTkEntry(tab_4_wrapper, width=w, height=h, text_color="#000000", border_width=2,
                                    border_color="grey", bg_color="#ffffff", corner_radius=25,
                                    fg_color="#ffffff", placeholder_text="enter vehicle ID")
        search_field.place(x=x, y=y)
        x = x + (w // 2) - 50
        w = 100
        y = y + h + 20
        search_btn = MyButton(tab_4_wrapper, text="Search", font_size=12, text_color="#000000", border_color="grey",
                              bg_color="#ffffff", fg_color="#e3e7f0", height=h, width=w, x=x, y=y
                              ).create_obj()
        search_btn.place(x=x, y=y)
        search_btn.configure(command=lambda: self.search_records(search_field.get(), search_btn))

        # button to exit the tab view from screen
        # first create a label to place the button on
        def exit_command():
            """exits the tabview from the display area"""
            tabview_frame.destroy()
            self.tabview = None
            return

        btn_wrapper = ctk.CTkLabel(tabview_frame, text='', width=width, height=exit_btn_frame_height,
                                   bg_color='#2f6c60', fg_color='#2f6c60')
        btn_wrapper.pack()

        x = width - 100
        y = 5
        w = 9 * 4
        h = 25
        exit_btn = MyButton(btn_wrapper, text="Exit", font_size=12, text_color="#000000",
                            bg_color="#25564C", fg_color="#e3b448", height=h, width=w, x=x, y=y,
                            command=exit_command).create_obj()
        exit_btn.place(x=x, y=y)

        return

    def manage_users(self, window, data):
        """creates a view for managing user data"""
        if data:
            items_per_page = 10
            grouper = SubGroupCreator(data)
            grouper.create_sub_groups(items_per_page)
            total_groups = grouper.total_groups()

            def display_items(group_number):
                """function creates a widget that displays certain number of data on the main display"""
                items_to_display = grouper.get_group(group_number)

                # create a wrapper where all the items are going to be displayed
                width = int(window.cget('width'))
                height = int(window.cget('height'))
                btn_wrapper_height = 30

                h = height - btn_wrapper_height
                w = width
                x, y = 0, 0
                item_wrapper = ctk.CTkLabel(window, text='', fg_color="#ffffff", height=h, width=w)
                item_wrapper.place(x=x, y=y)

                # create buttons to navigate different pages of the records
                w = width
                y = y + int(item_wrapper.cget('height'))
                btn_wrapper = ctk.CTkLabel(window, text="", fg_color="#e3e7f0", height=btn_wrapper_height,
                                           width=w)
                btn_wrapper.place(x=x, y=y)

                h = 20
                w = 40
                x = (btn_wrapper.cget('width') // 2) - 50
                y = 5
                prev_btn = ctk.CTkButton(btn_wrapper, text="<< Prev", text_color="#000000",
                                         bg_color="#e3e7f0", fg_color="#e3e7f0", height=h, width=w,
                                         border_width=2, border_color="grey")
                if group_number == 1:
                    prev_btn.configure(state='disabled')
                prev_btn.place(x=x, y=y)

                x = (btn_wrapper.cget('width') // 2) + 10
                next_btn = ctk.CTkButton(btn_wrapper, text="Next >>", text_color="#000000",
                                         bg_color="#e3e7f0", fg_color="#e3e7f0", height=h, width=w,
                                         border_width=2, border_color="grey")
                if group_number == total_groups:
                    next_btn.configure(state='disabled')
                next_btn.place(x=x, y=y)

                # functions to handle prev and next button clicks
                def on_prev_click():
                    # destroy current view
                    item_wrapper.destroy()
                    display_items(group_number - 1)

                def on_next_click():
                    # destroy current view
                    item_wrapper.destroy()
                    display_items(group_number + 1)

                prev_btn.configure(command=on_prev_click)
                next_btn.configure(command=on_next_click)

                # create content title
                w = int(item_wrapper.cget('width')) - 40
                h = 25
                x, y = 20, 0
                title = ctk.CTkLabel(item_wrapper, text='USERS', fg_color="#e3e7f0", height=h, width=w,
                                     text_color="#000000")
                title.place(x=x, y=y)
                title.cget('font').configure(size=18, weight='bold')

                skipper = h = (item_wrapper.cget('height') - 75) // items_per_page
                y = y + 5 + int(title.cget('height'))
                count = 1

                for item in items_to_display:
                    item = DotDict(item)

                    # contents
                    # serial number
                    w = 30
                    x = 10
                    col_0 = ctk.CTkLabel(item_wrapper, text=f'{item.count}.', fg_color="#f0f0f0", height=h, width=w,
                                         text_color="#000000", anchor="w", padx=5, pady=5, corner_radius=8)
                    col_0.place(x=x, y=y)

                    # name
                    w = 9 * 22
                    x = x + int(col_0.cget('width')) + 10
                    col_1 = ctk.CTkLabel(item_wrapper, text=item.full_name, fg_color="#f0f0f0", height=h, width=w,
                                         text_color="#000000", anchor="w", padx=5, pady=5, corner_radius=8)
                    col_1.place(x=x, y=y)

                    # email
                    w = 9 * 20
                    x = x + int(col_1.cget('width')) + 10
                    col_2 = ctk.CTkLabel(item_wrapper, text=item.email.split('@')[0], fg_color="#f0f0f0", height=h,
                                         width=w,
                                         text_color="#000000", anchor="w", padx=5, pady=5, corner_radius=8)
                    col_2.place(x=x, y=y)

                    # admin type
                    w = 9 * 8
                    x = x + int(col_2.cget('width')) + 10
                    col_3 = ctk.CTkLabel(item_wrapper, text=item.admin_type, fg_color="#f0f0f0", height=h,
                                         width=w,
                                         text_color="#000000", anchor="w", padx=5, pady=5, corner_radius=8)
                    col_3.place(x=x, y=y)

                    # edit button
                    w = 9 * 6
                    x = x + int(col_3.cget('width')) + 10
                    edit_btn = ctk.CTkButton(item_wrapper, text="Edit", text_color="#000000",
                                             bg_color="#ffffff", fg_color="#e3e7f0", height=h, width=w)
                    edit_btn.place(x=x, y=y)
                    edit_btn.configure(command=partial(self.open_user_entry, item))

                    x = x + int(edit_btn.cget('width')) + 10
                    delete_btn = ctk.CTkButton(item_wrapper, text="Delete", text_color="#000000",
                                               bg_color="#ffffff", fg_color="#e3e7f0", height=h, width=w)
                    delete_btn.place(x=x, y=y)
                    delete_btn.configure(command=partial(self.delete_resource, item.user_id, 'user',
                                                         delete_btn))

                    y += int(col_1.cget('height')) + 5
                    count += 1

            display_items(1)

    def manage_customers(self, window, data):
        """creates a view for managing user data"""
        if data:
            items_per_page = 10
            grouper = SubGroupCreator(data)
            grouper.create_sub_groups(items_per_page)
            total_groups = grouper.total_groups()

            def display_items(group_number):
                """function creates a widget that displays certain number of data on the main display"""
                items_to_display = grouper.get_group(group_number)

                # create a wrapper where all the items are going to be displayed
                width = int(window.cget('width'))
                height = int(window.cget('height'))
                btn_wrapper_height = 30

                h = height - btn_wrapper_height
                w = width
                x, y = 0, 0
                item_wrapper = ctk.CTkLabel(window, text='', fg_color="#ffffff", height=h, width=w)
                item_wrapper.place(x=x, y=y)

                # create buttons to navigate different pages of the records
                w = width
                y = y + int(item_wrapper.cget('height'))
                btn_wrapper = ctk.CTkLabel(window, text="", fg_color="#e3e7f0", height=btn_wrapper_height,
                                           width=w)
                btn_wrapper.place(x=x, y=y)

                h = 20
                w = 40
                x = (btn_wrapper.cget('width') // 2) - 50
                y = 5
                prev_btn = ctk.CTkButton(btn_wrapper, text="<< Prev", text_color="#000000",
                                         bg_color="#e3e7f0", fg_color="#e3e7f0", height=h, width=w,
                                         border_width=2, border_color="grey")
                if group_number == 1:
                    prev_btn.configure(state='disabled')
                prev_btn.place(x=x, y=y)

                x = (btn_wrapper.cget('width') // 2) + 10
                next_btn = ctk.CTkButton(btn_wrapper, text="Next >>", text_color="#000000",
                                         bg_color="#e3e7f0", fg_color="#e3e7f0", height=h, width=w,
                                         border_width=2, border_color="grey")
                if group_number == total_groups:
                    next_btn.configure(state='disabled')
                next_btn.place(x=x, y=y)

                # functions to handle prev and next button clicks
                def on_prev_click():
                    # destroy current view
                    item_wrapper.destroy()
                    display_items(group_number - 1)

                def on_next_click():
                    # destroy current view
                    item_wrapper.destroy()
                    display_items(group_number + 1)

                prev_btn.configure(command=on_prev_click)
                next_btn.configure(command=on_next_click)

                # create content title
                w = int(item_wrapper.cget('width')) - 40
                h = 25
                x, y = 20, 0
                title = ctk.CTkLabel(item_wrapper, text='CUSTOMERS', fg_color="#e3e7f0", height=h, width=w,
                                     text_color="#000000")
                title.place(x=x, y=y)
                title.cget('font').configure(size=18, weight='bold')

                skipper = h = (item_wrapper.cget('height') - 75) // items_per_page
                y = y + 5 + int(title.cget('height'))
                count = 1

                for item in items_to_display:
                    item = DotDict(item)

                    # contents
                    # serial number
                    w = 30
                    x = 10
                    col_0 = ctk.CTkLabel(item_wrapper, text=f'{item.count}.', fg_color="#f0f0f0", height=h, width=w,
                                         text_color="#000000", anchor="w", padx=5, pady=5, corner_radius=8)
                    col_0.place(x=x, y=y)

                    # name
                    w = 9 * 22
                    x = x + int(col_0.cget('width')) + 10
                    col_1 = ctk.CTkLabel(item_wrapper, text=item.customer_name, fg_color="#f0f0f0", height=h, width=w,
                                         text_color="#000000", anchor="w", padx=5, pady=5, corner_radius=8)
                    col_1.place(x=x, y=y)

                    # adress
                    w = 9 * 15
                    x = x + int(col_1.cget('width')) + 10
                    col_2 = ctk.CTkLabel(item_wrapper, text=item.customer_address[:15], fg_color="#f0f0f0", height=h,
                                         width=w,
                                         text_color="#000000", anchor="w", padx=5, pady=5, corner_radius=8)
                    col_2.place(x=x, y=y)

                    # ref number
                    w = 9 * 15
                    x = x + int(col_2.cget('width')) + 10
                    col_3 = ctk.CTkLabel(item_wrapper, text=item.customer_ref, fg_color="#f0f0f0", height=h,
                                         width=w,
                                         text_color="#000000", anchor="w", padx=5, pady=5, corner_radius=8)
                    col_3.place(x=x, y=y)

                    # edit button
                    w = 9 * 6
                    x = x + int(col_3.cget('width')) + 10
                    edit_btn = ctk.CTkButton(item_wrapper, text="Edit", text_color="#000000",
                                             bg_color="#ffffff", fg_color="#e3e7f0", height=h, width=w)
                    edit_btn.place(x=x, y=y)
                    edit_btn.configure(command=partial(self.open_customer_entry, item))

                    x = x + int(edit_btn.cget('width')) + 10
                    delete_btn = ctk.CTkButton(item_wrapper, text="Delete", text_color="#000000",
                                               bg_color="#ffffff", fg_color="#e3e7f0", height=h, width=w)
                    delete_btn.place(x=x, y=y)
                    delete_btn.configure(command=partial(self.delete_resource, item.customer_id, 'customer',
                                                         delete_btn))

                    y += int(col_1.cget('height')) + 5
                    count += 1

            display_items(1)

    def manage_hauliers(self, window, data):
        """creates a view for managing user data"""
        if data:
            items_per_page = 10
            grouper = SubGroupCreator(data)
            grouper.create_sub_groups(items_per_page)
            total_groups = grouper.total_groups()

            def display_items(group_number):
                """function creates a widget that displays certain number of data on the main display"""
                items_to_display = grouper.get_group(group_number)

                # create a wrapper where all the items are going to be displayed
                width = int(window.cget('width'))
                height = int(window.cget('height'))
                btn_wrapper_height = 30

                h = height - btn_wrapper_height
                w = width
                x, y = 0, 0
                item_wrapper = ctk.CTkLabel(window, text='', fg_color="#ffffff", height=h, width=w)
                item_wrapper.place(x=x, y=y)

                # create buttons to navigate different pages of the records
                w = width
                y = y + int(item_wrapper.cget('height'))
                btn_wrapper = ctk.CTkLabel(window, text="", fg_color="#e3e7f0", height=btn_wrapper_height,
                                           width=w)
                btn_wrapper.place(x=x, y=y)

                h = 20
                w = 40
                x = (btn_wrapper.cget('width') // 2) - 50
                y = 5
                prev_btn = ctk.CTkButton(btn_wrapper, text="<< Prev", text_color="#000000",
                                         bg_color="#e3e7f0", fg_color="#e3e7f0", height=h, width=w,
                                         border_width=2, border_color="grey")
                if group_number == 1:
                    prev_btn.configure(state='disabled')
                prev_btn.place(x=x, y=y)

                x = (btn_wrapper.cget('width') // 2) + 10
                next_btn = ctk.CTkButton(btn_wrapper, text="Next >>", text_color="#000000",
                                         bg_color="#e3e7f0", fg_color="#e3e7f0", height=h, width=w,
                                         border_width=2, border_color="grey")
                if group_number == total_groups:
                    next_btn.configure(state='disabled')
                next_btn.place(x=x, y=y)

                # functions to handle prev and next button clicks
                def on_prev_click():
                    # destroy current view
                    item_wrapper.destroy()
                    display_items(group_number - 1)

                def on_next_click():
                    # destroy current view
                    item_wrapper.destroy()
                    display_items(group_number + 1)

                prev_btn.configure(command=on_prev_click)
                next_btn.configure(command=on_next_click)

                # create content title
                w = int(item_wrapper.cget('width')) - 40
                h = 25
                x, y = 20, 0
                title = ctk.CTkLabel(item_wrapper, text='HAULIERS', fg_color="#e3e7f0", height=h, width=w,
                                     text_color="#000000")
                title.place(x=x, y=y)
                title.cget('font').configure(size=18, weight='bold')

                skipper = h = (item_wrapper.cget('height') - 75) // items_per_page
                y = y + 5 + int(title.cget('height'))
                count = 1

                for item in items_to_display:
                    item = DotDict(item)

                    # contents
                    # serial number
                    w = 30
                    x = 10
                    col_0 = ctk.CTkLabel(item_wrapper, text=f'{item.count}.', fg_color="#f0f0f0", height=h, width=w,
                                         text_color="#000000", anchor="w", padx=5, pady=5, corner_radius=8)
                    col_0.place(x=x, y=y)

                    # name
                    w = 9 * 22
                    x = x + int(col_0.cget('width')) + 10
                    col_1 = ctk.CTkLabel(item_wrapper, text=item.haulier_name, fg_color="#f0f0f0", height=h, width=w,
                                         text_color="#000000", anchor="w", padx=5, pady=5, corner_radius=8)
                    col_1.place(x=x, y=y)

                    # adress
                    w = 9 * 15
                    x = x + int(col_1.cget('width')) + 10
                    col_2 = ctk.CTkLabel(item_wrapper, text=item.haulier_address[:15], fg_color="#f0f0f0", height=h,
                                         width=w,
                                         text_color="#000000", anchor="w", padx=5, pady=5, corner_radius=8)
                    col_2.place(x=x, y=y)

                    # ref number
                    w = 9 * 15
                    x = x + int(col_2.cget('width')) + 10
                    col_3 = ctk.CTkLabel(item_wrapper, text=item.haulier_ref, fg_color="#f0f0f0", height=h,
                                         width=w,
                                         text_color="#000000", anchor="w", padx=5, pady=5, corner_radius=8)
                    col_3.place(x=x, y=y)

                    # edit button
                    w = 9 * 6
                    x = x + int(col_3.cget('width')) + 10
                    edit_btn = ctk.CTkButton(item_wrapper, text="Edit", text_color="#000000",
                                             bg_color="#ffffff", fg_color="#e3e7f0", height=h, width=w)
                    edit_btn.place(x=x, y=y)
                    edit_btn.configure(command=partial(self.open_haulier_entry, item))

                    x = x + int(edit_btn.cget('width')) + 10
                    delete_btn = ctk.CTkButton(item_wrapper, text="Delete", text_color="#000000",
                                               bg_color="#ffffff", fg_color="#e3e7f0", height=h, width=w)
                    delete_btn.place(x=x, y=y)
                    delete_btn.configure(command=partial(self.delete_resource, item.haulier_id, 'haulier',
                                                         delete_btn))

                    y += int(col_1.cget('height')) + 5
                    count += 1

            display_items(1)

    def search_records(self, vehicle_id, obj):
        """searches the database for records of the given vehicle ID"""
        obj.configure(text="wait...", state="disabled")
        if not vehicle_id:
            self.update_status('Provide vehicle id')
            obj.configure(text="Search", state="enabled")
            return

        # search database for records
        def search():
            """sends request to find records for vehicle id"""
            worker = Messenger(self.server_url, "/search/fetch_vehicle_records")
            response = worker.query_server({'vehicle_id': vehicle_id})
            if response['status'] == 1:
                self.view_weight_records(response['data'])
                self.update_status(response['message'])
                obj.configure(text="Search", state="enabled")
            else:
                self.update_status(response['message'])
                obj.configure(text="Search", state="enabled")

            return

        self.thread_request(search)

        return

    def edit_ticket(self, ticket_id, obj):
        """creates and edit window for editing ticket data"""
        obj.configure(text='wait...', state='disabled')
        if self.current_user.admin_type == 'user':
            func.notify_user('You are not allowed to perform this action.')
            self.update_status('Permission denied!')
            obj.configure(text='Edit Ticket', state='enabled')
            return

        if self.toplevel_sub_window is None:
            # fetch data
            worker = Messenger(self.server_url, '/search/existing_weight_record')
            response = worker.query_server({'weight_log_id': ticket_id})
            record = DotDict(response['data'])

            if response['status'] != 1:
                func.notify_user(response['message'])
                self.update_status(response['message'])
                obj.configure(text='Edit Ticket', state='enabled')
                return

            customers, hauliers = response['customers'], response['hauliers']

            # check that customer and haulier list are not empty
            check = lambda var: var is None or (isinstance(var, list) and not var)
            if check(customers):
                self.update_status('No customers record found in the database')
                obj.configure(text='Edit Ticket', state='enabled')
                return
            if check(hauliers):
                self.update_status('No haulier record found in the database')
                obj.configure(text='Edit Ticket', state='enabled')
                return

            customer_list = {}
            for x in customers:
                customer_list[x['customer_name']] = x['customer_id']
            haulier_list = {}
            for y in hauliers:
                haulier_list[y['haulier_name']] = y['haulier_id']

            top = ctk.CTkToplevel(self)
            width = 620
            height = 720
            position_x = (self.winfo_screenwidth() // 2) - (width // 2)
            position_y = (self.winfo_screenheight() // 2) - (height // 2)
            top.geometry("{}x{}+{}+{}".format(width, height, position_x * 2, position_y))

            top.title(f'EDITING DATA FOR {record.vehicle_id}')
            self.toplevel_sub_window = top

            # create a label the size of the main display label
            h = height
            w = width
            x, y = 0, 0
            report_label = MyLabel(top, text="", bg_color="#ffffff", fg_color="#c9c9c9",
                                   height=h, width=w, x=x, y=y).create_obj()
            report_label.place(x=x, y=y)

            #  create header for the form
            h = 100
            x, y = 0, 0
            report_header_label = MyLabel(report_label, text=f'EDITING DATA FOR {record.vehicle_id}',
                                          bg_color="#c9c9c9",
                                          fg_color="#838383", height=h, width=w, x=x, y=y, text_color="#ffffff",
                                          font_size=28, font_weight="bold") \
                .create_obj()
            report_header_label.place(x=x, y=y)

            # create 7 label divisions for the remaining form space
            h = (int(report_label.cget('height')) - int(report_header_label.cget('height'))) // 6
            w = report_label.cget('width')
            x = report_header_label.position_x
            y = report_header_label.position_y + int(report_header_label.cget('height'))

            # division 2
            div2 = MyLabel(report_label, text='', bg_color="#c9c9c9",
                           fg_color="#c9c9c9", height=h, width=w, x=x, y=y).create_obj()
            div2.place(x=x, y=y)

            d_w = (int(div2.cget('width')) - 30) // 2
            d_h = (int(div2.cget('height')) - 20) // 2
            x, y = 10, 5
            vehicle_id_label = MyLabel(div2, text='vehicle ID', bg_color="#c9c9c9", text_color="#ffffff",
                                       fg_color="#8b8b8b", height=d_h, width=d_w, x=x, y=y, font_size=16).create_obj()
            vehicle_id_label.place(x=x, y=y)
            vehicle_id = ctk.CTkEntry(div2, placeholder_text="Enter vehicle id", width=d_w,
                                      height=d_h)
            vehicle_id.insert(0, record.vehicle_id)

            vehicle_id.position_x, vehicle_id.position_y = x, 5 + int(vehicle_id_label.cget('height'))
            vehicle_id.place(x=vehicle_id.position_x, y=vehicle_id.position_y)
            self.selected_value['vehicle_id'] = vehicle_id

            x = x + int(vehicle_id_label.cget('width')) + 10
            vehicle_name_label = MyLabel(div2, text='vehicle Name', bg_color="#c9c9c9", text_color="#ffffff",
                                         fg_color="#8b8b8b", height=d_h, width=d_w, x=x, y=y, font_size=16).create_obj()
            vehicle_name_label.place(x=x, y=y)

            vehicle_name = ctk.CTkEntry(div2, placeholder_text="Enter vehicle name", width=d_w,
                                        height=d_h)
            vehicle_name.insert(0, record.vehicle_name)
            vehicle_name.position_x = vehicle_id.position_x + int(vehicle_id.cget('width')) + 10
            vehicle_name.position_y = vehicle_id.position_y
            vehicle_name.place(x=vehicle_name.position_x, y=vehicle_name.position_y)
            self.selected_value['vehicle_name'] = vehicle_name

            # division 3
            x = div2.position_x
            y = div2.position_y + int(div2.cget('height'))
            div3 = MyLabel(report_label, text='', bg_color="#c9c9c9",
                           fg_color="#c9c9c9", height=h, width=w, x=x, y=y).create_obj()
            div3.place(x=x, y=y)

            d_w = (int(div3.cget('width')) - 30) // 2
            d_h = (int(div3.cget('height')) - 20) // 2
            x, y = 10, 5
            driver_name_label = MyLabel(div3, text='Driver Name', bg_color="#c9c9c9", text_color="#ffffff",
                                        fg_color="#8b8b8b", height=d_h, width=d_w, x=x, y=y, font_size=16).create_obj()
            driver_name_label.place(x=x, y=y)

            driver_name = ctk.CTkEntry(div3, placeholder_text="Enter driver name here", width=d_w,
                                       height=d_h)

            driver_name.insert(0, record.driver_name)
            driver_name.position_x, driver_name.position_y = x, 5 + int(driver_name_label.cget('height'))
            driver_name.place(x=driver_name.position_x, y=driver_name.position_y)
            self.selected_value['driver_name'] = driver_name

            x = x + int(vehicle_id_label.cget('width')) + 10
            driver_phone_label = MyLabel(div3, text='Driver phone number', bg_color="#c9c9c9", text_color="#ffffff",
                                         fg_color="#8b8b8b", height=d_h, width=d_w, x=x, y=y, font_size=16).create_obj()
            driver_phone_label.place(x=x, y=y)
            driver_phone = ctk.CTkEntry(div3, placeholder_text="Enter driver phone number", width=d_w,
                                        height=d_h)
            driver_phone.insert(0, record.driver_phone)
            driver_phone.position_x = driver_name.position_x + int(driver_name.cget('width')) + 10
            driver_phone.position_y = driver_name.position_y
            driver_phone.place(x=driver_phone.position_x, y=driver_phone.position_y)
            self.selected_value['driver_phone'] = driver_phone

            # division 4
            x = div3.position_x
            y = div3.position_y + int(div3.cget('height'))
            div4 = MyLabel(report_label, text='', bg_color="#c9c9c9",
                           fg_color="#c9c9c9", height=h, width=w, x=x, y=y).create_obj()
            div4.place(x=x, y=y)

            d_w = (int(div4.cget('width')) - 30) // 2
            d_h = (int(div4.cget('height')) - 20) // 2
            x, y = 10, 5
            transport_company_label = MyLabel(div4, text='Haulier', bg_color="#c9c9c9", text_color="#ffffff",
                                              fg_color="#8b8b8b", height=d_h, width=d_w, x=x, y=y,
                                              font_size=16).create_obj()
            transport_company_label.place(x=x, y=y)
            transport_company = ctk.CTkComboBox(div4, values=list(haulier_list.keys()), width=d_w,
                                                height=d_h, corner_radius=5)

            new_values = [x for x in haulier_list.keys() if haulier_list.get(x) == record.haulier_id]
            # transport_company.configure(values=new_values)
            transport_company.set(new_values[0])
            self.selected_value['haulier'] = record.haulier_id
            transport_company.position_x = transport_company_label.position_x
            transport_company.position_y = y + 5 + int(transport_company.cget('height'))
            transport_company.place(x=transport_company.position_x, y=transport_company.position_y)

            def trans_callback(choice):
                """function to execute when a transport company is selected"""
                self.selected_value['haulier'] = haulier_list.get(choice)
                return

            transport_company.configure(command=trans_callback)

            x = x + int(transport_company_label.cget('width')) + 10
            customer_label = MyLabel(div4, text='Customer', bg_color="#c9c9c9", text_color="#ffffff",
                                     fg_color="#8b8b8b", height=d_h, width=d_w, x=x, y=y, font_size=16).create_obj()
            customer_label.place(x=x, y=y)

            customer = ctk.CTkComboBox(div4, values=list(customer_list.keys()), width=d_w,
                                       height=d_h, corner_radius=5)

            new_values = [x for x in customer_list.keys() if customer_list.get(x) == record.customer_id]
            # customer.configure(values=new_values)
            customer.set(new_values[0])
            self.selected_value['customer_id'] = record.customer_id
            customer.position_x = transport_company.position_x + int(transport_company.cget('width')) + 10
            customer.position_y = transport_company.position_y
            customer.place(x=customer.position_x, y=customer.position_y)

            def customer_callback(choice):
                """function to execute when a customer item is selected"""
                self.selected_value['customer_id'] = customer_list.get(choice)
                return

            customer.configure(command=customer_callback)

            # division 5
            x = div4.position_x
            y = div4.position_y + int(div4.cget('height'))
            div5 = MyLabel(report_label, text='', bg_color="#c9c9c9",
                           fg_color="#c9c9c9", height=h, width=w, x=x, y=y).create_obj()
            div5.place(x=x, y=y)

            d_w = (int(div5.cget('width')) - 40) // 3
            d_h = (int(div5.cget('height')) - 20) // 2
            x, y = 10, 5
            order_number_label = MyLabel(div5, text='Order Number', bg_color="#c9c9c9", text_color="#ffffff",
                                         fg_color="#8b8b8b", height=d_h, width=d_w, x=x, y=y,
                                         font_size=16).create_obj()
            order_number_label.place(x=x, y=y)
            order_number = ctk.CTkEntry(div5, placeholder_text="Enter order number", width=d_w,
                                        height=d_h)
            order_number.insert(0, record.order_number)
            order_number.position_x = order_number_label.position_x
            order_number.position_y = y + 5 + int(order_number_label.cget('height'))
            order_number.place(x=order_number.position_x, y=order_number.position_y)
            self.selected_value['order_number'] = order_number

            x = order_number_label.position_x + int(order_number_label.cget('width')) + 10
            product_label = MyLabel(div5, text='Product', bg_color="#c9c9c9", text_color="#ffffff",
                                    fg_color="#8b8b8b", height=d_h, width=d_w, x=x, y=y,
                                    font_size=16).create_obj()
            product_label.place(x=x, y=y)
            product = ctk.CTkEntry(div5, placeholder_text="Enter product name", width=d_w,
                                   height=d_h)
            product.insert(0, record.product)
            product.position_x = product_label.position_x
            product.position_y = order_number.position_y
            product.place(x=product.position_x, y=product.position_y)
            self.selected_value['product'] = product

            x = product_label.position_x + int(product_label.cget('width')) + 10
            destination_label = MyLabel(div5, text='Destination', bg_color="#c9c9c9", text_color="#ffffff",
                                        fg_color="#8b8b8b", height=d_h, width=d_w, x=x, y=y,
                                        font_size=16).create_obj()
            destination_label.place(x=x, y=y)
            destination = ctk.CTkEntry(div5, placeholder_text="Enter destination", width=d_w,
                                       height=d_h)
            destination.insert(0, record.destination)
            destination.position_x = destination_label.position_x
            destination.position_y = product.position_y
            destination.place(x=destination.position_x, y=destination.position_y)
            self.selected_value['destination'] = destination

            # division 6
            x = div5.position_x
            y = div5.position_y + int(div5.cget('height'))
            div6 = MyLabel(report_label, text='', bg_color="#c9c9c9",
                           fg_color="#c9c9c9", height=h, width=w, x=x, y=y).create_obj()
            div6.place(x=x, y=y)

            d_w = (int(div6.cget('width')) - 30) // 2
            d_h = (int(div6.cget('height')) - 20) // 2
            x, y = 10, 5
            weight_1_label = MyLabel(div6, text='Initial Weight', bg_color="#c9c9c9", text_color="#ffffff",
                                     fg_color="#8b8b8b", height=d_h, width=d_w, x=x, y=y,
                                     font_size=16).create_obj()
            weight_1_label.place(x=x, y=y)
            weight_1 = ctk.CTkEntry(div6, width=d_w, height=d_h)
            weight_1.insert(0, record.initial_weight)
            weight_1.position_x = weight_1_label.position_x
            weight_1.position_y = y + 5 + int(weight_1_label.cget('height'))
            weight_1.place(x=weight_1.position_x, y=weight_1.position_y)
            self.selected_value['weight_1'] = weight_1

            x = x + int(weight_1_label.cget('width')) + 10
            weight_2_label = MyLabel(div6, text='Final Weight', bg_color="#c9c9c9", text_color="#ffffff",
                                     fg_color="#8b8b8b", height=d_h, width=d_w, x=x, y=y,
                                     font_size=16).create_obj()
            weight_2_label.place(x=x, y=y)
            weight_2 = ctk.CTkEntry(div6, placeholder_text='Vehicle exit weight appears here', width=d_w, height=d_h)
            # insert the value here
            weight_2.insert(0, record.final_weight)
            weight_2.position_x = weight_2_label.position_x
            weight_2.position_y = weight_1.position_y
            weight_2.place(x=weight_2.position_x, y=weight_2.position_y)
            self.selected_value['weight_2'] = weight_2

            # division 7
            x = div6.position_x
            y = div6.position_y + int(div6.cget('height')) + 10
            div7 = MyLabel(report_label, text='', bg_color="#c9c9c9",
                           fg_color="#c9c9c9", height=h, width=w, x=x, y=y).create_obj()
            div7.place(x=x, y=y)

            d_w = (int(div7.cget('width')) - 50) // 2
            cancel_btn = MyButton(div7, text='Cancel', width=d_w, font_size=16,
                                  text_color="#ffbf00", bg_color="#c9c9c9", fg_color="#6699cc", corner_radius=8,
                                  height=d_h, x=10, y=5).create_obj()
            cancel_btn.place(x=cancel_btn.position_x, y=cancel_btn.position_y)

            x = cancel_btn.position_x + int(cancel_btn.cget('width')) + 30
            y = cancel_btn.position_y
            submit_btn = MyButton(div7, text='Submit', width=d_w, font_size=16,
                                  text_color="#ffbf00", bg_color="#c9c9c9", fg_color="#6699cc", corner_radius=8,
                                  height=d_h, x=x, y=y).create_obj()
            submit_btn.place(x=x, y=y)

            def cancel_action():
                """closes the record form"""
                self.toplevel_sub_window.destroy()
                self.toplevel_sub_window = None
                obj.configure(text='Edit Ticket', state='enabled')

            def submit_form_entry():
                """processes entry data and submits it for saving in the database"""
                submit_btn.configure(text="Processing, please wait...")
                # submit_btn.place(x=x, y=y)

                data = self.selected_value
                mr = {}
                mr['product'] = data['product'].get()
                mr['order_number'] = data['order_number'].get()
                mr['destination'] = data['destination'].get()
                mr['vehicle_name'] = data['vehicle_name'].get()
                mr['vehicle_id'] = data['vehicle_id'].get()
                mr['driver_phone'] = data['driver_phone'].get()
                mr['driver_name'] = data['driver_name'].get()
                mr['customer'] = data['customer_id']
                mr['haulier'] = data['haulier']
                mr['weight_1'] = int(data['weight_1'].get())
                mr['operator'] = self.current_user.id
                mr['weight_2'] = int(data['weight_2'].get())
                mr['action'] = 'edit'
                mr['weight_log_id'] = ticket_id

                messenger = Messenger(self.server_url, '/update_records')
                report_label.destroy()
                resp = messenger.query_server(mr)
                self.focus()

                if resp['status'] != 1:
                    self.update_status(resp['message'])
                else:
                    self.toplevel_sub_window.destroy()
                    self.toplevel_sub_window = None
                    self.update_status(resp['message'])
                    obj.configure(text='Edit Ticket', state='enabled')
                return

            def submit_action():
                self.thread_request(submit_form_entry)
                return

            cancel_btn.configure(command=cancel_action)
            submit_btn.configure(command=submit_action)
            self.toplevel_sub_window.protocol("WM_DELETE_WINDOW", cancel_action)

        else:
            self.toplevel_sub_window.focus()
        return

    def edit_waybill(self, item, waybill_info):
        """
        Opens a custom top-level window for logging waybill information.
        """
        # check if waybill has been approved
        if item.approval_status == "approved":
            func.notify_user("Waybill has been approved, you cannot make further changes to it.")
            self.focus()
            self.update_status('Permission denied!')
            self.toplevel_window.focus()
            return
        if self.current_user.admin_type == "user":
            func.notify_user("You are not authorized to perform this action.")
            self.focus()
            self.update_status('Permission denied!')
            self.toplevel_window.focus()
            return

        # destroy the waybill view
        self.toplevel_window.destroy()
        self.toplevel_window = None

        customer_list = {}
        for customer in self.fetched_resource['customers']:
            customer_list[customer['customer_name']] = customer['customer_id']
        files = []
        counter = 0
        if self.toplevel_window is None:

            customer_window = ctk.CTkToplevel(self)
            customer_window.geometry("{}x{}".format(650, 640))
            customer_window.title(f"Editing Waybill Information for {waybill_info['vehicle_id']}")

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

            # create text_variable for address
            tv3 = tk.StringVar()
            tv3.set(waybill_info['address'])
            address_entry = ctk.CTkEntry(customer_window, width=250, textvariable=tv3)

            # create text_variable for waybill number
            tv4 = tk.StringVar()
            tv4.set(waybill_info['waybill_number'])
            waybill_entry = ctk.CTkEntry(customer_window, width=250, textvariable=tv4)

            customer_entry.set(waybill_info['customer_name'])  # Set default value
            condition_entry.set('good')  # Set default value

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
                    'weight_log_id': item.id,
                    'id': waybill_info['id'],
                    'received_by': self.current_user.full_name
                }

                # process the files
                files_dict = dict(files)

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

                    submit_btn.configure(text="Finished!")
                    customer_window.destroy()
                    self.saved_values = {}
                    self.toplevel_window = None
                    self.bad_counter = 0
                    self.counter = 0
                else:
                    self.update_status(resp['message'])

                return

            def cancel_window():
                """
                Closes the haulier information window without saving any data.
                """
                self.toplevel_window = None
                self.saved_values = {}
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




