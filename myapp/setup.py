import sys
from cx_Freeze import setup, Executable

base = None

#if sys.platform == 'win32':
    #base = 'Win32GUI'

options = {
    'build_exe': {
        "packages": ["tkinter", "customtkinter", "validators", "img2pdf", "reportlab", "fpdf"], #names of packages (directories) to be included in the build
        "includes": [], # names of modules (files) to be included in the build
        'include_files': ['assets', 'static', 'app_settings.json', "ticket_temp.docx", "waybill_temp.docx"],
        # Add the ffg to the build folder:        
        # server/instance/email_template.txt        
    },
}

executables = [
    Executable('welcome.py', base=base, icon='assets/icons/app_icon.ico', target_name='Pikanto.exe'),  # Replace 'your_main_script.py' with your main script
    Executable('main.py', base=base, icon='assets/icons/app_icon.ico', target_name='main.exe'),
]

setup(
    name='Pikanto',
    version='1.0',
    description='A logistics weight management console.',
    options=options,
    executables=executables
)
