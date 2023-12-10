"""This contains functions for specific tasks"""
from server.appclass.file_class import FileHandler


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


def process_mass(obj) -> dict:
    """processes the mass data in the obj"""
    initial_mass = obj.initial_weight
    final_mass = obj.final_weight

    mr = {}
    if final_mass:
        # check which is larger
        if initial_mass < final_mass:
            mr['tare_mass'] = f"{initial_mass} | {obj.initial_time.strftime('%A, %dth of %B, %Y  %I:%M:%S %p')}"
            mr['gross_mass'] = f"{final_mass} | {obj.final_time.strftime('%A, %dth of %B, %Y  %I:%M:%S %p')}"
            mr['net_mass'] = f"{final_mass - initial_mass}"
        else:
            mr['tare_mass'] = f"{final_mass} | {obj.final_time.strftime('%A, %dth of %B, %Y  %I:%M:%S %p')}"
            mr['gross_mass'] = f"{initial_mass} | {obj.initial_time.strftime('%A, %dth of %B, %Y  %I:%M:%S %p')}"
            mr['net_mass'] = f"{initial_mass - final_mass}"
    else:
        mr['tare_mass'] = f"{initial_mass} | {obj.initial_time.strftime('%A, %dth of %B, %Y  %I:%M:%S %p')}"
        mr['gross_mass'] = ""
        mr['net_mass'] = ""

    return mr
