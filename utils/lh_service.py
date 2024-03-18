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
        
        total_distance = threshold - expected
        distance_from_expected = abs(value - expected)
        blend_ratio = distance_from_expected / total_distance

        blend_ratio = max(0, min(1, blend_ratio))

        blended_color = [
            int(color1[i] * (1 - blend_ratio) + color2[i] * blend_ratio)
            for i in range(3)]
        
        #max_brightness = (max(blended_color) + 255)//2
        for i in range(3):
            blended_color[i] = min(255, blended_color[i]) #* 255 // max_brightness)
        
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
                    color = self.blend_colors(prange[0], prange[1], value, self.color1, self.color2)
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
        p_range = self.config["paramrange"][param]
        return (param, p_range)
    
    def stop(self):
        self.filter.stop()
        
    def min_avg_max_len(self, metrics: dict):
        valuelist = []
        min_val   = None
        max_val   = None
        sum       = None
        for val in metrics.values():
            if str(val).replace(".", "").isnumeric():
                numval = float(val)
                valuelist.append(numval)
                if not min_val or numval < min_val: min_val = numval
                if not max_val or numval > max_val: max_val = numval
                sum = numval if not sum else sum + numval
            #else:
            #    print(val, "is not numeric")
        avg = sum/len(valuelist) if sum else None
        return (str(min_val)[:5], str(avg)[:5], str(max_val)[:5], len(valuelist), len(metrics))
    
    def run(self):
        #print("Test")
        self.keep_running = True
        while self.keep_running:
            self.refresh_config()
            param, param_range = self.param_and_range()
            #print("Parameter: ", param)
            self.filter.update()
            controller_metrics = self.filter.get_metrics(param)
            if controller_metrics:
                #print(controller_metrics)
                matrix = self.filled_matrix(param_range, controller_metrics)
                stats  = self.min_avg_max_len(controller_metrics)
                self.framequeue.put([matrix, stats])
                
            self.keep_running = self.config["keep_running"]
            
            sleep(self.interval)
        self.stop()