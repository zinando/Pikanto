import threading

from appclasses.labelclass import MyLabel
from appclasses.email_class import SendMail
from appclasses.views import CreateAppView
from appclasses.buttonclass import MyButton
from appclasses.textbox_class import MyTexBox
from helpers import myfunctions as func
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk
from appclasses.file_class import FileHandler
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

    def open_waybill_formxxxx(self, item):
        """creates a window for adding waybill data to weight records"""
        files = []

        # create a dialogue box that allows the user to enter waybill data
        if self.toplevel_window is None:
            # stop the status display
            self.status_message = 'stop'

            # create the dialogue box
            my_dialogue_box = DialogueBox(650, 480, fg_color='grey')
            my_dialogue_box.title('WAYBILL FORM')

            # create 6 rows for the entry widgets, 4 widgets per row

            # row 1
            d_h = my_dialogue_box.height // 6
            d_w = my_dialogue_box.width
            x, y = 0, 0
            row_1 = MyLabel(my_dialogue_box, text="", bg_color="grey", fg_color="grey", height=d_h, width=d_w,
                            x=x, y=y).create_obj()
            row_1.place(x=x, y=y)

            h = 40
            w = (int(row_1.cget('width')) - 40) // 4
            x = 5
            y = (int(row_1.cget('height')) - h) // 2
            waybill_number = ctk.CTkEntry(row_1, placeholder_text="Enter waybill number", width=w,
                                          height=h)
            waybill_number.place(x=x, y=y)
            self.selected_value['waybill_number'] = waybill_number

            x = x + int(waybill_number.cget('width')) + 5
            company_ref = ctk.CTkEntry(row_1, placeholder_text="Enter Company Reference", width=w,
                                       height=h)
            company_ref.place(x=x, y=y)
            self.selected_value['company_ref'] = company_ref

            x = x + int(company_ref.cget('width')) + 5
            customers = {'name_1': 1, 'name_2': 2, 'name_3': 3, 'name_4': 4}
            customer = ctk.CTkComboBox(row_1, values=list(customers.keys()), width=w,
                                       height=h, corner_radius=5)
            customer.set('Select customer')
            customer.place(x=x, y=y)

            def customer_callback(choice):
                """function to execute when a customer item is selected"""
                self.status_message = 'wait'
                self.selected_value['customer_id'] = customers.get(choice)
                self.status_message = None

            customer.configure(command=customer_callback)

            x = x + int(customer.cget('width')) + 5
            address = ctk.CTkEntry(row_1, placeholder_text="Enter delivery address", width=w,
                                   height=h)
            address.place(x=x, y=y)
            self.selected_value['address'] = address

            # row 2
            x = 0
            y = int(row_1.cget('height')) + row_1.position_y
            row_2 = MyLabel(my_dialogue_box, text="", bg_color="grey", fg_color="grey", height=d_h, width=d_w,
                            x=x, y=y).create_obj()
            row_2.place(x=x, y=y)

            w = (int(row_2.cget('width')) - 40) // 4
            x, y = 5, (int(row_2.cget('height')) - h) // 2
            description = ctk.CTkEntry(row_2, placeholder_text="Enter product description", width=w,
                                       height=h)
            description.place(x=x, y=y)
            self.selected_value['description'] = description

            x = x + int(description.cget('width')) + 10
            item_code = ctk.CTkEntry(row_2, placeholder_text="Enter item code", width=w,
                                     height=h)
            item_code.place(x=x, y=y)
            self.selected_value['item_code'] = item_code

            x = x + int(item_code.cget('width')) + 10
            product_count = ctk.CTkEntry(row_2, placeholder_text="Enter Number cases/bags", width=w,
                                         height=h)
            product_count.place(x=x, y=y)
            self.selected_value['product_count'] = product_count

            x = x + int(product_count.cget('width')) + 10
            product_weight = ctk.CTkEntry(row_2, placeholder_text="Enter product weight", width=w,
                                          height=h)
            product_weight.place(x=x, y=y)
            self.selected_value['product_weight'] = product_weight

            # row 3
            x = 0
            y = int(row_2.cget('height')) + row_2.position_y
            row_3 = MyLabel(my_dialogue_box, text="", bg_color="grey", fg_color="grey", height=d_h, width=d_w,
                            x=x, y=y).create_obj()
            row_3.place(x=x, y=y)

            w = (int(row_3.cget('width')) - 30) // 4
            x, y = 5, (int(row_2.cget('height')) - h) // 2
            accepted_qty = ctk.CTkEntry(row_3, placeholder_text="Enter accepted quantity", width=w,
                                        height=h)
            accepted_qty.place(x=x, y=y)
            self.selected_value['accepted_qty'] = accepted_qty

            x = x + int(accepted_qty.cget('width')) + 5
            product_condition = ctk.CTkComboBox(row_3, values=['good', 'bad'], width=w,
                                                height=h, corner_radius=5)
            product_condition.set('Product condition')
            product_condition.place(x=x, y=y)

            def condition_callback(choice):
                self.status_message = 'wait'
                self.selected_value['product_condition'] = choice
                self.status_message = None

            product_condition.configure(command=condition_callback)

            x = x + int(product_condition.cget('width')) + 5
            damaged_qty = ctk.CTkEntry(row_3, placeholder_text="Enter damaged qty", width=w,
                                       height=h)
            damaged_qty.place(x=x, y=y)
            self.selected_value['damaged_qty'] = damaged_qty

            x = x + int(damaged_qty.cget('width')) + 5
            shortage = ctk.CTkEntry(row_3, placeholder_text="Enter product shortage", width=w,
                                    height=h)
            shortage.place(x=x, y=y)
            self.selected_value['shortage'] = shortage

            # row 4
            x = 0
            y = int(row_3.cget('height')) + row_3.position_y
            row_4 = MyLabel(my_dialogue_box, text="", bg_color="grey", fg_color="grey", height=d_h, width=d_w,
                            x=x, y=y).create_obj()
            row_4.place(x=x, y=y)

            w = (int(row_4.cget('width')) - 40) // 4
            x, y = 5, (int(row_4.cget('height')) - h) // 2
            batch_number = ctk.CTkEntry(row_4, placeholder_text="Enter batch number", width=w,
                                        height=h)
            batch_number.place(x=x, y=y)
            self.selected_value['batch_number'] = batch_number

            x = x + int(batch_number.cget('width')) + 10
            receiver = ctk.CTkEntry(row_4, placeholder_text="Enter your name", width=w,
                                    height=h)
            receiver.place(x=x, y=y)
            self.selected_value['receiver'] = receiver

            x = x + int(receiver.cget('width')) + 10
            delivered_by = ctk.CTkEntry(row_4, placeholder_text="Enter driver name", width=w,
                                        height=h)
            delivered_by.place(x=x, y=y)
            self.selected_value['delivered_by'] = delivered_by

            x = x + int(delivered_by.cget('width')) + 5
            remarks = ctk.CTkEntry(row_4, placeholder_text="Remarks", width=w,
                                   height=h)
            remarks.place(x=x, y=y)
            self.selected_value['remarks'] = remarks

            # division 5
            x = 0
            y = int(row_4.cget('height')) + row_4.position_y
            row_5 = MyLabel(my_dialogue_box, text='', bg_color="grey", fg_color="grey",
                            height=d_h, width=d_w, x=x, y=y).create_obj()
            row_5.place(x=x, y=y)

            w = 150
            x = 470
            y = (int(row_5.cget('height')) - h) // 2
            upload_btn = MyButton(row_5, text='Select files', width=w, font_size=16,
                                  text_color="#ffbf00", bg_color="grey", fg_color="#6699cc",
                                  corner_radius=8, height=h, x=x, y=y).create_obj()
            upload_btn.place(x=upload_btn.position_x, y=upload_btn.position_y)

            file_listbox = tk.Listbox(row_5, cnf={'bg': 'grey'}, selectmode=tk.MULTIPLE, width=85, height=6,
                                      font=("Arial", 13))
            file_listbox.place(x=10, y=15)

            def delete_file_from_listbox(file_path):
                """removes a selected file from the listbox"""
                index = file_listbox.get(0, tk.END).index(file_path)
                file_listbox.delete(index)
                file_listbox.delete(index)  # Remove the delete button associated with the file

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

            # division 6
            x = 0
            y = int(row_5.cget('height')) + row_5.position_y
            row_6 = MyLabel(my_dialogue_box, text='', bg_color="#c9c9c9",
                            fg_color="#c9c9c9", height=d_h, width=d_w, x=x, y=y).create_obj()
            row_6.place(x=x, y=y)

            w = 200
            x = ((int(row_6.cget('width')) // 2) - w) // 2
            y = (int(row_6.cget('height')) - h) // 2
            cancel_btn = MyButton(row_6, text='Cancel', width=w, font_size=16,
                                  text_color="#ffbf00", bg_color="#c9c9c9", fg_color="#6699cc",
                                  corner_radius=0, height=h, x=x, y=y).create_obj()
            cancel_btn.place(x=cancel_btn.position_x, y=cancel_btn.position_y)

            x = int(row_6.cget('width')) // 2 + x
            y = cancel_btn.position_y
            submit_btn = MyButton(row_6, text='Submit', width=w, font_size=16,
                                  text_color="#ffbf00", bg_color="#c9c9c9", fg_color="#6699cc", corner_radius=0,
                                  height=h, x=x, y=y).create_obj()
            submit_btn.place(x=x, y=y)

            def cancel_action():
                """closes the record form"""
                my_dialogue_box.destroy()
                self.toplevel_window = None

            def submit_form_entries():
                """processes entry data and submits it for saving in the database"""
                submit_btn.configure(text="Processing, please wait...")
                submit_btn.place(x=x, y=y)

                # check if the select items were selected
                try:
                    pc = self.selected_value['product_condition']
                    cid = self.selected_value['customer_id']
                except KeyError:
                    func.notify_user('You did not select one option')
                    self.toplevel_window.focus()
                    submit_btn.configure(text="Submit")
                    return

                data = self.selected_value
                mr = {}
                mr['waybill_number'] = data['waybill_number'].get()
                mr['company_ref'] = data['company_ref'].get()
                mr['address'] = data['address'].get()
                mr['description'] = data['description'].get()
                mr['vehicle_id'] = item.vehicle_id
                mr['item_code'] = data['item_code'].get()
                mr['product_count'] = data['product_count'].get()
                mr['product_weight'] = data['product_weight'].get()
                mr['accepted_qty'] = data['accepted_qty'].get()
                mr['damaged_qty'] = data['damaged_qty'].get()
                mr['shortage'] = data['shortage'].get()
                mr['batch_number'] = data['batch_number'].get()
                mr['receiver'] = data['receiver'].get()
                mr['delivered_by'] = data['delivered_by'].get()
                mr['remarks'] = data['remarks'].get()
                mr['weight_log_id'] = item.id
                mr['product_condition'] = data['product_condition']
                mr['customer_id'] = data['customer_id']

                # process the files
                files_dict = dict(files)

                messenger = Messenger(self.server_url, '/create_waybill?action=save_data')
                resp = messenger.query_server(data=mr)
                if resp['status'] == 1:
                    messenger = Messenger(self.server_url,
                                          '/create_waybill?action=save_file&waybill_id={}&vehicle_id={}' \
                                          .format(resp['data']['waybill_id'], resp['data']['vehicle_id']))
                    response = messenger.query_server(files=files_dict)
                    self.update_status(response['message'])
                else:
                    self.update_status(resp['message'])
                return

            def thread_request():
                """Starts a thread that processes form and data and sends it to the database for storage"""
                submit_btn.configure(text="Processing...")

                # Start a thread to handle the database operation
                thread = threading.Thread(target=submit_form_entries)
                thread.daemon = True  # Daemonize the thread to avoid issues on application exit
                thread.start()

                # After starting the thread, update the button text back to its original state
                thread.join(timeout=15)  # Wait for the thread to finish, with a timeout if needed
                submit_btn.configure(text="Submit")
                time.sleep(3)
                my_dialogue_box.destroy()
                self.toplevel_window = None

            cancel_btn.configure(command=cancel_action)
            submit_btn.configure(command=thread_request)

            my_dialogue_box.protocol("WM_DELETE_WINDOW", self.on_closing)
            my_dialogue_box.focus_set()
            self.toplevel_window = my_dialogue_box

        else:
            self.toplevel_window.focus()

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

    def display_data_details(self, ticket_data=None, waybill_data=None):
        """
        Function to display the Weighbridge Slip in a top-level window.

        It creates a table displaying Weighbridge Slip data and fields for entering
        the driver's name and signature.
        """
        ticket_data = {
            "Date": "2023-12-01",
            "Vehicle ID": "ABC123",
            "Customer": "Customer A",
            "Haulier": "Haulier A",
            "Destination": "Destination A",
            "Product": "Product A",
            "Ticket Number": "T123",
            "Delivery Number": "D456",
            "Order Number": "O789",
            "Gross Mass": "1000 kg",
            "Tare Mass": "500 kg",
            "Net Mass": "500 kg",
        }

        company_info_data = {
            "Waybill Number": "WB001",
            "Date": "2023-12-01",
            "Location": "Location A",
            "Ugee Ref Number": "UR001",
            "Customer Ref Number": "CR001",
            "Customer Name": "Customer A",
            "Delivery Address": "Address A",
            "Vehicle ID": "V001",
            "Transporter": "Transporter A"
            # Add more company info data as needed...
        }

        product_data = [
            {
                "Product Description": "Product A",
                "Item Code": "001",
                "Number of Packages": 5,
                "Quantity": 100,
                "Accepted Quantity": 90,
                "Remarks": "Some remarks"
            },
            # Add more product data as needed...
        ]

        bad_products_info = [
            {
                "product_description": "Damaged Product A",
                "damaged_quantity": 5,
                "shortage_quantity": 2,
                "batch_number": "B001"
            },
            # Add more bad products info dictionaries as needed...
        ]

        top_level = tk.Toplevel(self)
        top_level.title("Weighbridge")

        # Create a frame for the table
        ticket_frame = ctk.CTkFrame(top_level)
        ticket_frame.pack(fill=tk.X)

        # Create a title label for "Weighbridge Slip"
        title_label = ttk.Label(ticket_frame, text="Weighbridge Slip", font=("TkDefaultFont", 16, "bold"))
        title_label.pack(pady=10)

        # Create Treeview widget
        ticket_tree = ttk.Treeview(ticket_frame, columns=("Key", "Value"), show="headings")
        ticket_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Define columns
        ticket_tree.heading("Key", text="Attributes")
        ticket_tree.heading("Value", text="Values")

        # Insert data into the treeview
        for key, value in ticket_data.items():
            ticket_tree.insert("", "end", values=(key, value))
            ticket_tree.tag_configure('column', font=("Arial", 16, "bold"), foreground="black")

        # Add fields for driver's name and signature in the same row
        driver_frame = ttk.Frame(top_level)
        driver_frame.pack(pady=10)

        driver_name_label = ttk.Label(driver_frame, text="Driver's Name:")
        driver_name_label.grid(row=0, column=0, padx=5)

        driver_name_entry = ttk.Entry(driver_frame)
        driver_name_entry.grid(row=0, column=1, padx=5)

        driver_signature_label = ttk.Label(driver_frame, text="Driver's Signature:")
        driver_signature_label.grid(row=0, column=2, padx=5)

        driver_signature_entry = ttk.Entry(driver_frame)
        driver_signature_entry.grid(row=0, column=3, padx=5)

        # Load and resize the image
        img = Image.open('static/assets/images/logo/mylogo.PNG')
        img = img.resize((img.width, min(img.height, 150)), Image.BILINEAR)
        img = ImageTk.PhotoImage(img)

        # Create a frame for the image
        image_frame = tk.Frame(top_level)
        image_frame.pack()

        # Display the resized image
        image_label = tk.Label(image_frame, image=img)
        image_label.image = img  # Keep a reference to the image
        image_label.pack(pady=10)

        # Create a label for "WAYBILL INFORMATION" with black background
        waybill_label = tk.Label(top_level, text="WAYBILL INFORMATION", bg="black", fg="white",
                                 font=("Arial", 16, "bold"))
        waybill_label.pack()

        # Create a table for company information
        company_info_frame = ttk.Frame(top_level)
        company_info_frame.pack(fill=tk.X)

        company_info_table = ttk.Treeview(company_info_frame, columns=("Attribute", "Value"), show="headings")
        company_info_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        company_info_table.heading("Attribute", text="Attribute")
        company_info_table.heading("Value", text="Value")

        for key, value in company_info_data.items():
            company_info_table.insert("", "end", values=(key, value))
            company_info_table.tag_configure('column', font=("Arial", 16, "bold"))

        # Create the second table for product information
        product_frame = ttk.Frame(top_level)
        product_frame.pack()

        product_table = ttk.Treeview(product_frame, columns=("Description", "Item Code", "Packages",
                                                             "Quantity", "Accepted Quantity", "Remarks"),
                                     show="headings")
        product_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        product_table.heading("Description", text="Product Description")
        product_table.heading("Item Code", text="Item Code")
        product_table.heading("Packages", text="Number of Packages")
        product_table.heading("Quantity", text="Quantity")
        product_table.heading("Accepted Quantity", text="Accepted Quantity")
        product_table.heading("Remarks", text="Remarks")

        # make the headings bold
        for col in product_table["columns"]:
            product_table.heading(col, text=col, anchor=tk.W)
            product_table.tag_configure(col, font=("Arial", 16, "bold"), foreground="black")

        for item in product_data:
            product_table.insert("", "end", values=(
                item["Product Description"],
                item["Item Code"],
                item["Number of Packages"],
                item["Quantity"],
                item["Accepted Quantity"],
                item["Remarks"]
            ))

        # Create a table footer for total under product description
        footer_frame = ttk.Frame(top_level)
        footer_frame.pack()

        footer_label = ttk.Label(footer_frame, text="Total:", font=("TkDefaultFont", 14, "bold"))
        footer_label.grid(row=0, column=0, padx=5)

        footer_value_label = ttk.Label(footer_frame, text="Value", font=("TkDefaultFont", 14, "bold"))
        footer_value_label.grid(row=0, column=1, padx=5)

        # Create a label for "Bad/Damaged Products"
        bad_products_label = ttk.Label(top_level, text="Bad/Damaged Products", font=("Arial", 14, "bold"))
        bad_products_label.pack()

        # Create the third table for bad/damaged products information
        bad_products_frame = ttk.Frame(top_level)
        bad_products_frame.pack(fill=tk.X)

        bad_products_table = ttk.Treeview(bad_products_frame, columns=("product_description", "damaged_quantity",
                                                                       "shortage_quantity", "batch_number"),
                                          show="headings")
        bad_products_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        bad_products_table.heading("product_description", text="Product Description")
        bad_products_table.heading("damaged_quantity", text="Damaged Quantity")
        bad_products_table.heading("shortage_quantity", text="Shortage Quantity")
        bad_products_table.heading("batch_number", text="Batch Number")

        for product_info in bad_products_info:
            bad_products_table.insert("", "end", values=(
                product_info["product_description"],
                product_info["damaged_quantity"],
                product_info["shortage_quantity"],
                product_info["batch_number"]
            ))

        # Create a label for approvals frame
        approval_label = ttk.Label(top_level, text="Approvals", font=("Arial", 18, "bold"))
        approval_label.pack()

        # Create the frame for approvals table
        approvals_frame = ttk.Frame(top_level)
        approvals_frame.pack(fill=tk.X)

        # Create the approvals table
        approvals_table = ttk.Treeview(approvals_frame, columns=("Received By", "Delivered By", "Authorized By"),
                                       show="headings")
        approvals_table.pack(fill=tk.X)

        approvals_table.heading("Received By", text="Received By")
        approvals_table.heading("Delivered By", text="Delivered By")
        approvals_table.heading("Authorized By", text="Authorized By")

        # Insert rows for Name, Signature, and Date under each header
        info = {"receiver": "WHSE Technician ", "receiver_signature": "...........", "receiver_date": "Today",
                "deliverer": "Driver", "deliverer_signature": "..............: ", "deliverer_date": "Today",
                "approver": "Plant Manager", "approver_signature": "...............: ", "approver_date": "Today"}

        approvals_table.insert("", "end", values=(
            f"Name:    {info['receiver']}\n\nSignature:     {info['receiver_signature']}\n\nDate:     {info['receiver_date']}",
            f"Name:    {info['deliverer']}\n\nSignature:    {info['deliverer_signature']}\n\nDate:    {info['deliverer_date']}",
            f"Name:    {info['approver']}\n\nSignature:     {info['approver_signature']}\n\nDate:     {info['approver_date']}",
        ))

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
        tree.heading('s/n', text='S/N')
        tree.heading('description', text='Description')
        tree.heading('code', text='Code')
        tree.heading('count', text='Count')
        tree.heading('weight', text='Weight')
        tree.heading('accepted qty', text='Accepted Qty')
        tree.heading('remarks', text='Remarks')

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
        tree.heading('s/n', text='S/N')
        tree.heading('description', text='Description')
        tree.heading('damaged quantity', text='Damaged Quantity')
        tree.heading('shortage', text='Shortage')
        tree.heading('batch number', text='Batch Number')

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

                product_data = {
                    'counter': self.counter + 1,
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

                bad_product_data = {
                    'counter': self.bad_counter + 1,
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

                request_email = approver_info['email']  # 'xienando4reaconcepts@gmail.com'  # approver_info['email']
                email_body, attachment_files = self.prepare_template_data(item, request_email)
                subject = 'Waybill Approval Request'
                sender = 'zinando2000@gmail.com'
                messenger = SendMail(sender, request_email, subject)
                messenger.elastic_email_by_smtp(email_body, attachment_files)

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
        return template, files
