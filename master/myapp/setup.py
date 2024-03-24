import sys
from cx_Freeze import setup, Executable

base = None

if sys.platform == 'win32':
    base = 'Win32GUI'

options = {
    'build_exe': {
        "packages": ["tkinter", "customtkinter", "validators", "img2pdf", "reportlab", "fpdf"],
        'include_files': ['assets', 'appclasses', "virtual/Lib/site-packages/validators", 
        'helpers', 'static', 'main.py', 'app_settings.json', 'flask_app.py', 'server', 
        'instance', "ticket_temp.docx", "waybill_temp.docx",
        "virtual/Lib/site-packages/img2pdf.py", "virtual/Lib/site-packages/reportlab", 
        "virtual/Lib/site-packages/fpdf","virtual/Lib/site-packages/jp2.py",
        "virtual/Lib/site-packages/psutil"],  # Add any additional files or data needed here
    },
}

executables = [
    Executable('welcome.py', base=base, icon='assets/icons/app_icon.ico', target_name='PikantoMaster.exe'),  # Replace 'your_main_script.py' with your main script
]

setup(
    name='PikantoMaster',
    version='1.0',
    description='Master- A logistics weight management console.',
    options=options,
    executables=executables
)
