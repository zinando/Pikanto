import sys
from cx_Freeze import setup, Executable

base = None

if sys.platform == 'win32':
    base = 'Win32GUI'

options = {
    'build_exe': {
        "packages": ["tkinter", "customtkinter"],
        'include_files': ['assets', 'appclasses', 'helpers', 'static', 'main.py', 'app_settings.json', 'flask_app.py', 'server', 'instance'],  # Add any additional files or data needed here
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
