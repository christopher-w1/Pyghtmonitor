import json, threading, queue
from utils.lh_filter import LHFilter
from time import sleep
from utils.lh_mapper import WindowMapper

class BackgroundService(threading.Thread):
    def __init__(self, framequeue: queue.Queue, interval = 1.0) -> None:
        self.framequeue = framequeue
        self.interval = interval
        self.config = {}
        self.refresh_config()
        self.filter = LHFilter(self.config["user"], self.config["token"])
        self.keep_running = True
        self.mapper = WindowMapper()
        self.mapper.read_yaml()
        self.controller_keys = []
        
    def grey_matrix(self):
        matrix = []
        for y in range(14):
            ls = []
            for x in range(28):
                ls.append((127, 127, 127))
            matrix.append(ls)
        return matrix
    
    def blend_colors(self, expected, threshold, value, color1, color2):
        
        if not value:
            return (127,127,144)
        
        expected = float(expected)
        threshold = float(threshold)
        value = float(value)
        
        if value < expected:
            inverted = []
            for i in range(len(color2)):
                inverted.append(255-color2[i])
            color2 = inverted
        
        total_distance = threshold - expected
        
        if total_distance == 0: return color1
        
        distance_from_expected = abs(value - expected)
        blend_ratio = distance_from_expected / total_distance

        blend_ratio = max(0, min(1, blend_ratio))

        blended_color = [
            int(color1[i] * (1 - blend_ratio) + color2[i] * blend_ratio)
            for i in range(3)]
        
        for i in range(3):
            blended_color[i] = min(255, blended_color[i])
        
        return tuple(blended_color)
    
    def filled_matrix(self, prange: list, metrics: dict):
        matrix = []
                
        for y in range(14):
            ls = []
            for x in range(28):
                color = (32, 32, 32)
                controllers = self.mapper.map_controllers()
                room = controllers[y][x]
                if room in metrics:
                    value = metrics[room]
                    if prange[0] != prange[1]:
                        color = self.blend_colors(prange[0], prange[1], value, self.color1, self.color2)
                    else:
                        color = self.color1
                ls.append(color)
            matrix.append(ls)
        return matrix
    
    def load_from_file(self, filename="appconfig.json"):
        data = {}
        try:
            with open(filename, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            print(f"File {filename} not found.")
        return data
    
    def refresh_config(self):
        try:
            self.config = self.load_from_file()
                
            match self.config["color_gradient"]:
                case "Blue->Red":
                    self.color1 = (0, 0, 255)
                    self.color2 = (255, 0, 0)
                case "Green->Blue":
                    self.color1 = (0, 255, 0)
                    self.color2 = (0, 0, 255)
                case _:
                    self.color1 = (0, 255, 0)
                    self.color2 = (255, 0, 0)
        except Exception as e:
            print(e)
            
    def param_and_range(self):
        param = self.config["parameter"]
        if param in self.config["paramrange"]:
            p_range = self.config["paramrange"][param]
        else:
            print(f"ERROR: Parameter {param} has no range!\n Using standard Range of 0..50")
            p_range = [0, 50]
        return (param, p_range)
    
    def stop(self):
        self.filter.stop()
        
    def shorten(self, number):
        if number.isnumeric():
            return number
        intlength = 0
        for char in number:
            if char.isnumeric():
                intlength += 1
            else:
                break
        maxlength = len(number)
        for i in range(len(number), 0):
            if number[i] == 0:
                maxlength = i-1
                break
        new_length = min(intlength+3, maxlength)
        return number[:new_length]
        
    def min_avg_max_len(self, metrics: dict):
        valuelist = []
        min_val   = None
        max_val   = None
        sum       = None
        for val in metrics.values():
            if str(val).replace(".", "").isnumeric():
                numval = float(val) if str(val).replace(".", "").isnumeric() else 0
                valuelist.append(numval)
                if not min_val or numval < min_val: min_val = numval
                if not max_val or numval > max_val: max_val = numval
                sum = numval if not sum else sum + numval
            
        avg = sum/len(valuelist) if sum else None
        return (self.shorten(str(min_val)), self.shorten(str(avg)), self.shorten(str(max_val)), len(valuelist), len(metrics))
    
    def run(self):
        self.keep_running = True
        while self.keep_running:
            self.refresh_config()
            param, param_range = self.param_and_range()
            self.filter.update()
            controller_metrics = self.filter.get_metrics(param)
            if self.controller_keys == []:
                self.controller_keys = self.filter.get_controller_keys()
            if controller_metrics:
                matrix = self.filled_matrix(param_range, controller_metrics)
                stats  = self.min_avg_max_len(controller_metrics)
                responding = controller_metrics.keys()
                self.framequeue.put([matrix, stats, responding, self.controller_keys])
            self.keep_running = self.config["keep_running"]
            sleep(self.interval)
        self.stop()