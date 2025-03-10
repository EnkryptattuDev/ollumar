from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import threading
import time

console = Console()

class FancySpinner:
    def __init__(self, message="Processing"):
        self.progress = None
        self.message = message
        self.task_id = None
        
    def start(self):
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[green]{task.description}"),
            console=console
        )
        self.progress.start()
        self.task_id = self.progress.add_task(self.message, total=None)
        
    def update(self, message):
        if self.progress and self.task_id is not None:
            self.progress.update(self.task_id, description=message)
    
    def stop(self):
        if self.progress:
            self.progress.stop()

class Spinner:
    def __init__(self):
        self.spinner = FancySpinner()
        self.running = False
        self.thread = None
        self.callback = None
        self.symbols = [".", "..", "..."]
        self.idx = 0

    def start(self, update_callback):
        self.running = True
        self.callback = update_callback
        self.spinner.start()
        
        def spin():
            while self.running:
                symbol = self.symbols[self.idx % len(self.symbols)]
                self.idx += 1
                if self.callback:
                    self.callback(symbol)
                time.sleep(0.3)
            if self.callback:
                self.callback(" " * 40)
                
        self.thread = threading.Thread(target=spin)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.spinner.stop()
        if self.thread:
            self.thread.join()