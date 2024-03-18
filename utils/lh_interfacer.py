from utils.wsconnector import WSConnector
from utils.notquitejson import NotQuiteJson
from time import sleep
import json
import re

class Interfacer:
    def __init__(self, username: str, token: str, address: str = "wss://lighthouse.uni-kiel.de/websocket",
                 ignore_ssl_cert=False):
        self.username = username
        self.token = token
        self.address = address
        self.connector = WSConnector(username, token, address, on_msg=print(),
                                     ignore_ssl_cert=ignore_ssl_cert)
        self.ph_thread = None
        self.parser = NotQuiteJson()
        self.connector.start()
        
    def update(self):
        self.connector.send("GET", "")
        self.json_string = self.connector.last_message
        
    def streamloop(self):
        while True:
            #print(response)
            print(" ")
            #self.json_to_file(response)
            rooms=self.get_rooms()
            if rooms: print(rooms.keys())
            sleep(2)
            
    def get_rooms(self, only_responding=True, api_version=None):
        response = self.get_parsed_data()
        if response:
            roomlist = response["PAYL"]["rooms"]
            roomdict = {}
            for entry in roomlist:
                if not api_version or int(entry["apiversion"]) == api_version:
                    if ((not only_responding) 
                        or int(entry["apiversion"]) == 1 and bool(entry["controllermetrics"]["isresponding"])
                        or int(entry["apiversion"]) == 2 and bool(entry["controllermetrics"]["responding"])):
                        roomdict[entry["room"]] = entry
                        roomdict[entry["room"]].pop("room")
            return roomdict
        
    def emulate(self):
        self.json_string = """
        {
        "rooms": [
            {
            "room": "1337",
            "api_version": 2,
            "controller_metrics": {
                "responding": true,
                "ping_latency_ms": 2.346,
                "firmware_version": 5,
                "uptime": 20,
                "frames": 0,
                "fps": 0,
                "core_temperature": 19.648264,
                "board_temperature": 23.75,
                "shunt_voltage": 0.00077,
                "voltage": 12.648001,
                "power": 0.970459,
                "current": 0.0769043
            },
            "lamp_metrics": [
                {
                "responding": true,
                "firmware_version": 5,
                "uptime": 21,
                "timeout": 10,
                "temperature": 12,
                "fuse_tripped": false,
                "flashing_status": "already up to date"
                }
            ]
            },
            {
            "room": "420",
            "api_version": 2,
            "controller_metrics": {
                "responding": false,
                "ping_latency_ms": null,
                "firmware_version": null,
                "uptime": null,
                "frames": null,
                "fps": null,
                "core_temperature": null,
                "board_temperature": null,
                "shunt_voltage": null,
                "voltage": null,
                "power": null,
                "current": null
            },
            "lamp_metrics": [
                {
                "responding": false,
                "firmware_version": null,
                "uptime": null,
                "timeout": null,
                "temperature": null,
                "fuse_tripped": null,
                "flashing_status": ""
                }
            ]
            }
        ]
        }"""
        
    def get_parsed_data(self):
        self.update()
        return self.parser.parseIter(self.json_string)
    
    def stop(self):
        self.connector.stop()
    
if __name__ == "__main__":
    name = "chris1234"
    token = "API-TOK_N/9u-eYpU-zTr0-bZDf-20s3"
    inf = Interfacer(name, token)
    inf.streamloop()