import tkinter as tk
import json, threading, queue
from tkinter import ttk
from utils.lh_service import BackgroundService
from time import sleep

preset = {
    "user": "",
    "token": "",
    "parameter": "responding",
    "paramlist": ["responding", "api_version", "core_temperature", "voltage", "current"],
    "paramrange": {
        "responding": [0, 1],
        "api_version": [1, 2],
        "core_temperature": [20.0, 50.0],
        "voltage": [10.0, 14.0], 
        "current": [0.0, 1.2]
    },
    "color_gradient": "Green->Red",
    "show_api": "All",
    "keep_running": "False"
}

def save_to_file(data, filename="appconfig.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def load_from_file(filename="appconfig.json"):
    data = {}
    try:
        with open(filename, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"File {filename} not found.")
    return data


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.scale_y = 32
        self.scale_x = 15

        self.canvas = tk.Canvas(self, width=29*self.scale_x, height=15*self.scale_y, bg="white")
        self.canvas.grid(row=0, column=0, padx=10, pady=10, rowspan=11, columnspan=1, sticky="ns")

        self.update_canvas()

        frame = tk.Frame(self)
        frame.grid(row=0, column=1, padx=10, pady=10)
        
        #default_font = frame.font.nametofont("TkDefaultFont")
        #bold_font = default_font.copy()
        #bold_font.configure(weight="bold")
        bold_font = ("Helvetica", 10, "bold")

        ttk.Label(frame, text="Parameter").grid(row=0, column=1, padx=5, pady=5)
        self.dropdown1 = ttk.Combobox(frame, values=["responding", "api_version", "core_temperature", "voltage", "current"])
        self.dropdown1.grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(frame, text="Show Version").grid(row=1, column=1, padx=5, pady=5)
        self.dropdown2 = ttk.Combobox(frame, values=["All", "1", "2"])
        self.dropdown2.grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(frame, text="Color Gradient").grid(row=2, column=1, padx=5, pady=5)
        self.dropdown3 = ttk.Combobox(frame, values=["Blue->Red", "Green->Red", "Green->Blue"])
        self.dropdown3.grid(row=2, column=2, padx=5, pady=5)

        ttk.Label(frame, text="Value Low").grid(row=3, column=1, padx=5, pady=5)
        self.input1 = ttk.Entry(frame)
        self.input1.grid(row=3, column=2, padx=5, pady=5)

        ttk.Label(frame, text="Value High").grid(row=4, column=1, padx=5, pady=5)
        self.input2 = ttk.Entry(frame)
        self.input2.grid(row=4, column=2, padx=5, pady=5)

        separator = ttk.Separator(frame, orient='horizontal')
        separator.grid(row=5, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Label(frame, text="User", font=bold_font).grid(row=6, column=1, columnspan=2, padx=5, pady=5)
        self.input3 = ttk.Entry(frame)
        self.input3.grid(row=7, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        ttk.Label(frame, text="API-Token", font=bold_font).grid(row=8, column=1, columnspan=2, padx=5, pady=5)
        self.input4 = ttk.Entry(frame, show="•")
        self.input4.grid(row=9, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        
        separator = ttk.Separator(frame, orient='horizontal')
        separator.grid(row=10, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.output_text = tk.Text(frame, wrap="word", width=30, height = 8)
        self.output_text.grid(row=11, column=1, columnspan=2, rowspan=1, sticky="nsew", padx=5, pady=5)
        
        separator = ttk.Separator(frame, orient='horizontal')
        separator.grid(row=12, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        
        start_button = ttk.Button(frame, text="Start Monitoring", command=self.start_service)
        start_button.grid(row=14, column=1, columnspan=1, sticky="esw", padx=20, pady=5)
        
        stop_button = ttk.Button(frame, text="Stop Monitoring", command=self.stop_service)
        stop_button.grid(row=14, column=2, columnspan=1, sticky="esw", padx=20, pady=5)
        

        
        #save_to_file(preset)
        self.settings = preset
        self.load_settings()
        
                # Callbacks für Dropdown-Menüs
        self.dropdown1.bind("<<ComboboxSelected>>", self.on_dropdown1_change)
        self.dropdown2.bind("<<ComboboxSelected>>", self.on_dropdown2_change)
        self.dropdown3.bind("<<ComboboxSelected>>", self.on_dropdown3_change)

        # Callbacks für Textboxen
        self.input1.bind("<FocusOut>", self.on_input1_change)
        self.input2.bind("<FocusOut>", self.on_input2_change)
        self.input3.bind("<FocusOut>", self.on_input3_change)
        self.input4.bind("<FocusOut>", self.on_input4_change)
        
        self.framequeue = queue.Queue()
        self.service = None
        self.monitoring = True
        
    def put_text(self, message, delete=False):
        # Hier kannst du den Text hinzufügen, den du ausgeben möchtest
        if delete: self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, f"{message}\n")

        
    def load_settings(self):
        conf = load_from_file()
        if conf: self.settings = conf
        else: save_to_file(preset)
        self.set_gui_values()

    def update_canvas(self, matrix=None):
        xoff = self.scale_x / 2 + 2
        yoff = self.scale_y / 2
        colors = ["#FFFFFF", "#000000"]  # white and black
        
        self.canvas.delete("all")
        self.canvas.create_rectangle(xoff/2, yoff/2, 28*self.scale_x+xoff*1.5, 15*self.scale_y+yoff, fill="#ccc", outline="")

        for j in range(14):
            for i in range(28):
                x = i * self.scale_x + xoff
                y = j * self.scale_y + yoff
                color = "#%02x%02x%02x" % (127, 127, 127)
                if matrix:
                    color = "#%02x%02x%02x" % matrix[j][i]
                self.canvas.create_rectangle(x, y, x+self.scale_x-1, y+0.5*self.scale_y-1, fill=color, outline="")
    
    def update_queue_content(self):
        try:
            # Versuche, den Inhalt der Queue abzurufen
            matrix, stats = self.framequeue.get_nowait()
            valmax, avg, valmix, n_sens, roomnum = stats
            self.put_text(f"Min:     {valmax} \nAverage: {avg} \nMax:     {valmix} \nSensors: {n_sens}\nActive Controllers: {roomnum}", delete=True)
            self.update_canvas(matrix)
            
        except queue.Empty:
            # Wenn die Queue leer ist, setze den Text entsprechend
            self.put_text("Waiting for input data...")
        finally:
            # Führe diese Funktion erneut nach 1000 Millisekunden (1 Sekunde) aus
            if self.monitoring:
                self.after(1000, self.update_queue_content)
            else:
                self.put_text("Background service stopped.")
                
    def update_config(self):
        pass
    
    def set_gui_values(self):
        self.dropdown1.set(self.settings["parameter"])
        self.dropdown2.set(self.settings["show_api"])
        self.dropdown3.set(self.settings["color_gradient"])
        self.input1.delete(0, tk.END)
        self.input2.delete(0, tk.END)
        self.input3.delete(0, tk.END)
        self.input4.delete(0, tk.END)
        self.input1.insert(0, self.settings["paramrange"][self.settings["parameter"]][0])
        self.input2.insert(0, self.settings["paramrange"][self.settings["parameter"]][1])
        self.input3.insert(0, self.settings["user"])
        self.input4.insert(0, self.settings["token"])
        
    def update_param_range(self):
        self.input1.insert(0, self.settings["paramrange"][self.settings["parameter"]][0])
        self.input2.insert(0, self.settings["paramrange"][self.settings["parameter"]][1])
        
    def on_dropdown1_change(self, event):
        new_value = self.dropdown1.get()
        self.settings["parameter"] = new_value
        self.set_gui_values()
        save_to_file(self.settings)

    def on_dropdown2_change(self, event):
        new_value = self.dropdown2.get()
        self.settings["show_api"] = new_value
        self.set_gui_values()
        save_to_file(self.settings)

    def on_dropdown3_change(self, event):
        new_value = self.dropdown3.get()
        self.settings["color_gradient"] = new_value
        self.set_gui_values()
        save_to_file(self.settings)

    def on_input1_change(self, event):
        new_value = self.input1.get()
        if new_value != self.settings["paramrange"][self.settings["parameter"]][1]:
            self.settings["paramrange"][self.settings["parameter"]][0] = new_value
            self.set_gui_values()
            save_to_file(self.settings)

    def on_input2_change(self, event):
        new_value = self.input2.get()
        if new_value != self.settings["paramrange"][self.settings["parameter"]][0]:
            self.settings["paramrange"][self.settings["parameter"]][1] = new_value
            self.set_gui_values()
            save_to_file(self.settings)

    def on_input3_change(self, event):
        new_value = self.input3.get()
        self.settings["user"] = new_value
        self.set_gui_values()
        save_to_file(self.settings)

    def on_input4_change(self, event):
        new_value = self.input4.get()
        self.settings["token"] = new_value
        self.set_gui_values()
        save_to_file(self.settings)
        
    def start_service(self):
        self.monitoring = True
        self.settings["keep_running"] = True
        save_to_file(self.settings)
        self.framequeue = queue.Queue()
        self.service = BackgroundService(self.framequeue)
        self.thread = threading.Thread(target=self.service.run)
        self.thread.start()  # Thread starten
        self.put_text("Background service started successfully.")
        self.update_queue_content()
        
    def stop_service(self):
        self.monitoring = False
        self.settings["keep_running"] = False
        self.put_text("Terminating service...")
        save_to_file(self.settings)

if __name__ == "__main__":
    app = GUI()
    app.mainloop()