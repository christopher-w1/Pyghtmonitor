import yaml

class WindowMapper:
    def __init__(self) -> None:
        self.clients = {}
        self.controller_matrix = []
        for y in range(14):
            ls = []
            for x in range(28):
                ls.append("?")
            self.controller_matrix.append(ls)
    
    def read_yaml(self, yaml_file='laserconfig.yaml'):
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)

            clients = data.get('Clients', [])
            for client in clients:
                room = client["room"]
                self.clients[room] = client

            self.map_controllers()
            
            for line in self.controller_matrix:
                print(line)
            
    def map_controllers(self):
        for room in self.clients:
            client = self.clients[room]
            start_index = client["startIdx"]
            num_lamps   = client["numLamps"]
            indices     = [x + start_index for x in range(num_lamps)]
            #print(room, indices)
            for i in indices:
                x = i % 28
                y = i // 28
                self.controller_matrix[y][x] = room
        return self.controller_matrix
                
if __name__=="__main__":
    wm = WindowMapper()
    wm.read_yaml()