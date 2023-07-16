"""This contains functions for specific tasks"""
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk

def create_image_obj(imagepath,size):
    """ This creates a CTkImage object that could be used on any of the app widgets
        It takes two args: imagepath (string)  to image and size (tuple) representing the width and height of image (w,h)
        Returns the image obj
    """
    image = Image.open(imagepath)    
    img = ctk.CTkImage(image,size=size)        
    return img 

def addspace(obj_position,obj_size):
    """Gets the position of the object and then adds up the size of the object to give the position of the point where the span of the obj ended"""
    return obj_position + obj_size    
