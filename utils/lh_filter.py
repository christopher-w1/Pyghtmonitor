from utils.lh_interfacer import Interfacer
from time import sleep, monotonic
class LHFilter:
    def __init__(self, username, token) -> None:
        self.interfacer  = Interfacer(username, token)
        self.rooms       = {}
        self.last_update = {}
        self.controller_keys = []
        self.update()
                
    def update(self):
        new_rooms = self.interfacer.get_rooms(only_responding=True)
        if new_rooms: 
            #print(f"{len(new_rooms)} rooms responding")
            #print(self.last_update)
            
            for room in new_rooms:
                value = new_rooms[room]
                self.rooms[room] = value
                self.last_update[room] = monotonic()
                
    def get_controller_keys(self):
        for room in self.rooms.values():
            if "controller_metrics" in room:
                for metric in room["controller_metrics"]:
                    if (room["controller_metrics"][metric] 
                        and not metric in self.controller_keys):
                        self.controller_keys.append(str(metric))
                        print(metric)
            else:
                print(room)
        print("Keys:", self.controller_keys)
        return self.controller_keys
                
    def time_since_response(self):
        response_times = {}
        current_time   = monotonic()
        for key in self.last_update:
            value = self.last_update[key]
            response_times[key] = current_time - value
        return response_times
    
    def get_metrics(self, metric: str):
        rooms = {}
        
        match metric:
            case "[Controller Active]":
                resplist = self.time_since_response()
                for key in resplist:
                    rooms[key] = True if resplist[key] < 5 else False
            case "[Lamps Per Controller]":
                for key in self.rooms:
                    if "lamp_metrics" in self.rooms[key]:
                        raw_value = self.rooms[key]["lamp_metrics"]
                        rooms[key] = int(len(raw_value)) if raw_value else None
                    else:
                        #print(self.rooms[key].keys())
                        rooms[key] = None#lamp_metrics
            case "[Power Per Lamp]":
                for key in self.rooms:
                    if "power" in self.rooms[key]["controller_metrics"] and "lamp_metrics" in self.rooms[key]:
                        power_value = float(self.rooms[key]["controller_metrics"]["power"])
                        lamp_value = max(float(len(self.rooms[key]["lamp_metrics"])), 1)
                        rooms[key] = power_value / lamp_value
                    else:
                        rooms[key] = None
            case "[API Version]":
                for key in self.rooms:
                    if "api_version" in self.rooms[key]:
                        raw_value = self.rooms[key]["api_version"]
                        rooms[key] = int(raw_value) if raw_value and str(raw_value).isnumeric() else None
                    else:
                        rooms[key] = None
            case _ :
                for key in self.rooms:
                    rooms[key] = None
                    if metric in self.rooms[key]["controller_metrics"]:
                        raw_value = self.rooms[key]["controller_metrics"][metric]
                        try:
                            if raw_value:
                                if str(raw_value).isnumeric():
                                    rooms[key] = int(raw_value)
                                else:
                                    rooms[key] = float(raw_value) 
                        except Exception as e:
                            pass
                    
        return rooms   
     
    def get_min_avg_max(self, param: str):
        metrics = self.get_metrics(param)
        valuelist = []
        min_val   = None
        max_val   = None
        sum       = None
        for val in metrics.values():
            if str(val).isnumeric():
                numval = float(val)
                valuelist.append(numval)
                if not min_val or numval < min_val: min_val = numval
                if not max_val or numval > max_val: max_val = numval
                sum = numval if not sum else sum + numval
        avg = sum/len(valuelist) if sum else None
        return (min_val, avg, max_val)
        
    def blend_colors(self, expected, threshold, value, color1, color2):
        # Berechne den prozentualen Abstand zwischen expected und threshold
        total_distance = threshold - expected
        distance_from_expected = abs(value - expected)
        blend_ratio = distance_from_expected / total_distance

        # Begrenze den Blend-Ratio-Wert zwischen 0 und 1
        blend_ratio = max(0, min(1, blend_ratio))

        # Mische die Farben basierend auf dem Blend-Verhältnis
        blended_color = [
            int(color1[i] * (1 - blend_ratio) + color2[i] * blend_ratio)
            for i in range(3)
        ]

        return tuple(blended_color)

    def stop(self):
        self.interfacer.stop()