"""This is the label class module"""
import customtkinter as ctk


class MyLabel(object):
    """Label class for our application"""

    def __init__(self, master, **kwargs):
        super(MyLabel, self).__init__()
        self.master = master

        self.text = kwargs["text"] if "text" in kwargs else ""
        self.image = kwargs["image"] if "image" in kwargs else None
        self.height = kwargs["height"] if "height" in kwargs else 0
        self.width = kwargs["width"] if "width" in kwargs else 0
        self.bg_color = kwargs["bg_color"] if "bg_color" in kwargs else "#2f6c60"
        self.fg_color = kwargs["fg_color"] if "fg_color" in kwargs else "white"
        self.text_color = kwargs["text_color"] if "text_color" in kwargs else "black"
        self.font = kwargs["font"] if "font" in kwargs else "Segoe UI"
        self.font_size = kwargs["font_size"] if "font_size" in kwargs else 12
        self.font_weight = kwargs["font_weight"] if "font_weight" in kwargs else "normal"
        self.font_style = kwargs["font_style"] if "font_style" in kwargs else "roman"
        self.x = kwargs["x"] if "x" in kwargs else 0
        self.y = kwargs["y"] if "y" in kwargs else 0
        self.corner_radius = kwargs["border_radius"] if "border_radius" in kwargs else None
        self.anchor = kwargs["anchor"] if "anchor" in kwargs else "center"
        self.justify = kwargs["justify"] if "justify" in kwargs else "center"
        self.cursor = kwargs["cursor"] if "cursor" in kwargs else "arrow"

    def create_obj(self):
        """Creates the label object and returns it"""
        lab = ctk.CTkLabel(self.master, text=self.text, text_color=self.text_color, fg_color=self.fg_color,
                           image=self.image, bg_color=self.bg_color, height=self.height, width=self.width,
                           corner_radius=self.corner_radius, anchor=self.anchor, justify=self.justify,
                           cursor=self.cursor)
        lab.cget("font").configure(family=self.font, size=self.font_size, weight=self.font_weight,
                                   slant=self.font_style)
        lab.position_x = self.x
        lab.position_y = self.y
        return lab
