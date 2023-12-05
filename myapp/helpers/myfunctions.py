"""This contains functions for specific tasks"""
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import serial
import time
from appclasses.file_class import FileHandler
import re


def notify_user(msg=None):
    """ Pops a message when there is need to. Message to be displayed can be given as an arg """
    if msg is None:
        messagebox.showinfo("Alert!", f"I am a message button.")
    else:
        messagebox.showinfo("Alert!", "{}".format(msg))


def create_image_obj(imagepath, size):
    """ This creates a CTkImage object that could be used on any of the app widgets
        It takes two args: imagepath (string)  to image and size (tuple) representing the width and height of image (w,h)
        Returns the image obj
    """
    image = Image.open(imagepath)
    img = ctk.CTkImage(image, size=size)
    return img


def save_files_to_app(filepath, location):
    """saves files to the user's app directory"""
    handler = FileHandler(filepath)
    response = handler.save_file(location)
    if response:
        notify_user('file saved successfully!')
    else:
        notify_user('Operation was not successful.')

    return


def addspace(obj_position, obj_size):
    """Gets the position of the object and then adds up the size of the object to give the position of the point where the span of the obj ended"""
    return obj_position + obj_size


def get_mass():
    # ser = serial.Serial(port='/dev/ttyS0', ## if using Linux serial
    ser = serial.Serial("COM3",
                        baudrate=9600,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS
                        )

    if not ser.isOpen():
        ser.open()

    ser.write(b'\nSI\n')
    time.sleep(1)  # give moment for balance to settle

    value = ser.read(ser.in_waiting)

    value = decode_byte(value)

    if ser.isOpen():
        ser.close()

    return value


def decode_byte(byte_value):
    """Decodes the bytes data gotten from the scale """

    x = str(byte_value).split("'")
    x = x[1].split("\\")
    new_x = x[5:-3]
    k = ''
    for w in new_x:
        k += w[2:]
    return k


def is_valid_email(email: str) -> bool:
    """
    Checks if the given string is a valid email address.
    Returns True if it's a valid email, False otherwise.
    """
    # Regular expression pattern for validating an email address
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    # Using the re.match function to check if the email matches the pattern
    if re.match(email_pattern, email):
        return True
    else:
        return False
