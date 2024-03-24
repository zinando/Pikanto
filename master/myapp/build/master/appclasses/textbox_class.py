"""This is the textbox class module"""
import customtkinter as ctk


class MyTexBox(object):
    """Creates a button instance for Pikanto app"""

    def __init__(self, master, **kwargs):
        super(MyTexBox, self).__init__()
        self.master = master

        self.text = kwargs["text"] if "text" in kwargs else ""
        self.image = kwargs["image"] if "image" in kwargs else None
        self.height = kwargs["height"] if "height" in kwargs else 0
        self.command = kwargs["command"] if "command" in kwargs else None
        self.width = kwargs["width"] if "width" in kwargs else 0
        self.bg_color = kwargs["bg_color"] if "bg_color" in kwargs else "#2f6c60"
        self.fg_color = kwargs["fg_color"] if "fg_color" in kwargs else "white"
        self.text_color = kwargs["text_color"] if "text_color" in kwargs else "black"
        self.font = kwargs["font"] if "font" in kwargs else "Segoe UI"
        self.font_size = kwargs["font_size"] if "font_size" in kwargs else 12
        self.font_weight = kwargs["font_weight"] if "font_weight" in kwargs else "normal"
        self.x = kwargs["x"] if "x" in kwargs else 0
        self.y = kwargs["y"] if "y" in kwargs else 0
        self.corner_radius = kwargs["border_radius"] if "border_radius" in kwargs else 5

    def create_obj(self):
        """Creates the button object and returns it"""
        box = ctk.CTkTextbox(self.master, text_color=self.text_color, fg_color=self.fg_color,
                             bg_color=self.bg_color, height=self.height, width=self.width,
                             corner_radius=self.corner_radius, border_width=0,
                             font=(self.font, self.font_size, self.font_weight))
        box.insert("0.0", self.text)

        box.position_x = self.x
        box.position_y = self.y

        return box
