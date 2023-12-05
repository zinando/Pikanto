"""Customtkinter toplevel class module"""
import customtkinter as ctk


class DialogueBox(ctk.CTkToplevel):
    """Class for creating toplevel window for dialogue with app users"""

    def __init__(self, width, height, **kwargs):
        super().__init__(**kwargs)
        self.geometry("{}x{}".format(width, height))
        self.configure(fg_color=kwargs['fg_color'])
        self.width = width
        self.height = height


