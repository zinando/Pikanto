"""This is the main application window module"""
from appclasses.labelclass import MyLabel
from appclasses.email_class import SendMail
from appclasses.views import CreateAppView
from appclasses.more_views import WindowViews
from appclasses.buttonclass import MyButton
from appclasses.textbox_class import MyTexBox
from helpers import myfunctions as func
from threading import Thread
import customtkinter as ctk
from functools import partial
from appclasses.toplevel_class import DialogueBox
from appclasses.report_messenger import Messenger
from appclasses.dotdict_class import DotDict
from appclasses.group_class import SubGroupCreator
import os
import sys
import json
import time
from datetime import datetime 


class Pikanto(WindowViews):
    """This creates an instance of the Pikanto app main window"""

    def __init__(self):
        """inherit the properties of CreateAppView class"""
        super(Pikanto, self).__init__()
        self.toplevel_window = None
        self.selected_value = {}
        self.current_user = None
        self.fetched_resource = {}
        self.create_base_view()
        self.check_internet_connection()
        if len(sys.argv) > 1:
            user_id = sys.argv[1]
            self.thread_request(self.load_current_user, int(user_id))
        self.fetch_resources()

    def create_report_form(self):
        """creates the dialogue box for entering email report data"""
        # check for existing initial weight data record for the vehicle (self.selected_value['haulier'])
        worker = Messenger(self.server_url, '/search/existing_weight_record')
        response = worker.query_server({'vehicle_id': self.selected_value['vehicle_id']})
        record = response['data']
        if record:
            record = DotDict(response['data'])
            header_text = "Update Vehicle Record"
        else:
            header_text = "Create New Record"

        customers, hauliers = response['customers'], response['hauliers']

        # check that customer and haulier list are not empty
        if customers is None or len(customers) == 0:
            self.update_status('No customers record found in the database')
            return
        if hauliers is None or len(hauliers) == 0:
            self.update_status('No haulier record found in the database')
            return

        customer_list = {}
        for x in customers:
            customer_list[x['customer_name']] = x['customer_id']
        haulier_list = {}
        for y in hauliers:
            haulier_list[y['haulier_name']] = y['haulier_id']

        # create a label the size of the main display label
        h = int(self.display_label.cget('height'))
        w = int(self.display_label.cget('width'))
        x, y = self.display_label.position_x, self.display_label.position_y
        report_label = MyLabel(self, text="", bg_color="#ffffff", fg_color="#c9c9c9", height=h, width=w, x=x, y=y) \
            .create_obj()
        report_label.place(x=x, y=y)

        #  create header for the form
        h = 100
        x, y = 0, 0
        report_header_label = MyLabel(report_label, text=header_text, bg_color="#c9c9c9",
                                      fg_color="#838383", height=h, width=w, x=x, y=y, text_color="#ffffff",
                                      font_size=28, font_weight="bold") \
            .create_obj()
        report_header_label.place(x=x, y=y)

        # create 7 label divisions for the remaining form space
        h = (int(report_label.cget('height')) - int(report_header_label.cget('height'))) // 7
        w = report_label.cget('width')
        x = report_header_label.position_x
        y = report_header_label.position_y + int(report_header_label.cget('height'))
        text = "Weight Data: {} {}".format(self.weight_data, self.unit)
        div1 = MyLabel(report_label, text=text, bg_color="#c9c9c9",
                       fg_color="#ffffff", height=h, width=w, x=x, y=y, text_color="#000000",
                       font_size=22, font_weight="bold", corner_radius=8).create_obj()
        div1.place(x=x, y=y)

        # division 2
        y = div1.position_y + int(div1.cget('height'))
        div2 = MyLabel(report_label, text='', bg_color="#c9c9c9",
                       fg_color="#c9c9c9", height=h, width=w, x=x, y=y).create_obj()
        div2.place(x=x, y=y)

        d_w = (int(div2.cget('width')) - 30) // 2
        d_h = 40
        vehicle_id = ctk.CTkEntry(div2, placeholder_text="Enter vehicle id", width=d_w,
                                  height=d_h)
        vehicle_id.insert(0, self.selected_value['vehicle_id'])
        if record:
            vehicle_id.configure(state='disabled')
        vehicle_id.position_x, vehicle_id.position_y = 10, 5
        vehicle_id.place(x=vehicle_id.position_x, y=vehicle_id.position_y)
        self.selected_value['vehicle_id'] = vehicle_id

        vehicle_name = ctk.CTkEntry(div2, placeholder_text="Enter vehicle name", width=d_w,
                                    height=d_h)
        if record:
            vehicle_name.insert(0, record.vehicle_name)
            vehicle_name.configure(state='disabled')
        vehicle_name.position_x = vehicle_id.position_x + int(vehicle_id.cget('width')) + 10
        vehicle_name.position_y = vehicle_id.position_y
        vehicle_name.place(x=vehicle_name.position_x, y=vehicle_name.position_y)
        self.selected_value['vehicle_name'] = vehicle_name

        # division 3
        y = div2.position_y + int(div2.cget('height'))
        div3 = MyLabel(report_label, text='', bg_color="#c9c9c9",
                       fg_color="#c9c9c9", height=h, width=w, x=x, y=y).create_obj()
        div3.place(x=x, y=y)

        d_w = (int(div3.cget('width')) - 30) // 2
        driver_name = ctk.CTkEntry(div3, placeholder_text="Enter driver name here", width=d_w,
                                   height=d_h)
        if record:
            driver_name.insert(0, record.driver_name)
            driver_name.configure(state='disabled')
        driver_name.position_x, driver_name.position_y = 10, 5
        driver_name.place(x=driver_name.position_x, y=driver_name.position_y)
        self.selected_value['driver_name'] = driver_name

        driver_phone = ctk.CTkEntry(div3, placeholder_text="Enter driver phone number", width=d_w,
                                    height=d_h)
        if record:
            driver_phone.insert(0, record.driver_phone)
            driver_phone.configure(state='disabled')
        driver_phone.position_x = driver_name.position_x + int(driver_name.cget('width')) + 10
        driver_phone.position_y = driver_name.position_y
        driver_phone.place(x=driver_phone.position_x, y=driver_phone.position_y)
        self.selected_value['driver_phone'] = driver_phone

        # division 4
        y = div3.position_y + int(div3.cget('height'))
        div4 = MyLabel(report_label, text='', bg_color="#c9c9c9",
                       fg_color="#c9c9c9", height=h, width=w, x=x, y=y).create_obj()
        div4.place(x=x, y=y)

        d_w = (int(div4.cget('width')) - 30) // 2
        trans_companies = {'name_1': 1, 'name_2': 2, 'name_3': 3, 'name_4': 4}
        transport_company = ctk.CTkComboBox(div4, values=list(haulier_list.keys()), width=d_w,
                                            height=d_h, corner_radius=5)
        if record:
            new_values = [x for x in haulier_list.keys() if haulier_list.get(x) == record.haulier_id]
            transport_company.configure(values=new_values)
            transport_company.set(new_values[0])
            self.selected_value['haulier'] = record.haulier_id
        else:
            transport_company.set('Select transport company')
        transport_company.position_x, transport_company.position_y = 10, 5
        transport_company.place(x=transport_company.position_x, y=transport_company.position_y)

        def trans_callback(choice):
            """function to execute when a transport company is selected"""
            self.status_message = 'wait'
            self.selected_value['haulier'] = haulier_list.get(choice)
            self.status_message = None

        transport_company.configure(command=trans_callback)

        customers = {'name_1': 1, 'name_2': 2, 'name_3': 3, 'name_4': 4}
        customer = ctk.CTkComboBox(div4, values=list(customer_list.keys()), width=d_w,
                                   height=d_h, corner_radius=5)
        if record:
            new_values = [x for x in customer_list.keys() if customer_list.get(x) == record.customer_id]
            customer.configure(values=new_values)
            customer.set(new_values[0])
            self.selected_value['customer_id'] = record.customer_id
        else:
            customer.set('Select customer')
        customer.position_x = transport_company.position_x + int(transport_company.cget('width')) + 10
        customer.position_y = transport_company.position_y
        customer.place(x=customer.position_x, y=customer.position_y)

        def customer_callback(choice):
            """function to execute when a customer item is selected"""
            self.status_message = 'wait'
            self.selected_value['customer_id'] = customer_list.get(choice)
            self.status_message = None

        customer.configure(command=customer_callback)

        # division 5
        y = div4.position_y + int(div4.cget('height'))
        div5 = MyLabel(report_label, text='', bg_color="#c9c9c9",
                       fg_color="#c9c9c9", height=h, width=w, x=x, y=y).create_obj()
        div5.place(x=x, y=y)

        d_w = (int(div5.cget('width')) - 20) // 3
        order_number = ctk.CTkEntry(div5, placeholder_text="Enter order number", width=d_w,
                                    height=d_h)
        if record:
            order_number.insert(0, record.order_number)
            order_number.configure(state='disabled')
        order_number.position_x, order_number.position_y = 10, 5
        order_number.place(x=order_number.position_x, y=order_number.position_y)
        self.selected_value['order_number'] = order_number

        product = ctk.CTkEntry(div5, placeholder_text="Enter product name", width=d_w,
                               height=d_h)
        if record:
            product.insert(0, record.product)
            product.configure(state='disabled')
        product.position_x = order_number.position_x + int(order_number.cget('width')) + 5
        product.position_y = order_number.position_y
        product.place(x=product.position_x, y=product.position_y)
        self.selected_value['product'] = product

        destination = ctk.CTkEntry(div5, placeholder_text="Enter destination", width=d_w,
                                   height=d_h)
        if record:
            destination.insert(0, record.destination)
            destination.configure(state='disabled')
        destination.position_x = product.position_x + int(product.cget('width')) + 5
        destination.position_y = product.position_y
        destination.place(x=destination.position_x, y=destination.position_y)
        self.selected_value['destination'] = destination

        # division 6
        y = div5.position_y + int(div5.cget('height'))
        div6 = MyLabel(report_label, text='', bg_color="#c9c9c9",
                       fg_color="#c9c9c9", height=h, width=w, x=x, y=y).create_obj()
        div6.place(x=x, y=y)

        d_w = (int(div6.cget('width')) - 20) // 3
        weight_1 = ctk.CTkEntry(div6, width=d_w, height=d_h)
        if record:
            weight_1.insert(0, "{}{}    |  {}".format(record.initial_weight, self.unit, record.initial_time))
        else:
            weight_1.insert(0, self.weight_data)
        weight_1.configure(state='disabled')
        weight_1.position_x, weight_1.position_y = 10, 5
        weight_1.place(x=weight_1.position_x, y=weight_1.position_y)
        self.selected_value['weight_1'] = weight_1

        weight_2 = ctk.CTkEntry(div6, placeholder_text='Vehicle exit weight appears here', width=d_w, height=d_h)
        # insert the value here
        if record:
            weight_2.insert(0, "{}{}    |  {}".format(self.weight_data, self.unit, datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")))
        weight_2.configure(state='disabled')
        weight_2.position_x = weight_1.position_x + int(weight_1.cget('width')) + 5
        weight_2.position_y = weight_1.position_y
        weight_2.place(x=weight_2.position_x, y=weight_2.position_y)
        self.selected_value['weight_2'] = weight_2

        weight_3 = ctk.CTkEntry(div6, placeholder_text='Net weight appears here', width=d_w, height=d_h)
        # insert the value here
        if record:
            if self.weight_data > int(record.initial_weight):
                difference = self.weight_data - int(record.initial_weight)
            else:
                difference = int(record.initial_weight) - self.weight_data
            weight_3.insert(0, difference)
        weight_3.configure(state='disabled')
        weight_3.position_x = weight_2.position_x + int(weight_2.cget('width')) + 5
        weight_3.position_y = weight_2.position_y
        weight_3.place(x=weight_3.position_x, y=weight_3.position_y)
        self.selected_value['net_weight'] = weight_3

        # division 7
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
            report_label.destroy()

        def submit_form_entries():
            """processes entry data and submits it for saving in the database"""
            submit_btn.configure(text="Processing, please wait...")
            submit_btn.place(x=x, y=y)

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
            mr['weight_1'] = data['weight_1'].get()
            mr['operator'] = self.current_user.id
            messenger = Messenger(self.server_url, '/save_records')
            if record:
                mr['weight_1'] = record.initial_weight
                mr['weight_2'] = self.weight_data  # data['weight_2'].get()
                mr['net_weight'] = data['net_weight'].get()
                messenger = Messenger(self.server_url, '/update_records')
                report_label.destroy()
                response = messenger.query_server(mr)

                # if successfull, send notification email to WHSE team

                if response['status'] == 1:
                    self.update_status(response['message'])
                    self.update_status('Preparing to send notification to Waybill Technician, please wait...')
                    sender = self.current_user.email
                    request_email = self.waybill_tech_email
                    subject = f"Prepare Waybill for {mr['vehicle_id']}"
                    email_body = "Please prepare waybill for the vehicle ID quoted above.\n\n"
                    email_body += "Regards,\n\n"
                    email_body += f'{self.current_user.full_name}.'
                    messenger = SendMail(sender, request_email, subject)
                    messenger.send_email_with_application(email_body)
            else:
                report_label.destroy()
                resp = messenger.query_server(mr)
                self.update_status(resp['message'])

        def thread_request():
            """Starts a thread that processes form and data and sends it to the database for storage"""
            # Start a thread to handle the database operation
            thread = Thread(target=submit_form_entries)
            thread.daemon = True  # Daemonize the thread to avoid issues on application exit
            thread.start()

        cancel_btn.configure(command=cancel_action)
        submit_btn.configure(command=thread_request)

        return

    def view_weight_records(self, data=None):
        """fetches weight records from database and display them on the main display window"""
        # check if the view is open and close
        if self.record_view_display:
            self.record_view_display.destroy()

        # fetch data from database if data is None
        if not data:
            my_query = Messenger(self.server_url, '/fetch_resources/weight_records')
            response = my_query.query_server({'data': None})
            if response['status'] == 1:
                data = response['data']
            else:
                data = None
                func.notify_user('No records found!')
                return

        if data:
            items_per_page = 5
            grouper = SubGroupCreator(data)
            grouper.create_sub_groups(items_per_page)
            total_groups = grouper.total_groups()

            def display_items(group_number):
                """function creates a widget that displays certain number of data on the main display"""
                items_to_display = grouper.get_group(group_number)

                # create a label the size of the main display label
                h = int(self.display_label.cget('height'))
                w = int(self.display_label.cget('width'))
                x, y = self.display_label.position_x, self.display_label.position_y
                report_label = MyLabel(self, text="", bg_color="#ffffff", fg_color="#c9c9c9", height=h, width=w, x=x,
                                       y=y).create_obj()
                report_label.place(x=x, y=y)
                self.record_view_display = report_label

                #  create header for the form
                h = 60
                x, y = 0, 0
                report_header_label = MyLabel(report_label, text="", bg_color="#ffffff", fg_color="#ffffff",
                                              height=h, width=w, x=x, y=y, text_color="#000000", font_size=28,
                                              font_weight="bold") \
                    .create_obj()
                report_header_label.place(x=x, y=y)

                # create 4 header widgets in the header label
                h = int(report_header_label.cget('height')) - 10
                # w = (((int(report_header_label.cget('width'))-10) // 3) * 2)//3
                w = ((int(report_header_label.cget('width')) - 10) * (2 / 9)) - 5
                x, y = 5, 5
                head_1 = MyTexBox(report_header_label, text='HAULIER', bg_color="#ffffff",
                                  fg_color="#2f6c60", height=h, width=w, x=x, y=y, text_color="#FFFFFF",
                                  font_size=18, font_weight="bold", corner_radius=8).create_obj()
                head_1.place(x=x, y=y)
                head_1.configure(state='disabled')
                x = head_1.position_x + int(head_1.cget('width')) + 5
                head_2 = MyTexBox(report_header_label, text='VEHICLE ID', bg_color="#ffffff",
                                  fg_color="#2f6c60", height=h, width=w, x=x, y=y, text_color="#FFFFFF",
                                  font_size=18, font_weight="bold", corner_radius=8).create_obj()
                head_2.place(x=x, y=y)
                head_2.configure(state='disabled')
                x = head_2.position_x + int(head_2.cget('width')) + 5
                head_3 = MyTexBox(report_header_label, text='TIME', bg_color="#ffffff",
                                  fg_color="#2f6c60", height=h, width=w, x=x, y=y, text_color="#FFFFFF",
                                  font_size=18, font_weight="bold", corner_radius=8).create_obj()
                head_3.place(x=x, y=y)
                head_3.configure(state='disabled')
                w = ((int(report_header_label.cget('width')) - 10) // 3)
                x = head_3.position_x + int(head_3.cget('width')) + 5
                head_4 = MyTexBox(report_header_label, text='ACTIONS', bg_color="#ffffff",
                                  fg_color="#2f6c60", height=h, width=w, x=x, y=y, text_color="#FFFFFF",
                                  font_size=18, font_weight="bold", corner_radius=8).create_obj()
                head_4.place(x=x, y=y)
                head_4.configure(state='disabled')

                # create a wrapper where all the items are going to be displayed
                h = int(report_label.cget('height')) - (50 + int(report_header_label.cget('height')))
                w = int(report_label.cget('width'))
                x, y = 0, int(report_header_label.cget('height')) + report_header_label.position_y
                content_wrapper = MyLabel(report_label, text='', bg_color="#2f6c60",
                                          fg_color="#ffffff", height=h, width=w, x=x, y=y,
                                          font_weight="bold", corner_radius=8).create_obj()
                content_wrapper.place(x=x, y=y)

                # iterate over the list of items to display and create widgets to display
                # ...information for each item wrt to the header
                item_position_y = 0
                for item in items_to_display:
                    item = DotDict(item)
                    skipper = h = content_wrapper.cget('height') // items_per_page
                    w = int(content_wrapper.cget('width')) - 10
                    y = item_position_y
                    x = 5
                    item_wrapper = MyLabel(content_wrapper, text='', bg_color="#2f6c60",
                                           fg_color="#2f6c60", height=h, width=w, x=x, y=y,
                                           font_weight="bold", corner_radius=8).create_obj()
                    item_wrapper.place(x=x, y=y)

                    d_h = h - 20
                    d_w = int(head_1.cget('width')) - 5
                    d_x = head_1.position_x
                    d_y = 10
                    col_1 = MyTexBox(item_wrapper, text=item.haulier, bg_color="#2f6c60",
                                     fg_color="#ffffff", height=d_h, width=d_w, x=d_x, y=d_y, text_color="#000000",
                                     font_size=14, corner_radius=8).create_obj()
                    col_1.place(x=d_x, y=d_y)
                    col_1.configure(state='disabled')

                    # create an indicator to show if item is approved or not
                    if item.approval_status == 'approved':
                        bg_color = '#53f925'
                        indicator_text = 'approved'
                    else:
                        bg_color = 'grey'
                        indicator_text = 'pending'
                    indicator = MyTexBox(col_1, text=indicator_text, bg_color="#ffffff",
                                         fg_color=bg_color, height=(d_h / 2) - 5, width=(d_w / 2) - 10, x=5, y=25,
                                         text_color="#000000", font_size=12, corner_radius=50).create_obj()
                    indicator.place(x=5, y=25)
                    indicator.configure(state='disabled')

                    d_x = head_2.position_x
                    col_2 = MyTexBox(item_wrapper, text=item.vehicle_id, bg_color="#2f6c60",
                                     fg_color="#ffffff", height=d_h, width=d_w, x=d_x, y=d_y, text_color="#000000",
                                     font_size=14, corner_radius=8).create_obj()
                    col_2.place(x=d_x, y=d_y)
                    col_2.configure(state='disabled')

                    d_x = head_3.position_x
                    col_3 = MyTexBox(item_wrapper, text=item.initial_time, bg_color="#2f6c60",
                                     fg_color="#ffffff", height=d_h, width=d_w, x=d_x, y=d_y, text_color="#000000",
                                     font_size=14, corner_radius=8).create_obj()
                    col_3.place(x=d_x, y=d_y)
                    col_3.configure(state='disabled')

                    # create wrapper for the action buttons
                    w = int(head_4.cget('width')) - 5
                    x = head_4.position_x
                    action_btn_wrapper = MyLabel(item_wrapper, text='', bg_color="#2f6c60",
                                                 fg_color="#ffffff", height=d_h, width=w, x=x, y=d_y,
                                                 font_weight="bold", corner_radius=8).create_obj()
                    action_btn_wrapper.place(x=x, y=d_y)

                    # buttons
                    h = 30
                    w = (int(action_btn_wrapper.cget('width')) // 3) - 15
                    x = 5
                    y = (int(action_btn_wrapper.cget('height')) - h) // 2
                    detail_btn = MyButton(action_btn_wrapper, text="Ticket", font_size=12,
                                          text_color="#ffffff", bg_color="#ffffff", fg_color="#6699cc",
                                          height=h, width=w, x=x, y=y,
                                          command=partial(self.view_ticket_details, item)).create_obj()
                    detail_btn.place(x=x, y=y)

                    x = detail_btn.position_x + int(detail_btn.cget('width')) + 15
                    waybill_btn = MyButton(action_btn_wrapper, text="Waybill", font_size=12,
                                           text_color="#ffffff", bg_color="#ffffff", fg_color="#6699cc",
                                           height=h, width=w, x=x, y=y,
                                           command=partial(self.open_waybill_entry, item)).create_obj()
                    waybill_btn.place(x=x, y=y)

                    # waybill button to display details if waybill has been created, else show waybill form
                    if item.waybill_ready:
                        waybill_btn.configure(command=partial(self.view_waybill_detail, item))

                    x = waybill_btn.position_x + int(waybill_btn.cget('width')) + 15
                    ticket_btn = MyButton(action_btn_wrapper, text="Request", font_size=12,
                                          text_color="#ffffff", bg_color="#ffffff", fg_color="#6699cc",
                                          height=h, width=w, x=x, y=y,
                                          command=partial(self.send_approval_request, item)).create_obj()
                    if not item.ticket_ready or not item.waybill_ready or item.approval_status != 'pending':
                        ticket_btn.configure(state='disabled')
                    ticket_btn.place(x=x, y=y)

                    item_position_y += skipper

                # create buttons to navigate different pages of the records
                h = 50
                w = int(report_label.cget('width'))
                y = int(report_label.cget('height')) - 50
                x = 0
                btn_wrapper = MyLabel(report_label, text='', bg_color="#2f6c60",
                                      fg_color="#ffffff", height=h, width=w, x=x, y=y,
                                      font_weight="bold", corner_radius=8).create_obj()
                btn_wrapper.place(x=x, y=y)

                h = 20
                w = 40
                x = (btn_wrapper.cget('width') // 2) - 50
                y = 10
                prev_btn = MyButton(btn_wrapper, text="<< Prev", font_size=12, text_color="#ffffff",
                                    bg_color="#ffffff", fg_color="#6699cc", height=h, width=w, x=x, y=y,
                                    ).create_obj()
                if group_number == 1:
                    prev_btn.configure(state='disabled')
                prev_btn.place(x=x, y=y)

                x = (btn_wrapper.cget('width') // 2) + 10
                next_btn = MyButton(btn_wrapper, text="Next >>", font_size=12, text_color="#ffffff",
                                    bg_color="#ffffff", fg_color="#6699cc", height=h, width=w, x=x, y=y,
                                    ).create_obj()
                if group_number == total_groups:
                    next_btn.configure(state='disabled')
                next_btn.place(x=x, y=y)

                # functions to handle prev and next button clicks
                def on_prev_click():
                    # destroy current view
                    report_label.destroy()
                    display_items(group_number - 1)

                def on_next_click():
                    # destroy current view
                    report_label.destroy()
                    display_items(group_number + 1)

                prev_btn.configure(command=on_prev_click)
                next_btn.configure(command=on_next_click)

                # button to exit the record view from screen
                x = x + 250
                exit_btn = MyButton(btn_wrapper, text="Exit", font_size=12, text_color="#000000",
                                    bg_color="#ffffff", fg_color="#e3b448", height=h, width=w, x=x, y=y,
                                    command=lambda: report_label.destroy()).create_obj()
                exit_btn.place(x=x, y=y)

            display_items(1)

    def window_animation(self, text):
        """displays animation on the main display window"""
        h = int(self.display_label.cget('height')) // 3
        w = (int(self.display_label.cget('width')) // 3) * 2
        x = (int(self.display_label.cget('width')) // 3) // 2 + self.display_label.position_x
        y = self.display_label.position_y + h
        _object = MyLabel(self.display_label, height=h, width=w, bg_color="#ffffff", fg_color="red",
                          text_color="#000000", text=text, x=x, y=y).create_obj()
        _object.place(x=x, y=y)
        return _object

    def record_data(self):
        """generates a dialogue box for user to select transport company"""

        self.selected_value['vehicle_id'] = None

        def btn_action():
            """function to execute when the user submits the form"""
            # check if a value was selected
            self.selected_value['vehicle_id'] = self.state_objects['vehicle_id'].get()
            if not self.selected_value['vehicle_id']:
                func.notify_user('You did not enter any value.')
                return
            self.status_message = None
            self.toplevel_window.destroy()
            self.toplevel_window = None
            self.create_report_form()

        def on_closing():
            """function to execute when dialogue box is about to close"""
            self.status_message = None
            self.toplevel_window.destroy()
            self.toplevel_window = None

        # create a dialogue box that allows the user to select the transport company whose data will be recorded
        if self.toplevel_window is None:
            # stop the status display
            self.status_message = 'stop'

            # create the dialogue box
            my_dialogue_box = DialogueBox(400, 300, fg_color='#2f6c60')
            my_dialogue_box.title('Provide Vehicle ID')
            # create an entry widget in the box
            w = (my_dialogue_box.width // 3) * 2
            transport_company = ctk.CTkEntry(my_dialogue_box, placeholder_text="Enter vehicle id", width=w,
                                             height=40)
            self.state_objects['vehicle_id'] = transport_company
            transport_company.pack(pady=110)
            ok_btn = ctk.CTkButton(my_dialogue_box, text='Submit', text_color='#ffbf00', fg_color='#6699cc',
                                   bg_color='grey', corner_radius=2, border_spacing=0, command=btn_action,
                                   font=("Segoe UI", 12, "normal"))
            ok_btn.pack()
            my_dialogue_box.protocol("WM_DELETE_WINDOW", on_closing)
            self.toplevel_window = my_dialogue_box

        else:
            self.toplevel_window.focus()

    def fetch_resources(self):
        """fetches all usable data from the database"""
        customer = None
        haulier = None
        user = None

        # fetch data from database
        my_query = Messenger(self.server_url, '/fetch_resources/all')
        response = my_query.query_server({'data': None})

        if response['status'] == 1:
            self.fetched_resource['customers'] = customer = response['customers']
            self.fetched_resource['hauliers'] = haulier = response['hauliers']
            self.fetched_resource['users'] = user = response['users']
        else:
            self.fetched_resource['customers'] = []
            self.fetched_resource['hauliers'] = []
            self.fetched_resource['users'] = []

        return customer, haulier

    def check_internet_connection(self):
        """checks that device has internet connection and notifies user"""
        word = "Your device does not have internet connection. Please connect to an active network!"

        def run_notification():
            while not func.is_internet_connected():
                self.update_status(' ')
                self.display_word_letter_by_letter(word)
            self.update_status('Internet Connection was restored!')

        if not func.is_internet_connected():
            self.thread_request(run_notification)

        return

    def load_current_user(self, user_id):
        """creates an instance of the current_user class using user data from database server"""
        # get system ip
        data = {}
        data['ip'] = func.get_ip_address()
        data['user_id'] = user_id

        # send a request to server
        worker = Messenger(self.server_url, '/user?action=get-current-user')
        response = worker.query_server(data)

        if response['status'] != 1:
            # log user out
            self.logout_user()

        self.current_user = CurrentUser(response['data'])

        if self.current_user:
            self.update_status(f'welcome {self.current_user.full_name}.')

        return

    def logout_user(self):
        """returns user to login page"""
        # get system ip
        data = {}
        data['ip'] = func.get_ip_address()

        # send a request to server
        worker = Messenger(self.server_url, '/user?action=logout-user')
        worker.query_server(data)

        self.withdraw()
        os.system("python welcome.py")
        self.destroy()
        return

    def run_periodically(self):
        """shots down and starts up ngrok agent every less than 2 hours."""
        if func.is_ngrok_running():
            # shot down ngrok
            self.stop_ngrok(self.ngrok_url)

            # wait for 2 seconds
            time.sleep(2)

        # check if ngrok is running already
        # start ngrok
        self.start_ngrok()

        # wait for a little less than 1hr 40mins then run again
        self.after(6000000, self.run_periodically)


class CurrentUser:
    """class for create a user instance"""
    def __init__(self, user_obj):
        self.full_name = user_obj['full_name']
        self.admin_type = user_obj['admin_type']
        self.email = user_obj['email']
        self.activated = user_obj['activated']
        self.id = user_obj['user_id']
        self.first_name = user_obj['first_name']
        self.last_name = user_obj['last_name']



if __name__ == "__main__":
    gui = Pikanto()
    gui.mainloop()
