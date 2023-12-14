"""Customtkinter toplevel class module"""
import customtkinter as ctk
import tkinter as tk


class DialogueBox(ctk.CTkToplevel):
    """Class for creating toplevel window for dialogue with app users"""

    def __init__(self, width, height, **kwargs):
        super().__init__(**kwargs)
        #self.geometry("{}x{}".format(width, height))
        screen_width, screen_height = self.get_screen_resolution()
        self.geometry(f"{width}x{height}+{int((screen_width - width) / 2)}+{int((screen_height - height) / 2)}")
        self.configure(fg_color=kwargs['fg_color'])
        self.width = width
        self.height = height


    def get_screen_resolution(self):
        # Create a hidden Tkinter window to access screen information
        root = tk.Tk()
        root.attributes('-alpha', 0)  # Hide the window

        # Get the screen width and height in pixels
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        root.destroy()

        return screen_width, screen_height


