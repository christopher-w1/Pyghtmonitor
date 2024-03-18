import re

class NotQuiteJson:
    class JsonStruct:
        def __init__(self, type, parent=None) -> None:
            self.type   = type
            self.parent = parent
            self.keys   = []
            self.values = []
            
        def build(self):
            if self.type == dict:
                data = {}
                for k, v in zip(self.keys, self.values):
                    data[k] = v
            elif self.type == list:
                data = self.values
            else:
                data = "".join(self.values)
                if data.isnumeric() and False:
                    if not "." in data:
                        data = int(data)
                    else:
                        data = float(data)
                else: 
                    match data.lower():
                        case "false":
                            data = False
                        case "true":
                            data = True
                        case "none":
                            data = None
            return data
            
        def append_val(self, value):
            self.values.append(value)
            
        def append_key(self, key):
            self.keys.append(key)
                
        def is_string(self):
            return self.type == str
        
        def __repr__(self):
            if self.type == dict:
                return f"[Ks: ({self.keys}) Vs: ({self.values})]"
            elif self.type == list:
                return f"[Le:{str(self.values)}]"
            else:
                st = "".join(self.values)
                return f"[Str:{ st }]"
            
    def __init__(self, debug=False) -> None:
        self.debug = debug
        
    def parseIter(self, source_data: str):
        source_data  = source_data.replace("{}", "None").replace("[]", "None").replace("''", "None").replace('""', "None")
        stack = [self.JsonStruct(type=dict)]
        try:
            for char in source_data:
                match char:
                    case "{":
                        # new dict
                        stack.append(self.JsonStruct(type=dict, parent=stack[-1]))
                    case "[":
                        # new list
                        stack.append(self.JsonStruct(type=list, parent=stack[-1]))
                    case ":":
                        # key ends
                        key = stack.pop().build()
                        # Make sure the key is a string
                        stack[-1].append_key(str(key))
                    case _  :
                        # is a string
                        if char.isalnum() or char==".":
                            if not stack[-1].is_string():
                                # Initialize new string if necessary
                                stack.append(self.JsonStruct(type=str, parent=stack[-1]))
                            # add char to current string
                            stack[-1].append_val(char)
                            
                        elif char in ["]", "}", ","]:
                            if len(stack) < 3:
                                print("End of struct list reached. Bracket Mismatch?")
                                return stack[-1].build()
                            # End of child structure. Pop from stack and add ref to parent
                            value = stack.pop().build() # Converts object class to data structure
                            parent = stack[-1]
                            if self.debug: print(f"Inserting {type(value)} '{value}' \nin {type(parent)} '{parent}'")
                            if not type(parent) == self.JsonStruct:
                                print(f"MISMATCH: Expected JsonStruct, got {type(parent)}")
                                break
                            else:
                                parent.append_val(value)
        except Exception as e:
            print("ERROR: ", e)
            print(char, stack)
        return stack[-1].build()


"""data_string = "{'REID': 0, 'RNUM': 200, 'RESPONSE': 'OK', 'PAYL': {'rooms': [{'room': '1413', 'api_version': 1, 'controller_metrics': {'id': 1, 'version': 0, 'uptime': 0, 'frames': 0, 'temperature': 0, 'init_temperature': 0, 'settings': '', 'error_color': {'R': 0, 'G': 0, 'B': 0}, 'timeout': 0, 'is_responding': True}, 'lamp_metrics': {1402: {'id': 1402, 'version': 0, 'uptime': 0, 'temperature': 0, 'init_temperature': 0, 'settings': '', 'error_color': {'R': 0, 'G': 0, 'B': 0}, 'timeout': 0}, 1401: {'id': 1401, 'version': 0, 'uptime': 0, 'temperature': 0, 'init_temperature': 0, 'settings': '', 'error_color': {'R': 0, 'G': 0, 'B': 0}, 'timeout': 0}}}, {'room': '1412', 'api_version': 1, 'controller_metrics': {'id': 0, 'version': 0, 'uptime': 0, 'frames': 0, 'temperature': 0, 'init_temperature': 0, 'settings': '', 'error_color': {'R': 0, 'G': 0, 'B': 0}, 'timeout': 0, 'is_responding': False}, 'lamp_metrics': {}}, {'room': '1411', 'api_version': 1, 'controller_metrics': {'id': 3, 'version': 0, 'uptime': 0, 'frames': 0, 'temperature': 0, 'init_temperature': 0, 'settings': '', 'error_color': {'R': 0, 'G': 0, 'B': 0}, 'timeout': 0, 'is_responding': True}, 'lamp_metrics': {1407: {'id': 1407, 'version': 0, 'uptime': 0, 'temperature': 0, 'init_temperature': 0, 'settings': '', 'error_color': {'R': 0, 'G': 0, 'B': 0}, 'timeout': 0}, 1408: {'id': 1408, 'version': 0, 'uptime': 0, 'temperature': 0, 'init_temperature': 0, 'settings': ''}}}}}}"
data_string2 = "{'REID': 2, 'RNUM': 200, 'RESPONSE': 'OK', 'PAYL': { 'metrics': None }}"
data_string3 = "{REID: 2, 'RNUM': 200, 'RESPONSE': 'OK'}"
data_string4 = "{'DATA': {val1: a, val2: {}, val3: [10, 12, 13e]}, 'ONLINE': TrUe}"
ps = NotQuiteJson()
result = ps.parseIter(exampledata.example)
rooms = []
for _ in range(14): rooms.append([])
for room in result["PAYL"]["rooms"]:
    level = int(re.sub('[^0-9]','', str(room["room"]))) // 100
    if room["apiversion"] > 1:
        print(level, room["room"])
        rooms[level-1].append(str(room["room"]) + str(room["controllermetrics"]["responding"]))
    else:
        print(level, room["room"])
        rooms[level-1].append(str(room["room"]) + str(room["controllermetrics"]["isresponding"]))


for i in range(len(rooms)):
    print(rooms[13-i])
    
print(result["PAYL"]["rooms"][32])"""