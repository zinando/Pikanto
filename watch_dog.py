import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MyHandler(FileSystemEventHandler):
    """class for monitoring my app files for changes and reloads it on file changes"""
    def __init__(self):
        pass

    def on_any_event(self, event):
        if event.is_directory:
            return
        if event.event_type == 'modified' or event.event_type == 'created':
            print(f'Restarting tkinter app due to changes in {event.src_path}')
            subprocess.run(["python", "myapp/main.py"])


if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
