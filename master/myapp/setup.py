import sys
from cx_Freeze import setup, Executable

base = None

#if sys.platform == 'win32':
    #base = 'Win32GUI'

options = {
    'build_exe': {
        "packages": ["tkinter", "customtkinter", "validators", "img2pdf", "reportlab", "fpdf", "sqlite"],
        "includes": [],
        'include_files': ['assets', 'static', 'app_settings.json',
        "ticket_temp.docx", "waybill_temp.docx"]
        # Add the ffg to the build folder:
        # lib/server/config.py
        # server/instance/email_template.txt
        # var/server.extensions-instance/pikanto_db.sqlite

    },
}

executables = [
    Executable('welcome.py', base=base, icon='assets/icons/app_icon.ico', target_name='PikantoMaster.exe'),  # Replace 'your_main_script.py' with your main script
    Executable('main.py', base=base, icon='assets/icons/app_icon.ico', target_name='main.exe'),
    Executable('flask_app.py', base=base, icon='assets/icons/app_icon.ico', target_name='flask_app.exe'),    
]

setup(
    name='PikantoMaster',
    version='1.0',
    description='Master- A logistics weight management console.',
    options=options,
    executables=executables
)
