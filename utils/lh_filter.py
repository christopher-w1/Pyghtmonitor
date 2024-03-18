from utils.lh_interfacer import Interfacer
from time import sleep, monotonic
class LHFilter:
    def __init__(self, username, token) -> None:
        self.interfacer  = Interfacer(username, token)
        self.rooms       = {}
        self.last_update = {}
        self.update()
        
    def update(self):
        new_rooms = self.interfacer.get_rooms(only_responding=True)
        if new_rooms: 
            #print(f"{len(new_rooms)} rooms responding")
            #print(self.last_update)
            
            for key in new_rooms:
                value = new_rooms[key]
                self.rooms[key] = value
                self.last_update[key] = monotonic()
                
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
            case "responding":
                resplist = self.time_since_response()
                for key in resplist:
                    rooms[key] = True if resplist[key] < 5 else False
            case "api_version":
                for key in self.rooms:
                    rooms[key] = self.rooms[key]["apiversion"]
            case "core_temperature":
                for key in self.rooms:
                    #print(self.rooms[key]["controllermetrics"])
                    if "coretemperature" in self.rooms[key]["controllermetrics"]:
                        rooms[key] = float(self.rooms[key]["controllermetrics"]["coretemperature"][:5])
                    elif "temperature" in self.rooms[key]["controllermetrics"]:
                        rooms[key] = float(self.rooms[key]["controllermetrics"]["temperature"]) + 20 if float(self.rooms[key]["controllermetrics"]["temperature"]) != 0 else None
                    else:
                        rooms[key] = None
            case "voltage":
                for key in self.rooms:
                    #print(self.rooms[key]["controllermetrics"])
                    if "voltage" in self.rooms[key]["controllermetrics"]:
                        raw_value = self.rooms[key]["controllermetrics"]["voltage"]#[:2] + "." + self.rooms[key]["controllermetrics"]["current"][2:4]
                        rooms[key] = float(raw_value)
                    else:
                        rooms[key] = None
            case "current":
                for key in self.rooms:
                    #print(self.rooms[key]["controllermetrics"])
                    if "current" in self.rooms[key]["controllermetrics"]:
                        raw_value = self.rooms[key]["controllermetrics"]["current"]#[:1] + "." + self.rooms[key]["controllermetrics"]["current"][1:4]
                        rooms[key] = float(raw_value)
                    else:
                        rooms[key] = None
            case "power":
                for key in self.rooms:
                    if "power" in self.rooms[key]["controllermetrics"]:
                        raw_value = self.rooms[key]["controllermetrics"]["power"]
                        rooms[key] = float(raw_value) if raw_value else None
                    else:
                        rooms[key] = None
            case "board_temperature":
                for key in self.rooms:
                    if "boardtemperature" in self.rooms[key]["controllermetrics"]:
                        raw_value = self.rooms[key]["controllermetrics"]["boardtemperature"]
                        rooms[key] = float(raw_value) if raw_value else None
                    else:
                        rooms[key] = None
            case "ping":
                for key in self.rooms:
                    if "pinglatencyms" in self.rooms[key]["controllermetrics"]:
                        raw_value = self.rooms[key]["controllermetrics"]["pinglatencyms"]
                        rooms[key] = float(raw_value) if raw_value else None
                    else:
                        #print(self.rooms[key]["controllermetrics"])
                        rooms[key] = None
            case "n_lamps":
                for key in self.rooms:
                    if "lampmetrics" in self.rooms[key]:
                        raw_value = len(self.rooms[key]["lampmetrics"])
                        rooms[key] = float(raw_value) if raw_value else None
                    else:
                        #print(self.rooms[key].keys())
                        rooms[key] = None#lamp_metrics
            case "power/lamps":
                for key in self.rooms:
                    if "power" in self.rooms[key]["controllermetrics"] and "lampmetrics" in self.rooms[key]:
                        power_value = float(self.rooms[key]["controllermetrics"]["power"])
                        lamp_value = max(float(len(self.rooms[key]["lampmetrics"])), 1)
                        rooms[key] = power_value / lamp_value
                    else:
                        rooms[key] = None
            case _ :
                for key in self.rooms:
                    rooms[key] = None
                    
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
        
if __name__ == "__main__":
    name = "chris1234"
    token = "API-TOK_N/9u-eYpU-zTr0-bZDf-20s3"
    filt = LHFilter(name, token)
    for _ in range(10):
        filt.update()
        print(filt.get_metrics("voltage"))
        sleep(1)