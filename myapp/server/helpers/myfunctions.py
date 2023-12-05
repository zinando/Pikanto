"""This contains functions for specific tasks"""
from appclass.file_class import FileHandler


def save_files_to_app(filepath, location):
    """saves files to the user's app directory"""
    handler = FileHandler(filepath)
    response = handler.save_file(location)
    if response:
        message = 'file saved successfully!'
        status = 1
    else:
        status = 2
        message = 'Operation was not successful.'

    return {'status': status, 'data': None, 'message': message, 'error': None}
