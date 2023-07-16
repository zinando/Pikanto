"""This is the top level frame class module"""
import tkinter as tk
import customtkinter as ctk 
from appclasses.buttonclass import MyButton
from appclasses.labelclass import MyLabel


class MyFrame(ctk.CTkFrame):
	"""Top level frame class for Pikanto application"""
	def __init__(self, master, **kwargs):		
		super().__init__(master, **kwargs)				
		self.height = kwargs["height"] if "height" in kwargs else 400
		self.width = kwargs["width"] if "width" in kwargs else 400
		self.fg_color = kwargs["fg_color"] if "fg_color" in kwargs else "white"
		self.border_color = kwargs["border_color"] if "border_color" in kwargs else "gray"
		self.border_width = kwargs["border_width"] if "border_width" in kwargs else 2
		self.bg_color = kwargs["bg_color"] if "bg_color" in kwargs else "gray"
		
		#add widgets here
	def create_entry(self,**kwargs):
		"""Creates an entry widget for the Frame"""
		width = kwargs["width"] if "width" in kwargs else self.width
		height = kwargs["height"] if "height" in kwargs else self.height
		text_var = kwargs["text_var"] if "text_var" in kwargs else tk.StringVar()
		pht = kwargs["pht"] if "pht" in kwargs else None #placeholder_text
		state = kwargs["state"] if "state" in kwargs else "normal"
		x = kwargs["x"] if "x" in kwargs else 0
		y = kwargs["y"] if "y" in kwargs else 0
		
		entry = ctk.CTkEntry(self,height=height,width=width,corner_radius=0,placeholder_text=pht,state=state)
		entry.place(x=x,y=y)
		return entry

	def create_button(self,**kwargs):
		"""Creates a button widget for the Frame"""	
		width = kwargs["width"] if "width" in kwargs else self.width/4
		height = kwargs["height"] if "height" in kwargs else self.height/4
		text = kwargs["text"] if "text" in kwargs else "" 				
		x = kwargs["x"] if "x" in kwargs else 0
		y = kwargs["y"] if "y" in kwargs else 0
		image = kwargs["image"] if "image" in kwargs else None		
		command = kwargs["command"] if "command" in kwargs else None						
		bg_color = kwargs["bg_color"] if "bg_color" in kwargs else "#2f6c60"
		fg_color = kwargs["fg_color"] if "fg_color" in kwargs else "white"
		text_color = kwargs["text_color"] if "text_color" in kwargs else "black"
		font = kwargs["font"] if "font" in kwargs else "Segoe UI"
		font_size = kwargs["font_size"] if "font_size" in kwargs else 12
		font_weight = kwargs["font_weight"] if "font_weight" in kwargs else "normal"

		save_button = MyButton(self,text=text,command=command,font_size=font_size,font_weight=font_weight,text_color=text_color, bg_color=bg_color,fg_color=fg_color,height=height,width=width).create_obj()
		save_button.place(x=x,y=y)

		return save_button

	def create_label(self,**kwargs):
		"""Creates a labe widget for the Frame"""
		width = kwargs["width"] if "width" in kwargs else self.width
		height = kwargs["height"] if "height" in kwargs else self.height
		text = kwargs["text"] if "text" in kwargs else "" 				
		x = kwargs["x"] if "x" in kwargs else 0
		y = kwargs["y"] if "y" in kwargs else 0
		image = kwargs["image"] if "image" in kwargs else None		
		command = kwargs["command"] if "command" in kwargs else None						
		bg_color = kwargs["bg_color"] if "bg_color" in kwargs else "#2f6c60"
		fg_color = kwargs["fg_color"] if "fg_color" in kwargs else "white"
		text_color = kwargs["text_color"] if "text_color" in kwargs else "black"
		font = kwargs["font"] if "font" in kwargs else "Segoe UI"
		font_size = kwargs["font_size"] if "font_size" in kwargs else 12
		font_weight = kwargs["font_weight"] if "font_weight" in kwargs else "normal"

		lab = MyLabel(self, text=text,text_color=text_color,fg_color=fg_color, image = image, bg_color=bg_color, height=height, width=width).create_obj()
		lab.place(x=x,y=y)
		return lab