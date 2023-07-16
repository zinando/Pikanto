"""This is the main application window module"""
import customtkinter as ctk
from appclasses.labelclass import MyLabel
from appclasses.buttonclass import MyButton
from appclasses.frameclass import MyFrame
from helpers  import myfunctions as func
import os
import time
import random
import serial

class Pikanto(ctk.CTk):
	"""This creates an instance of the Pikanto app main window"""
	def __init__(self):
		super(Pikanto, self).__init__()
		self.port_number = None
		self.status_message = None
		self.unit = "Kg"
		self.weight_data = None		
		self.resizable(False,False)
		width, height = 1000, 600
		self.w,self.h = width, height
		position_x = (self.winfo_screenwidth()//2) - (width//2)
		position_y = (self.winfo_screenheight()//2) - (height//2)
		self.geometry("{}x{}+{}+{}".format(width,height,position_x,position_y))
		self.iconbitmap('assets/icons/app_icon.ico')
		self.title('Pikanto - logistics weight station data manager')
		
		bg_label = MyLabel(self,text="",bg_color="#2f6c60",fg_color="#2f6c60",height=height,width=width).create_obj()
		bg_label.place(x=0,y=0)

		status_report_label_text = MyLabel(self,text="Action Status:",text_color="#6699cc",font_size=14,font="Silkscreen",bg_color="#2f6c60",fg_color="#2f6c60",height=40,width=118).create_obj()
		status_report_label_text.place(x=270,y=10)

		self.update()
		status_report_label = MyLabel(self,text="",text_color="#ffffff",bg_color="#2f6c60",fg_color="#25564c",height=int(status_report_label_text.cget("height"))+10,width=width-280-10-int(status_report_label_text.cget("width"))).create_obj()
		d_x = func.addspace(status_report_label_text.winfo_x(),int(status_report_label_text.cget("width")))
		status_report_label.place(x=d_x+10,y=status_report_label_text.winfo_y()-5)
		self.status_report_display = status_report_label
		
		self.update()
		self.display_label = MyLabel(self,text="",bg_color="#2f6c60",fg_color="#ffffff",height=height-100,width=width-280).create_obj()
		d_y = func.addspace(status_report_label.winfo_y(),int(status_report_label.cget("height")))
		self.display_label.place(x=status_report_label_text.winfo_x(),y=d_y+5)

		self.update()
		self.data_display_label = MyLabel(self,text="0.0 kg",font_size=22,text_color="#2f6c60",bg_color="#ffffff",fg_color="#f5f5f5",height=int(status_report_label.cget("height")),width=int(status_report_label.cget("width"))+40).create_obj()
		d_x = self.display_label.winfo_x() + (int(self.display_label.cget("width")) - 40 - int(status_report_label.cget("width")))/2
		self.data_display_label.place(x=d_x+10,y=self.display_label.winfo_y()+5)


		settings_btn = MyButton(self,text="Settings",command=self.open_settings_form,font_size=16,font_weight="bold",text_color="#000000", bg_color="#2f6c60",fg_color="#6699cc",height=50,width=100).create_obj()
		settings_btn.place(x=20,y=10)

		data_manipulation_btns_label = MyLabel(self,text="",bg_color="#2f6c60",fg_color="#25564c",height=100,width=230).create_obj()
		self.update()
		d_y = func.addspace(settings_btn.winfo_y(),int(settings_btn.cget("height")))
		data_manipulation_btns_label.place(x=settings_btn.winfo_x(),y=d_y+40)
		#buttons
		self.update()
		h = (int(data_manipulation_btns_label.cget("height"))/2)-10
		w = (int(data_manipulation_btns_label.cget("width"))/2)-10
		x = data_manipulation_btns_label.winfo_x()
		y = data_manipulation_btns_label.winfo_y()
		read_data_btn = MyButton(self,text="Read Data",command=self.show_scale_data,font_size=14,text_color="#ffbf00", bg_color="#2f6c60",fg_color="#6699cc",height=h,width=w).create_obj()
		read_data_btn.place(x=x+5,y=y+5)
		
		self.update()
		clear_data_btn = MyButton(self,text="Clear Data",command=self.clear_data,font_size=14,text_color="#ffbf00", bg_color="#2f6c60",fg_color="#6699cc",height=h,width=w).create_obj()
		d_x = read_data_btn.winfo_x() + int(read_data_btn.cget("width")) + 5
		clear_data_btn.place(x=d_x,y=read_data_btn.winfo_y())
		
		self.update()
		record_data_btn = MyButton(self,text="Record Data",command=None,font_size=14,text_color="#ffbf00", bg_color="#2f6c60",fg_color="#6699cc",height=h,width=w).create_obj()
		d_y = read_data_btn.winfo_y() + int(read_data_btn.cget("height")) + 5
		record_data_btn.place(x=read_data_btn.winfo_x(),y=d_y)
		
		self.update()
		view_records_btn = MyButton(self,text="View Records",command=None,font_size=14,text_color="#ffbf00", bg_color="#2f6c60",fg_color="#6699cc",height=h,width=w).create_obj()
		view_records_btn.place(x=clear_data_btn.winfo_x(),y=record_data_btn.winfo_y())



		request_btns_label = MyLabel(self,text="",bg_color="#2f6c60",fg_color="#25564c",height=100,width=230).create_obj()
		self.update()
		d_y = func.addspace(data_manipulation_btns_label.winfo_y(),int(data_manipulation_btns_label.cget("height")))
		request_btns_label.place(x=settings_btn.winfo_x(),y=d_y+40)

		tutorial_btns_label = MyLabel(self,text="",bg_color="#2f6c60",fg_color="#25564c",height=150,width=250).create_obj()
		self.update()
		d_y = func.addspace(request_btns_label.winfo_y(),int(request_btns_label.cget("height")))
		tutorial_btns_label.place(x=settings_btn.winfo_x()-10,y=d_y+40)

		welcome_text = "Welcome to PIKANTO application. Enjoy the ride!"
		self.display_text(welcome_text)
		self.display_data("0.0")


	def show_scale_data(self):
		"""Retrieves the reading on the scale with the set port number"""
		port = '/dev/ttyUSB0' #self.port_number #
		baudrate = 9600
		parity = serial.PARITY_NONE
		stopbits = serial.STOPBITS_ONE
		bytesize = serial.EIGHTBITS

		try:
		    temp = serial.Serial(port, baudrate, bytesize, parity, stopbits)		    
		    # Flush both input/output buffer.
		    temp.reset_input_buffer()
		    temp.reset_output_buffer()
		    temp.close()
		except:			
		    self.update_status('Unable to open/clean ' + port + ':' + str(baudrate))
		    return

		with serial.Serial(port, baud, bytesize, parity, stopbits) as ser:		    	           
			# Only read data if there are bytes already waiting in the buffer.
			if ser.in_waiting > 0:
				time.sleep(0.1)
				#continue
			#We got bytes, read them.
			x = ser.readline()	        
			self.weight_data = None
			time.sleep(0.1)			
			self.weight_data = x
			self.update()
			self.display_data(self.weight_data)
	        #print(x)	            

		

		return
	def update_status(self,message):
		"""Pauses animation message on the status display and displays message"""
		self.status_message = message
		self.status_report_display.configure(text=self.status_message)
		self.update()
		time.sleep(5)
		self.status_report_display.configure(text="")
		self.update()
		self.status_message = None

	def save_settings(self,**kwargs):
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

	def display_data(self,data=None):
		"""Displays data on the data_display label"""		
		self.weight_data = data

		def load_data():			
			self.data_display_label.configure(text="{} {}".format(self.weight_data,self.unit))
			self.update()
		if self.weight_data:
			load_data()
			self.data_display_label.after(300,self.display_data)
		else:
			return		
					

	def open_settings_form(self):
		"""creates a form for setting the scale port number"""		

		self.settings_frame = MyFrame(self,fg_color="gray",height=int(self.display_label.cget("height")),width=int(self.display_label.cget("width")))
		self.update()
		port_field = self.settings_frame.create_entry(height=40,width=230,pht="port number to read data from",x=self.settings_frame.winfo_x()+10,y=self.settings_frame.winfo_y()+20)
		
		d_x = self.settings_frame.winfo_x()+(self.settings_frame.width/2)- 57
		d_y = self.settings_frame.winfo_y()+(self.settings_frame.height)- 50
		save_btn = self.settings_frame.create_button(width=114,height=30,x=d_x,y=d_y,text="Save Settings",bg_color="gray",fg_color="#6699cc",command=lambda:self.save_settings(port_number=port_field.get()))
		
		self.settings_frame.place(x=self.display_label.winfo_x(),y=self.display_label.winfo_y())

		return

	def display_text(self,text=None):
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
					self.status_report_display.configure(text=y+xk[count])
					self.update()
					count += 1
					time.sleep(0.1)
				y = self.status_report_display.cget("text")+" "				
				self.status_report_display.configure(text=y)	

		self.status_report_display.after(5000, self.display_text)	
		 

if __name__ == "__main__":
	app = Pikanto()
	app.mainloop()